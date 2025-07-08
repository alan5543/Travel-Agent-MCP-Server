from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from apiService import get_hotel_list, get_hotel_details, get_events, get_places, get_current_currency_rates, get_current_date
from enumType import SortBy, Rating, HotelClass, PropertyType, Amenity
import os
from dotenv import load_dotenv
import logging
import datetime
import re

# Set up logging
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("serp-mcp-server")

load_dotenv()

# Get API key from environment
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY not found in .env file")

CURRENCYFREAKS_API_KEY = os.getenv("CURRENCYFREAKS_API_KEY")
if not CURRENCYFREAKS_API_KEY:
    raise ValueError("CURRENCYFREAKS_API_KEY not found in .env file")


@mcp.tool()
async def search_hotels(
    query: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    currency: str = "USD",
    gl: str = "us",
    hl: str = "en",
    sort_by: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_types: Optional[List[str]] = None,
    amenities: Optional[List[str]] = None,
    rating: Optional[str] = None,
    hotel_class: Optional[List[str]] = None,
    free_cancellation: Optional[bool] = None,
    special_offers: Optional[bool] = None,
    eco_certified: Optional[bool] = None,
    vacation_rentals: Optional[bool] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    children: Optional[int] = None,
    children_ages: Optional[List[int]] = None,
    next_page_token: Optional[str] = None
) -> Dict:
    """
    Search for hotels or vacation rentals in a specified location using the SerpApi Google Hotels API.

    This tool retrieves a list of hotels or vacation rentals based on the provided search parameters.
    It returns a JSON object containing a list of properties and pagination details.
    Use the `property_token` from the response to fetch detailed information about a specific property
    using the `find_hotel_detail` tool.

    Args:
        query (str): The search query for the location (e.g., "Hong Kong"). Required.
        check_in_date (str): Check-in date in YYYY-MM-DD format (e.g., "2025-06-27"). Required.
        check_out_date (str): Check-out date in YYYY-MM-DD format (e.g., "2025-06-28"). Required.
        adults (int, optional): Number of adults. Defaults to 2.
        currency (str, optional): Currency code for prices (e.g., "USD", "EUR"). Defaults to "USD".
        gl (str, optional): Country code for localization (e.g., "us", "uk"). Defaults to "us".
        hl (str, optional): Language code for results (e.g., "en", "fr"). Defaults to "en".
        sort_by (str, optional): Sorting option for results. Options: "LOWEST_PRICE", "HIGHEST_RATING", "MOST_REVIEWED".
        min_price (float, optional): Minimum price per night.
        max_price (float, optional): Maximum price per night.
        property_types (List[str], optional): Types of properties to filter. Options: "BEACH_HOTELS", "BOUTIQUE_HOTELS",
            "HOSTELS", "INNS", "MOTELS", "RESORTS", "SPA_HOTELS", "BED_AND_BREAKFASTS", "OTHER",
            "APARTMENT_HOTELS", "MINSHUKU", "JAPANESE_STYLE_BUSINESS_HOTELS", "RYOKAN".
        amenities (List[str], optional): Amenities to filter. Options: "FREE_PARKING", "PARKING", "INDOOR_POOL",
            "OUTDOOR_POOL", "POOL", "FITNESS_CENTER", "RESTAURANT", "FREE_BREAKFAST", "SPA", "BEACH_ACCESS",
            "CHILD_FRIENDLY", "BAR", "PET_FRIENDLY", "ROOM_SERVICE", "FREE_WIFI", "AIR_CONDITIONED",
            "ALL_INCLUSIVE_AVAILABLE", "WHEELCHAIR_ACCESSIBLE", "EV_CHARGER".
        rating (str, optional): Minimum rating filter. Options: "THREE_POINT_FIVE_PLUS", "FOUR_PLUS", "FOUR_POINT_FIVE_PLUS".
        hotel_class (List[str], optional): Hotel star ratings to filter. Options: "TWO_STAR", "THREE_STAR", "FOUR_STAR", "FIVE_STAR".
        free_cancellation (bool, optional): Filter for properties offering free cancellation.
        special_offers (bool, optional): Filter for properties with special offers.
        eco_certified (bool, optional): Filter for eco-certified properties.
        vacation_rentals (bool, optional): If True, search for vacation rentals instead of hotels.
        bedrooms (int, optional): Minimum number of bedrooms for vacation rentals.
        bathrooms (int, optional): Minimum number of bathrooms for vacation rentals.
        children (int, optional): Number of children.
        children_ages (List[int], optional): Ages of children (1 to 17). Must match the number of children.
        next_page_token (str, optional): Token for retrieving the next page of results.

    Returns:
        A JSON object with the following structure:
        {
            "properties": [
                {
                    "type": str,  // e.g., "hotel" or "vacation rental"
                    "name": str,  // e.g., "Hong Kong SkyCity Marriott Hotel"
                    "description": str,  // Brief description
                    "link": str,  // URL to property's website
                    "gps_coordinates": {"latitude": float, "longitude": float},
                    "rate_per_night": {
                        "lowest": str,  // e.g., "$173"
                        "extracted_lowest": float  // e.g., 173
                    },
                    "hotel_class": str,  // e.g., "5-star hotel"
                    "overall_rating": float,  // e.g., 4.3
                    "reviews": int,  // e.g., 4201
                    "amenities": [str],  // e.g., ["Free Wi-Fi", "Indoor pool"]
                    "property_token": str  // Token for find_hotel_detail
                }
            ],
            "serpapi_pagination": {
                "current_from": int,  // e.g., 1
                "current_to": int,  // e.g., 18
                "next_page_token": str  // Token for next page
            }
        }
        If the request fails, returns: {"error": str}  // e.g., "API request failed: <reason>"

    Raises:
        ValueError: If check_in_date or check_out_date is not in YYYY-MM-DD format, or if children_ages length does not match children count.
    """

    # Validate dates
    current_year = datetime.now().year
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", check_in_date):
        return {"error": "Invalid check-in date format: Must be YYYY-MM-DD."}
    try:
        cin_date = datetime.strptime(check_in_date, "%Y-%m-%d")
        if cin_date.year < current_year:
            check_in_date = f"{current_year}-{cin_date.strftime('%m-%d')}"
            logger.info(f"Adjusted check_in_date from {cin_date.year} to {current_year}: {check_in_date}")
    except ValueError:
        return {"error": "Invalid check-in date: Unable to parse date."}
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", check_out_date):
        return {"error": "Invalid check-out date format: Must be YYYY-MM-DD."}
    try:
        cout_date = datetime.strptime(check_out_date, "%Y-%m-%d")
        if cout_date.year < current_year:
            check_out_date = f"{current_year}-{cout_date.strftime('%m-%d')}"
            logger.info(f"Adjusted check_out_date from {cout_date.year} to {current_year}: {check_out_date}")
    except ValueError:
        return {"error": "Invalid check-out date: Unable to parse date."}

    # Map string inputs to Enum values
    sort_by_enum = SortBy[sort_by] if sort_by else None
    rating_enum = Rating[rating] if rating else None
    hotel_class_enum = [HotelClass[hc] for hc in hotel_class] if hotel_class else None
    property_types_enum = [PropertyType[pt] for pt in property_types] if property_types else None
    amenities_enum = [Amenity[a] for a in amenities] if amenities else None

    try:
        result = get_hotel_list(
            query=query,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            currency=currency,
            gl=gl,
            hl=hl,
            sort_by=sort_by_enum,
            min_price=min_price,
            max_price=max_price,
            property_types=property_types_enum,
            amenities=amenities_enum,
            rating=rating_enum,
            hotel_class=hotel_class_enum,
            free_cancellation=free_cancellation,
            special_offers=special_offers,
            eco_certified=eco_certified,
            vacation_rentals=vacation_rentals,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            children=children,
            children_ages=children_ages,
            next_page_token=next_page_token,
            api_key=SERPAPI_KEY
        )
        return result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def find_hotel_detail(
    query: str,
    property_token: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    currency: str = "USD",
    gl: str = "us",
    hl: str = "en",
    children: Optional[int] = None,
    children_ages: Optional[List[int]] = None
) -> Dict:
    """
    Retrieve detailed information for a specific hotel or vacation rental using the SerpApi Google Hotels API.

    This tool fetches detailed information about a property identified by its `property_token`, which is obtained
    from the `search_hotels` tool. The response includes the property's name, address, phone number, prices,
    amenities, nearby places, ratings, and images.

    Args:
        query (str): The search query used in the original search (e.g., "Hong Kong"). Required.
        property_token (str): Unique token identifying the property (from `search_hotels` response). Required.
        check_in_date (str): Check-in date in YYYY-MM-DD format (e.g., "2025-06-27"). Required.
        check_out_date (str): Check-out date in YYYY-MM-DD format (e.g., "2025-06-28"). Required.
        adults (int, optional): Number of adults. Defaults to 2.
        currency (str, optional): Currency code for prices (e.g., "USD", "EUR"). Defaults to "USD".
        gl (str, optional): Country code for localization (e.g., "us", "uk"). Defaults to "us".
        hl (str, optional): Language code for results (e.g., "en", "fr"). Defaults to "en".
        children (int, optional): Number of children. Defaults to None.
        children_ages (List[int], optional): Ages of children (1 to 17). Must match the number of children.

    Returns:
        A JSON object with the following structure:
        {
            "search_metadata": {
                "status": str,  // e.g., "Success"
                "created_at": str  // e.g., "2025-06-26 19:52:23 UTC"
            },
            "search_parameters": {
                "q": str,  // e.g., "Hong Kong"
                "check_in_date": str,  // e.g., "2025-06-27"
                "check_out_date": str,  // e.g., "2025-06-28"
                "adults": int,  // e.g., 2
                "children": int  // e.g., 2 (optional)
            },
            "hotel": {
                "name": str,  // e.g., "Regal Airport Hotel Hong Kong"
                "description": str,  // Brief description
                "link": str,  // URL to property's website
                "address": str,  // e.g., "9 Cheong Tat Road, Hong Kong International Airport Chek Lap Kok, Lantau Island, Hong Kong"
                "phone": str,  // e.g., "+852 2286 8888"
                "gps_coordinates": {"latitude": float, "longitude": float},  // e.g., {"latitude": 22.3186949, "longitude": 113.9343274}
                "check_in_time": str,  // e.g., "2:00 PM"
                "check_out_time": str,  // e.g., "12:00 PM"
                "rates": {
                    "lowest": str,  // e.g., "US$190"
                    "before_taxes": str  // e.g., "US$174"
                },
                "deal": str,  // e.g., "41% less than usual" (optional)
                "hotel_class": str,  // e.g., "5-star hotel"
                "overall_rating": float,  // e.g., 4.0
                "reviews": int,  // e.g., 5681
                "images": [{"thumbnail": str}],  // List of image URLs
                "amenities": [str]  // e.g., ["6 restaurants", "Spa", "Gym", "Indoor/outdoor pools"]
            },
            "prices": {
                "sources": [
                    {
                        "source": str,  // e.g., "klook"
                        "rate": str  // e.g., "US$190"
                    }
                ]
            },
            "nearby_places": {
                "points_of_interest": [
                    {
                        "name": str,  // e.g., "Hong Kong Disneyland"
                        "distance": str,  // e.g., "18 km"
                        "rating": float  // e.g., 4.5
                    }
                ],
                "restaurants": [
                    {
                        "name": str,  // e.g., "Rouge 紅軒"
                        "type": str,  // e.g., "Cantonese"
                        "rating": float  // e.g., 4.0
                    }
                ]
            },
            "reviews_summary": {
                "total": int,  // e.g., 5681
                "breakdown": {
                    "5_star": int,  // e.g., 2401
                    "4_star": int  // e.g., 1749
                },
                "top_categories": [
                    {
                        "name": str,  // e.g., "Location"
                        "rating": float  // e.g., 4.0
                    }
                ]
            }
        }
        If the request fails, returns: {"error": str}  // e.g., "API request failed: <reason>"

    Raises:
        ValueError: If check_in_date or check_out_date is not in YYYY-MM-DD format, or if children_ages length does not match children count.
    """
    # Validate dates
    current_year = datetime.now().year
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", check_in_date):
        return {"error": "Invalid check-in date format: Must be YYYY-MM-DD."}
    try:
        cin_date = datetime.strptime(check_in_date, "%Y-%m-%d")
        if cin_date.year < current_year:
            check_in_date = f"{current_year}-{cin_date.strftime('%m-%d')}"
            logger.info(f"Adjusted check_in_date from {cin_date.year} to {current_year}: {check_in_date}")
    except ValueError:
        return {"error": "Invalid check-in date: Unable to parse date."}
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", check_out_date):
        return {"error": "Invalid check-out date format: Must be YYYY-MM-DD."}
    try:
        cout_date = datetime.strptime(check_out_date, "%Y-%m-%d")
        if cout_date.year < current_year:
            check_out_date = f"{current_year}-{cout_date.strftime('%m-%d')}"
            logger.info(f"Adjusted check_out_date from {cout_date.year} to {current_year}: {check_out_date}")
    except ValueError:
        return {"error": "Invalid check-out date: Unable to parse date."}
        
    try:
        result = get_hotel_details(
            query=query,
            property_token=property_token,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            currency=currency,
            gl=gl,
            hl=hl,
            children=children,
            children_ages=children_ages,
            api_key=SERPAPI_KEY
        )
        return result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



