import pandas as pd
import json
import time
import logging
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright
from enums import PlaneType, SortOption
from models import FlightPassengers, FlightFilters
from utils import generate_search_url, clean_price, generate_booking_link, parse_flight_leg

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_flights(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: FlightPassengers = FlightPassengers(),
    plane_type: PlaneType = PlaneType.ECONOMY,
    sort_option: SortOption = SortOption.BEST_FLIGHT,
    filters: Optional[FlightFilters] = None,
    start_index: int = 0,
    end_index: int = 15
) -> Dict[str, Any]:
    """Scrape flight data from Kayak based on search parameters.

    Args:
        departure_airport: 3-letter IATA code (e.g., YYZ)
        arrival_airport: 3-letter IATA code (e.g., HKG)
        departure_date: ISO 8601 date (e.g., 2025-07-01)
        return_date: ISO 8601 date for return flight, None for one-way
        passengers: FlightPassengers object with adults, students, children
        plane_type: PlaneType enum (e.g., PlaneType.ECONOMY)
        sort_option: SortOption enum (e.g., SortOption.BEST_FLIGHT)
        filters: FlightFilters object for fs parameters
        start_index: Starting index of flight results to return (0-based, inclusive)
        end_index: Ending index of flight results to return (inclusive)

    Returns:
        Dictionary with flight data or error response if no flights found or errors occur
    """
    # Validate index parameters
    if not isinstance(start_index, int) or not isinstance(end_index, int):
        raise ValueError("start_index and end_index must be integers")
    if start_index < 0:
        raise ValueError("start_index cannot be negative")
    if end_index < start_index:
        raise ValueError("end_index must be greater than or equal to start_index")

    # Generate search URL
    search_url = generate_search_url(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_date=departure_date,
        return_date=return_date,
        passengers=passengers,
        plane_type=plane_type,
        sort_option=sort_option,
        filters=filters
    )
    logging.info(f"Generated search URL: {search_url}")

    # Prepare search parameters for response
    search_params = {
        "search_url": search_url,
        "departure_airport": departure_airport,
        "arrival_airport": arrival_airport,
        "departure_date": departure_date,
        "return_date": return_date,
        "passengers": passengers.to_dict(),
        "plane_type": plane_type.value,
        "sort_option": sort_option.value,
        "filters": filters.to_dict() if filters else None,
        "start_index": start_index,
        "end_index": end_index
    }

    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                java_script_enabled=True,
                bypass_csp=True,
            )
            page = context.new_page()

            # Retry navigation and loading
            attempts = 0
            max_attempts = 3
            while attempts < max_attempts:
                try:
                    logging.info(f"Attempt {attempts + 1}: Navigating to Kayak...")
                    page.goto(search_url, timeout=60000)
                    logging.info("Waiting for DOM content...")
                    page.wait_for_load_state("domcontentloaded", timeout=60000)
                    logging.info("Simulating user scroll...")
                    page.evaluate("window.scrollBy(0, 1000)")
                    break
                except Exception as e:
                    logging.error(f"Navigation error on attempt {attempts + 1}: {str(e)}")
                    page.screenshot(path=f"timeout_screenshot_attempt_{attempts + 1}.png")
                    with open(f"timeout_page_attempt_{attempts + 1}.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    attempts += 1
                    time.sleep(5)
            else:
                logging.error("Failed to load page after multiple attempts.")
                page.screenshot(path="timeout_screenshot_final.png")
                browser.close()
                error_response = {
                    "status": "no_flights_found",
                    "message": "Failed to load Kayak page after multiple attempts",
                    "total_results": 0,
                    "search_parameters": search_params
                }
                with open("flights_data.json", "w", encoding="utf-8") as f:
                    json.dump(error_response, f, indent=2)
                pd.DataFrame().to_csv("flights_data.csv", index=False)
                return error_response

            # Check for no-results message
            no_results_elem = page.query_selector("div[class*='no-results'], div:has-text('No flights found'), div:has-text('no results')")
            if no_results_elem:
                logging.warning(f"No flights found: {no_results_elem.inner_text()}")
                browser.close()
                error_response = {
                    "status": "no_flights_found",
                    "message": "No flights available for the specified parameters",
                    "total_results": 0,
                    "search_parameters": search_params
                }
                with open("flights_data.json", "w", encoding="utf-8") as f:
                    json.dump(error_response, f, indent=2)
                pd.DataFrame().to_csv("flights_data.csv", index=False)
                return error_response

            # Wait for flight results
            try:
                logging.info("Waiting for flight results...")
                page.wait_for_selector(".Fxw9-result-item-container", timeout=60000)
                logging.info("Flight results found!")
            except Exception as e:
                logging.error(f"Flight results container not found: {str(e)}")
                page.screenshot(path="no_results_screenshot.png")
                with open("no_results_page.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                browser.close()
                error_response = {
                    "status": "no_flights_found",
                    "message": f"Flight results container not found: {str(e)}",
                    "total_results": 0,
                    "search_parameters": search_params
                }
                with open("flights_data.json", "w", encoding="utf-8") as f:
                    json.dump(error_response, f, indent=2)
                pd.DataFrame().to_csv("flights_data.csv", index=False)
                return error_response

            # Extract flight data
            flight_data = []
            results_per_page = 15
            target_results = end_index + 1
            current_results = 0

            while current_results < target_results:
                result_items = page.query_selector_all(".Fxw9-result-item-container")
                current_results = len(result_items)
                logging.info(f"Found {current_results} result items.")

                # Check if we have enough results or no more to load
                show_more_button = page.query_selector("div.ULvh-button.show-more-button")
                if current_results >= target_results or not show_more_button:
                    break

                # Click "Show more" button
                try:
                    logging.info("Clicking 'Show more results' button...")
                    show_more_button.click()
                    # Wait for new results to load
                    page.wait_for_timeout(5000)
                    # Verify new results appeared
                    new_result_items = page.query_selector_all(".Fxw9-result-item-container")
                    if len(new_result_items) <= current_results:
                        logging.warning("No new results loaded after clicking 'Show more'.")
                        break
                    current_results = len(new_result_items)
                except Exception as e:
                    logging.warning(f"Failed to click 'Show more' button: {str(e)}")
                    page.screenshot(path="show_more_error_screenshot.png")
                    with open("show_more_error_page.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    break

            # Process all available results
            result_items = page.query_selector_all(".Fxw9-result-item-container")
            if not result_items:
                logging.warning("No flight result items found.")
                page.screenshot(path="no_results_screenshot.png")
                with open("no_results_page.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                browser.close()
                error_response = {
                    "status": "no_flights_found",
                    "message": "No flight results found for the specified parameters",
                    "total_results": 0,
                    "search_parameters": search_params
                }
                with open("flights_data.json", "w", encoding="utf-8") as f:
                    json.dump(error_response, f, indent=2)
                pd.DataFrame().to_csv("flights_data.csv", index=False)
                return error_response

            total_results = len(result_items)
            logging.info(f"Total available results: {total_results}")

            # Extract flight data
            for idx, item in enumerate(result_items):
                # Skip items outside the requested range
                if idx < start_index or idx > end_index:
                    continue
                logging.info(f"Processing item {idx}...")
                # Skip advertisements
                if not item.query_selector(".hJSA-list") or item.query_selector(".c_3eP-badge-content, .NAnQ-ad-badge"):
                    logging.info("Skipping advertisement block.")
                    continue

                # Extract flight details
                price_elem = item.query_selector(".e2GB-price-text")
                fare_types_elem = item.query_selector(".DOum-name")
                available_sites_elem = item.query_selector(".M_JD-num-sites-label")
                booking_link_elem = item.query_selector(".nrc6-price-section .M_JD-booking-btn a[role='link']")
                carry_on_elem = item.query_selector(".ac27-fee-box[aria-label*='carry-on bag'] .ac27-inner:last-child")
                checked_bags_elem = item.query_selector(".ac27-fee-box[aria-label*='checked bag'] .ac27-inner:last-child")

                # Extract flight legs
                outbound_leg = item.query_selector(".hJSA-list > li:nth-child(1)")
                return_leg = item.query_selector(".hJSA-list > li:nth-child(2)")
                outbound_flight = parse_flight_leg(outbound_leg)
                return_flight = parse_flight_leg(return_leg)

                # Extract metadata
                multiple_airlines_elem = item.query_selector("div:has-text('Multiple Airlines')")
                booking_button_elem = item.query_selector(".dOAU-booking-text")

                # Build structured JSON
                flight_data.append({
                    "flightDetails": {
                        "price": clean_price(price_elem.inner_text()) if price_elem else "N/A",
                        "fareTypes": fare_types_elem.inner_text().split(", ") if fare_types_elem else [],
                        "availableSites": int(available_sites_elem.inner_text().split()[0]) if available_sites_elem and available_sites_elem.inner_text().split()[0].isdigit() else 0,
                        "baggage": {
                            "carryOn": int(carry_on_elem.inner_text()) if carry_on_elem and carry_on_elem.inner_text().isdigit() else 0,
                            "checkedBags": int(checked_bags_elem.inner_text()) if checked_bags_elem and checked_bags_elem.inner_text().isdigit() else 0
                        },
                        "bookingLink": generate_booking_link(booking_link_elem.get_attribute("href")) if booking_link_elem else "https://www.ca.kayak.com"
                    },
                    "outboundFlight": outbound_flight,
                    "returnFlight": return_flight,
                    "metadata": {
                        "multipleAirlines": bool(multiple_airlines_elem),
                        "bookingButtonText": booking_button_elem.inner_text() if booking_button_elem else "N/A"
                    }
                })

            browser.close()

            # Check if requested range was fully satisfied
            message = None
            if total_results < target_results:
                message = f"Requested up to index {end_index}, but only {total_results} results available."

            # Save to JSON
            success_response = {
                "status": "success",
                "flights": flight_data,
                "total_results": total_results,
                "message": message,
                "search_parameters": search_params
            }
            with open("flights_data.json", "w", encoding="utf-8") as f:
                json.dump(success_response, f, indent=2)
            logging.info("Data saved to flights_data.json")

            # Save to CSV
            csv_data = []
            for flight in flight_data:
                csv_data.append({
                    "price": flight["flightDetails"]["price"],
                    "fareTypes": ", ".join(flight["flightDetails"]["fareTypes"]),
                    "availableSites": flight["flightDetails"]["availableSites"],
                    "carryOn": flight["flightDetails"]["baggage"]["carryOn"],
                    "checkedBags": flight["flightDetails"]["baggage"]["checkedBags"],
                    "outbound_departureTime": flight["outboundFlight"].get("departureTime", "N/A"),
                    "outbound_duration": flight["outboundFlight"].get("duration", "N/A"),
                    "return_departureTime": flight["returnFlight"].get("departureTime", "N/A"),
                    "return_duration": flight["returnFlight"].get("duration", "N/A")
                })
            df = pd.DataFrame(csv_data)
            df.to_csv("flights_data.csv", index=False)
            logging.info("Data saved to flights_data.csv")

            return success_response

    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")
        error_response = {
            "status": "no_flights_found",
            "message": f"Error occurred: {str(e)}",
            "total_results": 0,
            "search_parameters": search_params
        }
        with open("flights_data.json", "w", encoding="utf-8") as f:
            json.dump(error_response, f, indent=2)
        pd.DataFrame().to_csv("flights_data.csv", index=False)
        return error_response

if __name__ == "__main__":
    # Example usage
    passengers = FlightPassengers(
        adults=2,
        students=0,
        children=[]
    )
    filters = FlightFilters(
        carry_on_free=1,
        max_price=6000,
    )
    result = scrape_flights(
        departure_airport="YYZ",
        arrival_airport="HKG",
        departure_date="2025-07-01",
        return_date="2025-07-25",
        passengers=passengers,
        plane_type=PlaneType.ECONOMY,
        sort_option=SortOption.CHEAPEST,
        filters=filters,
        start_index=60,
        end_index=75
    )
    logging.info(f"Scraping result: {result.get('status', 'unknown')}, {len(result.get('flights', []))} flights found.")