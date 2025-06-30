import re
import logging
from typing import Optional
from enums import PlaneType, SortOption
from models import FlightPassengers, FlightFilters
from config import BASE_URL, BASE_SEARCH_URL

def generate_search_url(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: FlightPassengers = FlightPassengers(),
    plane_type: PlaneType = PlaneType.ECONOMY,
    sort_option: SortOption = SortOption.BEST_FLIGHT,
    filters: Optional[FlightFilters] = None
) -> str:
    """Generate a Kayak search URL based on input parameters.

    Args:
        departure_airport: 3-letter IATA code (e.g., YYZ)
        arrival_airport: 3-letter IATA code (e.g., HKG)
        departure_date: ISO 8601 date (e.g., 2025-07-01)
        return_date: ISO 8601 date for return flight, None for one-way
        passengers: FlightPassengers object with adults, students, children
        plane_type: PlaneType enum (e.g., PlaneType.ECONOMY)
        sort_option: SortOption enum (e.g., SortOption.BEST_FLIGHT)
        filters: FlightFilters object for fs parameters

    Returns:
        Full search URL as a string

    Raises:
        ValueError: If inputs are invalid (e.g., invalid airport codes, dates)
    """
    # Validate airports
    if not re.match(r"^[A-Z]{3}$", departure_airport):
        raise ValueError(f"Invalid departure airport code: {departure_airport}")
    if not re.match(r"^[A-Z]{3}$", arrival_airport):
        raise ValueError(f"Invalid arrival airport code: {arrival_airport}")

    # Validate dates
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, departure_date):
        raise ValueError(f"Invalid departure date format: {departure_date}")
    if return_date and not re.match(date_pattern, return_date):
        raise ValueError(f"Invalid return date format: {return_date}")

    # Construct URL path
    path_parts = [f"{departure_airport}-{arrival_airport}", departure_date]
    if return_date:
        path_parts.append(return_date)
    path_parts.append(passengers.to_url_string())
    path_parts.append(plane_type.value)
    path = "/".join(path_parts)

    # Construct query parameters
    query_parts = [f"sort={sort_option.value}"]
    if filters and filters.to_url_string():
        query_parts.append(f"fs={filters.to_url_string()}")

    # Build full URL
    base_url = BASE_SEARCH_URL
    query_string = "&".join(query_parts)
    return f"{base_url}/{path}?{query_string}"

def clean_price(price_str):
    """Clean price string by replacing Unicode escape characters."""
    if not price_str:
        return "N/A"
    cleaned = price_str.replace("\u00a0", " ")
    return cleaned

def generate_booking_link(suffix_url):
    """Construct full booking URL."""
    return BASE_URL + suffix_url