@mcp.tool()
async def search_events(
    query: str,
    location: Optional[str] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    start: Optional[int] = None,
    filters: Optional[List[str]] = None
) -> Dict:
    """
    Search for current events in a specified location using the SerpApi Google Events API.

    This tool retrieves a list of events based on the provided search query and optional filters.
    The query should include the location (e.g., "Events in Austin, TX"). Use the `filters` parameter
    to narrow down results by date or event type (e.g., ["date:today"] for today's events).

    Args:
        query (str): The search query, including the location (e.g., "Events in Austin, TX"). Required.
        location (str, optional): The city or region to originate the search from (e.g., "Austin, TX").
            If omitted, the location in the query is used.
        gl (str, optional): Country code for localization (e.g., "us" for United States, "uk" for United Kingdom).
            See Google countries: https://serpapi.com/google-countries
        hl (str, optional): Language code for results (e.g., "en" for English, "fr" for French).
            See Google languages: https://serpapi.com/google-languages
        start (int, optional): Result offset for pagination (e.g., 0 for first page, 10 for second page).
        filters (List[str], optional): Filters for events. Options:
            - "date:today" - Today's events
            - "date:tomorrow" - Tomorrow's events
            - "date:week" - This week's events
            - "date:weekend" - This weekend's events
            - "date:next_week" - Next week's events
            - "date:month" - This month's events
            - "date:next_month" - Next month's events
            - "event_type:Virtual-Event" - Online events
            Multiple filters can be combined (e.g., ["date:today", "event_type:Virtual-Event"]).

    Returns:
        A JSON object with the following structure:
        {
            "search_metadata": {
                "status": str,  // e.g., "Success"
                "created_at": str  // e.g., "2025-06-26 19:52:23 UTC"
            },
            "search_parameters": {
                "q": str,  // e.g., "Events in Austin, TX"
                "engine": str  // e.g., "google_events"
            },
            "events_results": [
                {
                    "title": str,  // e.g., "Austin City Limits Music Festival"
                    "date": {
                        "start_date": str,  // e.g., "Oct 1"
                        "when": str  // e.g., "Oct 1 – 10"
                    },
                    "address": [str],  // e.g., ["Zilker Park, 2207 Lou Neff Rd", "Austin, TX"]
                    "link": str,  // e.g., "https://www.austintexas.org/event/..."
                    "description": str,  // Brief event description
                    "ticket_info": [
                        {
                            "source": str,  // e.g., "Mileycyrus.com"
                            "link": str,  // e.g., "https://mileycyrus.com/events/..."
                            "link_type": str  // e.g., "tickets" or "more info"
                        }
                    ],
                    "venue": {
                        "name": str,  // e.g., "Zilker Park"
                        "rating": float,  // e.g., 4.8
                        "reviews": int,  // e.g., 837
                        "link": str  // e.g., "https://www.google.com/search?q=Zilker+Park..."
                    },
                    "thumbnail": str  // e.g., "https://encrypted-tbn0.gstatic.com/..."
                }
            ]
        }
        If the request fails, returns: {"error": str}  // e.g., "API request failed: <reason>"
    """
    try:
        result = get_events(
            query=query,
            location=location,
            gl=gl,
            hl=hl,
            start=start,
            htichips=filters,
            api_key=SERPAPI_KEY
        )
        return result
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



