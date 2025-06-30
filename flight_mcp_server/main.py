import re
import asyncio
from typing import Optional, List, Set
from mcp.server.fastmcp import FastMCP
from scrapper import scrape_flights
from enums import PlaneType, SortOption, ChildType, Alliance
from models import FlightPassengers, FlightFilters
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

mcp = FastMCP("flight-mcp-server")

@mcp.tool()
async def scrape_flights_tool(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 2,
    students: int = 0,
    children: List[str] = [],
    plane_type: str = "economy",
    sort_option: str = "price_a",
    carry_on_free: Optional[int] = 1,
    checked_bags_free: Optional[int] = None,
    stops: Optional[int] = None,
    max_price: Optional[int] = 6000,
    alliance: Optional[str] = None,
    include_airlines: Optional[Set[str]] = None,
    exclude_airlines: Optional[Set[str]] = None,
    wifi_only: bool = False,
    start_index: int = 0,
    end_index: int = 15
) -> str:
    """Scrape flight data from Kayak with pagination support. You can ask the user whether it is a one-way or round-trip flight, if they only give you the departure date, then it is a one-way flight, if they give you the departure date and return date, then it is a round-trip flight.
    You can also ask the user what is their sort option, if they don't give you the sort option, then you can use the default sort option.
    You can also ask the user what is their plane type, if they don't give you the plane type, then you can use the default plane type.
    You can also ask the user what is their alliance, if they don't give you the alliance, then you can use the default alliance.
    You can also ask the user what is their include airlines, if they don't give you the include airlines, then you can use the default include airlines.
    You can also ask the user what is their exclude airlines, if they don't give you the exclude airlines, then you can use the default exclude airlines.
    You can also ask the user what is their wifi only, if they don't give you the wifi only, then you can use the default wifi only.
    You can also ask the user what is their start index, if they don't give you the start index, then you can use the default start index.

    Args:
        departure_airport: 3-letter IATA code for departure airport (e.g., "YYZ" for Toronto).
        arrival_airport: 3-letter IATA code for arrival airport (e.g., "HKG" for Hong Kong).
        departure_date: Departure date in ISO 8601 format (YYYY-MM-DD, e.g., "2025-07-01").
        return_date: Return date in ISO 8601 format (YYYY-MM-DD, e.g., "2025-07-25"). None for one-way flights.
        adults: Number of adult passengers (age 12+). Default: 2.
        students: Number of student passengers (age 12+ with student fare eligibility). Default: 0.
        children: List of child passenger types: "11" (age 2-11), "1S" (toddler under 2 with seat), "1L" (infant under 2 on lap). Default: [].
        plane_type: Cabin class: "economy", "premium", "business", or "first". Default: "economy".
        sort_option: Sort order for results: "bestflight_a" (best flights), "price_a" (cheapest), "price_b" (most expensive), "duration_a" (quickest), "duration_b" (slowest), "depart_a" (earliest takeoff), "depart_b" (latest takeoff), "arrive_a" (earliest landing), "arrive_b" (latest landing), "departReturn_a" (earliest return takeoff), "departReturn_b" (latest return takeoff), "arriveReturn_a" (earliest return landing), "arriveReturn_b" (latest return landing). Default: "price_a".
        carry_on_free: Minimum number of free carry-on bags. None for no preference. Default: 1.
        checked_bags_free: Minimum number of free checked bags. None for no preference. Default: None.
        stops: Maximum number of stops (0 for direct flights). None for no preference. Default: None.
        max_price: Maximum price in CAD. None for no price limit. Default: 6000.
        alliance: Airline alliance: "VALUE_ALLIANCE", "ONE_WORLD", "SKY_TEAM", "STAR_ALLIANCE". None for no preference. Default: None.
        include_airlines: Set of 2-letter IATA airline codes to include (e.g., {"AC", "UA"}). None for no inclusion filter. Default: None.
        exclude_airlines: Set of 2-letter IATA airline codes to exclude (e.g., {"NK", "F9"}). None for no exclusion filter. Default: None.
        wifi_only: If true, only include flights with Wi-Fi available. Default: False.
        start_index: Starting index of flight results to return (0-based, inclusive). Default: 0.
        end_index: Ending index of flight results to return (inclusive). Must be >= start_index. Default: 15.

    Returns:
        A string summarizing flight results, with each flight separated by "---". Includes price, outbound/return times, airlines, airports, stops, and stop details. If no flights are found or an error occurs, returns an error message with total results count.
    """

        # Validate inputs
    current_year = datetime.now().year  # Current year as of June 27, 2025

    # Validate and adjust departure_date
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", departure_date):
        return "Invalid departure date format: Must be YYYY-MM-DD."
    try:
        dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        if dep_date.year < current_year:
            departure_date = f"{current_year}-{dep_date.strftime('%m-%d')}"
            logger.info(f"Adjusted departure_date from {dep_date.year} to {current_year}: {departure_date}")
    except ValueError:
        return "Invalid departure date: Unable to parse date."

    # Validate and adjust return_date if provided
    if return_date:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", return_date):
            return "Invalid return date format: Must be YYYY-MM-DD."
        try:
            ret_date = datetime.strptime(return_date, "%Y-%m-%d")
            if ret_date.year < current_year:
                return_date = f"{current_year}-{ret_date.strftime('%m-%d')}"
                logger.info(f"Adjusted return_date from {ret_date.year} to {current_year}: {return_date}")
        except ValueError:
            return "Invalid return date: Unable to parse date."
    

    # Validate inputs
    if not re.match(r"^[A-Z]{3}$", departure_airport):
        return "Invalid departure airport code: Must be a 3-letter IATA code."
    if not re.match(r"^[A-Z]{3}$", arrival_airport):
        return "Invalid arrival airport code: Must be a 3-letter IATA code."
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", departure_date):
        return "Invalid departure date format: Must be YYYY-MM-DD."
    if return_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", return_date):
        return "Invalid return date format: Must be YYYY-MM-DD."
    if adults < 0 or students < 0:
        return "Adults and students cannot be negative."
    if adults == 0 and students == 0 and not children:
        return "At least one passenger is required."
    valid_child_types = {e.value for e in ChildType}
    if children and not all(c in valid_child_types for c in children):
        return "Invalid child type. Must be '11', '1S', or '1L'."
    valid_plane_types = {e.value for e in PlaneType}
    if plane_type not in valid_plane_types:
        return f"Invalid plane_type. Must be one of: {', '.join(valid_plane_types)}."
    valid_sort_options = {e.value for e in SortOption}
    if sort_option not in valid_sort_options:
        return f"Invalid sort_option. Must be one of: {', '.join(valid_sort_options)}."
    valid_alliances = {e.value for e in Alliance}
    if alliance and alliance not in valid_alliances:
        return f"Invalid alliance. Must be one of: {', '.join(valid_alliances)}."
    if include_airlines and not all(re.match(r"^[A-Z0-9]{2}$", code) for code in include_airlines):
        return "Invalid include_airlines: All codes must be 2-character IATA codes."
    if exclude_airlines and not all(re.match(r"^[A-Z0-9]{2}$", code) for code in exclude_airlines):
        return "Invalid exclude_airlines: All codes must be 2-character IATA codes."
    if carry_on_free is not None and carry_on_free < 0:
        return "carry_on_free cannot be negative."
    if checked_bags_free is not None and checked_bags_free < 0:
        return "checked_bags_free cannot be negative."
    if stops is not None and stops < 0:
        return "stops cannot be negative."
    if max_price is not None and max_price <= 0:
        return "max_price must be positive."
    if not isinstance(start_index, int) or start_index < 0:
        return "start_index must be a non-negative integer."
    if not isinstance(end_index, int) or end_index < start_index:
        return "end_index must be an integer greater than or equal to start_index."

    # Convert inputs to scrapper.py types
    try:
        passengers = FlightPassengers(
            adults=adults,
            students=students,
            children=[ChildType(c) for c in children]
        )
        filters = FlightFilters(
            carry_on_free=carry_on_free,
            checked_bags_free=checked_bags_free,
            stops=stops,
            max_price=max_price,
            alliance=Alliance(alliance) if alliance else None,
            include_airlines=include_airlines,
            exclude_airlines=exclude_airlines,
            wifi_only=wifi_only
        )
    except Exception as e:
        return f"Error creating passenger or filter objects: {str(e)}"

    # Run sync scrape_flights in async context
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: scrape_flights(
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                departure_date=departure_date,
                return_date=return_date,
                passengers=passengers,
                plane_type=PlaneType(plane_type),
                sort_option=SortOption(sort_option),
                filters=filters,
                start_index=start_index,
                end_index=end_index
            )
        )
    except Exception as e:
        logger.error(f"Error running scrape_flights: {str(e)}")
        return f"Error fetching flight data: {str(e)}"

    # Format output
    if not isinstance(result, dict) or result.get("status") == "no_flights_found":
        message = result.get("message", "No flight results found") if isinstance(result, dict) else "Invalid response format"
        total_results = result.get("total_results", 0) if isinstance(result, dict) else 0
        return f"No flights found: {message}\nTotal results: {total_results}"

    flights = result.get("flights", [])
    total_results = result.get("total_results", 0)
    message = result.get("message", "")
    output = []

    for flight in flights:
        details = flight.get("flightDetails", {})
        outbound = flight.get("outboundFlight", {})
        return_flight = flight.get("returnFlight", {})

        # Skip if critical data is missing
        if not details or not outbound:
            logger.warning(f"Skipping flight with missing details or outbound data: {flight}")
            continue

        # Build flight details
        flight_lines = [
            "Flight:",
            f"Price: {details.get('price', 'N/A')}",
            f"Fare Types: {', '.join(details.get('fareTypes', [])) or 'N/A'}",
            f"Available Booking Sites: {details.get('availableSites', 0)}",
            f"Baggage: {details.get('baggage', {}).get('carryOn', 0)} carry-on, {details.get('baggage', {}).get('checkedBags', 0)} checked",
            "Outbound:",
            f"  Departure: {outbound.get('departureTime', 'N/A')} from {outbound.get('departureAirport', {}).get('code', 'N/A')} ({outbound.get('departureAirport', {}).get('name', 'Unknown')})",
            f"  Arrival: {outbound.get('arrivalTime', 'N/A')} at {outbound.get('arrivalAirport', {}).get('code', 'N/A')} ({outbound.get('arrivalAirport', {}).get('name', 'Unknown')})",
            f"  Duration: {outbound.get('duration', 'N/A')}",
            f"  Airlines: {', '.join(outbound.get('airlines', ['N/A']))}",
            f"  Stops: {outbound.get('stops', 0)}",
        ]

        # Add outbound stop details if available
        if outbound.get('stops', 0) > 0 and outbound.get('stopDetails'):
            for i, stop in enumerate(outbound.get('stopDetails', []), 1):
                flight_lines.append(
                    f"    Stop {i}: {stop.get('airportCode', 'N/A')} ({stop.get('airportName', 'Unknown')}), Layover: {stop.get('layoverDuration', 'N/A')}"
                )

        # Add return flight if valid and round-trip is requested
        if return_date and return_flight and return_flight.get("departureTime", "N/A") != "N/A" and return_flight.get("arrivalTime", "N/A") != "N/A":
            flight_lines.extend([
                "Return:",
                f"  Departure: {return_flight.get('departureTime', 'N/A')} from {return_flight.get('departureAirport', {}).get('code', 'N/A')} ({return_flight.get('departureAirport', {}).get('name', 'Unknown')})",
                f"  Arrival: {return_flight.get('arrivalTime', 'N/A')} at {return_flight.get('arrivalAirport', {}).get('code', 'N/A')} ({return_flight.get('arrivalAirport', {}).get('name', 'Unknown')})",
                f"  Duration: {return_flight.get('duration', 'N/A')}",
                f"  Airlines: {', '.join(return_flight.get('airlines', ['N/A']))}",
                f"  Stops: {return_flight.get('stops', 0)}",
            ])

            # Add return stop details if available
            if return_flight.get('stops', 0) > 0 and return_flight.get('stopDetails'):
                for i, stop in enumerate(return_flight.get('stopDetails', []), 1):
                    flight_lines.append(
                        f"    Stop {i}: {stop.get('airportCode', 'N/A')} ({stop.get('airportName', 'Unknown')}), Layover: {stop.get('layoverDuration', 'N/A')}"
                    )

        # Add booking link
        flight_lines.append(f"Booking Link: {details.get('bookingLink', 'N/A')}")

        # Join lines to create flight string
        flight_str = "\n".join(flight_lines)
        output.append(flight_str)

    if not output:
        return f"No valid flights found in the requested range.\nTotal results: {total_results}"

    output_str = "\n---\n".join(output)
    if message:
        output_str += f"\nNote: {message}"
    output_str += f"\nTotal results available: {total_results}"
    return output_str


if __name__ == "__main__":
    logger.info("Starting Flight MCP server...")
    mcp.run(transport='stdio')
    logger.info("Flight MCP server stopped.")