def parse_flight_leg(flight_leg_elem):
    """Parse a single flight leg (outbound or return) and return structured data."""
    if not flight_leg_elem:
        logging.warning("No leg element found.")
        return {}

    # Extract times
    times = flight_leg_elem.query_selector_all(".VY2U .vmXl span")
    departure_time = times[0].inner_text() if len(times) > 0 else "N/A"
    arrival_time = times[2].inner_text() if len(times) > 2 else "N/A"

    # Extract airports
    efvi_elem = flight_leg_elem.query_selector(".EFvI")
    if not efvi_elem:
        logging.warning("No .EFvI element found in leg.")
        return {
            "departureTime": departure_time,
            "departureAirport": {"code": "N/A", "name": "N/A"},
            "arrivalTime": arrival_time,
            "arrivalAirport": {"code": "N/A", "name": "N/A"},
            "duration": "N/A",
            "airlines": ["N/A"],
            "stops": 0,
            "stopDetails": [],
            "nextDayArrival": False
        }

    # Get all airport info elements
    airport_info_elems = efvi_elem.query_selector_all(".jLhY-airport-info")
    if len(airport_info_elems) != 2:
        logging.warning(f"Expected 2 airport info elements, found {len(airport_info_elems)}: {efvi_elem.inner_text()}")
        departure_airport = {"code": "N/A", "name": "N/A"}
        arrival_airport = {"code": "N/A", "name": "N/A"}
    else:
        # Departure airport
        dep_spans = airport_info_elems[0].query_selector_all("span")
        departure_airport = {
            "code": dep_spans[0].inner_text() if len(dep_spans) > 0 else "N/A",
            "name": dep_spans[1].inner_text() if len(dep_spans) > 1 else "N/A"
        }
        # Arrival airport
        arr_spans = airport_info_elems[1].query_selector_all("span")
        arrival_airport = {
            "code": arr_spans[0].inner_text() if len(arr_spans) > 0 else "N/A",
            "name": arr_spans[1].inner_text() if len(arr_spans) > 1 else "N/A"
        }

        # Validate airports
        if departure_airport["code"] == arrival_airport["code"]:
            logging.warning(f"Same departure and arrival airport detected: {departure_airport['code']} - {efvi_elem.inner_text()}")

    # Extract duration
    duration_elem = flight_leg_elem.query_selector(".xdW8 .vmXl")
    duration = duration_elem.inner_text() if duration_elem else "N/A"

    # Extract airlines
    airlines = [img.get_attribute("alt") for img in flight_leg_elem.query_selector_all(".c5iUd-leg-carrier img")]
    airlines = airlines if airlines else ["N/A"]

    # Extract stops
    stops_elem = flight_leg_elem.query_selector(".JWEO-stops-text")
    stops = 0
    if stops_elem and stops_elem.inner_text().split()[0].isdigit():
        stops = int(stops_elem.inner_text().split()[0])
    elif stops_elem and stops_elem.inner_text().lower() == "direct":
        stops = 0
    else:
        logging.warning("Unrecognized stops text: %s", stops_elem.inner_text() if stops_elem else "None")

    # Extract stop details
    stop_details = []
    if stops > 0:
        # Target top-level spans containing stop data
        stop_elements = flight_leg_elem.query_selector_all(".JWEO .c_cgF-mod-variant-full-airport > span")
        for stop_elem in stop_elements:
            # Get the inner span containing the airport code
            code_elem = stop_elem.query_selector("span")
            if not code_elem:
                logging.warning("No code element found in stop: %s", stop_elem.inner_text())
                continue
            airport_code = code_elem.inner_text()[:3]
            if not re.match(r"^[A-Z]{3}$", airport_code):
                logging.warning("Invalid airport code in stop: %s", airport_code)
                continue
            # Skip if code matches departure or arrival airport
            if airport_code in [departure_airport["code"], arrival_airport["code"]]:
                logging.info(f"Skipping airport code {airport_code} as it matches departure or arrival.")
                continue
            # Get hEI8 span for layover details
            hEI8_elem = stop_elem.query_selector(".hEI8")
            if not hEI8_elem:
                logging.warning("No hEI8 element found in stop: %s", stop_elem.inner_text())
                continue
            stop_text = hEI8_elem.inner_text()
            # Extract airport name from AFFP span
            airport_name_elem = hEI8_elem.query_selector(".AFFP")
            airport_name = airport_name_elem.inner_text() if airport_name_elem else "N/A"
            # Extract layover duration
            layover_match = re.search(r"(\d+h \d+m) layover", stop_text)
            layover_duration = layover_match.group(1) if layover_match else "N/A"
            stop_details.append({
                "airportCode": airport_code,
                "airportName": airport_name,
                "layoverDuration": layover_duration
            })
        # Deduplicate stops
        seen = set()
        stop_details = [d for d in stop_details if not (d["airportCode"] in seen or seen.add(d["airportCode"]))]
        # Validate number of stops
        if len(stop_details) != stops:
            logging.warning(f"Expected {stops} stops, but found {len(stop_details)} in stopDetails: {stop_details}")

    # Check for next day arrival
    next_day_elem = flight_leg_elem.query_selector(".VY2U-adendum")
    next_day_arrival = bool(next_day_elem)

    return {
        "departureTime": departure_time,
        "departureAirport": departure_airport,
        "arrivalTime": arrival_time,
        "arrivalAirport": arrival_airport,
        "duration": duration,
        "airlines": airlines,
        "stops": stops,
        "stopDetails": stop_details,
        "nextDayArrival": next_day_arrival
    }