@mcp.tool()
async def search_places(
    query: str,
    gl: Optional[str] = None,
    hl: Optional[str] = None
) -> Dict:
    """
    Search for top sights or places (e.g., attractions, restaurants) using the SerpApi Google Top Sights API.

    This tool retrieves a list of top sights or places based on the provided search query, such as
    "top sights in Paris" or "best restaurants in Paris". The response includes categories (e.g., "Local favorites"),
    sights with details like title, description, rating, reviews, and thumbnail, and a link to view more results.

    Args:
        query (str): The search query, including the type of place and location (e.g., "top sights in Paris" or
            "best restaurants in Paris"). Required.
        gl (str, optional): Country code for localization (e.g., "us" for United States, "fr" for France).
            See Google countries: https://serpapi.com/google-countries
        hl (str, optional): Language code for results (e.g., "en" for English, "fr" for French).
            See Google languages: https://serpapi.com/google-languages

    Returns:
        A JSON object with the following structure:
        {
            "search_metadata": {
                "status": str,  // e.g., "Success"
                "created_at": str  // e.g., "2025-06-26 19:52:23 UTC"
            },
            "search_parameters": {
                "q": str,  // e.g., "top sights in Paris"
                "engine": str  // e.g., "google"
            },
            "top_sights": {
                "categories": [
                    {
                        "title": str,  // e.g., "Local favorites"
                        "link": str  // e.g., "https://www.google.com/travel/things-to-do/..."
                    }
                ],
                "sights": [
                    {
                        "title": str,  // e.g., "Eiffel Tower"
                        "link": str,  // e.g., "https://www.google.com/travel/things-to-do/..."
                        "description": str,  // e.g., "Landmark 324m-high 19th-century tower"
                        "rating": float,  // e.g., 4.6
                        "reviews": int,  // e.g., 273384
                        "thumbnail": str  // e.g., "https://serpapi.com/searches/..."
                    }
                ],
                "show_more_link": str  // e.g., "https://www.google.com/travel/things-to-do/..."
            }
        }
        If the request fails or no top sights are found, returns: {"error": str}  // e.g., "No top sights found"
    """
    try:
        result = get_places(
            query=query,
            gl=gl,
            hl=hl,
            api_key=SERPAPI_KEY
        )
        return result
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



@mcp.tool()
async def get_latest_currency_rates(
    base: str,
) -> Dict:
    """
    Getting the latest currency rates in the world
    Args: base: str, the base currency to get the rates for. Example: "USD"
    Returns:
        json: {
        "date": "2023-03-21 12:43:00+00",
        "base": "USD",
        "rates": {
            "AGLD": "2.3263929277654998",
            "FJD": "2.21592",
            "MXN": "18.670707655673546",
            "LVL": "0.651918",
            "SCR": "13.21713243157135",
            "CDF": "2068.490771",
            "BBD": "2.0",
            "HNL": "24.57644632001569",
            .
            .
            .
        }
        }
    """
    try:
        result = get_current_currency_rates(
            base=base,
            api_key=CURRENCYFREAKS_API_KEY
        )
        return result
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def current_date() -> Dict:
    """
    Retrieve the current date and time and year.

    This tool provides the current date and time to ensure accurate time-sensitive queries.

    Returns:
        A JSON object with the following structure:
        {
            "date": str,  // e.g., "2025-06-26"
            "time": str,  // e.g., "23:48:00"
            "timezone": str  // e.g., "EDT"
        }
    """
    try:
        return get_current_date()
    except Exception as e:
        return {"error": f"Failed to get current date: {str(e)}"}


if __name__ == "__main__":
    logger.info("Starting Serp MCP server...")
    mcp.run(transport='stdio')
    logger.info("Serp MCP server stopped.")
