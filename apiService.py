import requests
from typing import Dict, List, Optional
from datetime import datetime
from enumType import SortBy, Rating, HotelClass, PropertyType, Amenity


def get_hotel_list(
    query: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    currency: str = "USD",
    gl: str = "us",
    hl: str = "en",
    sort_by: Optional[SortBy] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    property_types: Optional[List[PropertyType]] = None,
    amenities: Optional[List[Amenity]] = None,
    rating: Optional[Rating] = None,
    hotel_class: Optional[List[HotelClass]] = None,
    free_cancellation: Optional[bool] = None,
    special_offers: Optional[bool] = None,
    eco_certified: Optional[bool] = None,
    vacation_rentals: Optional[bool] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    children: Optional[int] = None,
    children_ages: Optional[List[int]] = None,
    next_page_token: Optional[str] = None,
    api_key: str = "YOUR_API_KEY"
) -> Dict:
    """
    Retrieve a filtered list of hotels or vacation rentals from the SerpApi Google Hotels API.

    This function sends a GET request to the SerpApi Google Hotels API to fetch a list of properties
    (hotels or vacation rentals) based on the provided search parameters. The response is filtered to
    include only the `properties` and `serpapi_pagination` keys. Use the `property_token` from the
    `properties` list to fetch detailed information about a specific property using `get_hotel_details`.

    Args:
        query (str): The search query (e.g., "Hong Kong"). Required.
        check_in_date (str): Check-in date in YYYY-MM-DD format (e.g., "2025-06-27"). Required.
        check_out_date (str): Check-out date in YYYY-MM-DD format (e.g., "2025-06-28"). Required.
        adults (int, optional): Number of adults. Defaults to 2.
        currency (str, optional): Currency code for prices (e.g., "USD", "EUR"). Defaults to "USD".
            See Google Travel Currencies: https://serpapi.com/google-travel-currencies
        gl (str, optional): Country code for localization (e.g., "us" for United States, "uk" for United Kingdom).
            Defaults to "us". See Google countries: https://serpapi.com/google-countries
        hl (str, optional): Language code for results (e.g., "en" for English, "fr" for French).
            Defaults to "en". See Google languages: https://serpapi.com/google-languages
        sort_by (SortBy, optional): Sorting option for results. Defaults to None (sort by relevance).
            Options:
            - SortBy.LOWEST_PRICE: Sort by lowest price.
            - SortBy.HIGHEST_RATING: Sort by highest rating.
            - SortBy.MOST_REVIEWED: Sort by most reviewed.
        min_price (int, optional): Minimum price per night filter. Defaults to None.
        max_price (int, optional): Maximum price per night filter. Defaults to None.
        property_types (List[PropertyType], optional): List of property types to filter results.
            Defaults to None. Options:
            - PropertyType.BEACH_HOTELS: Beach hotels.
            - PropertyType.BOUTIQUE_HOTELS: Boutique hotels.
            - PropertyType.HOSTELS: Hostels.
            - PropertyType.INNS: Inns.
            - PropertyType.MOTELS: Motels.
            - PropertyType.RESORTS: Resorts.
            - PropertyType.SPA_HOTELS: Spa hotels.
            - PropertyType.BED_AND_BREAKFASTS: Bed and breakfasts.
            - PropertyType.OTHER: Other property types.
            - PropertyType.APARTMENT_HOTELS: Apartment hotels.
            - PropertyType.MINSHUKU: Japanese guesthouses (Minshuku).
            - PropertyType.JAPANESE_STYLE_BUSINESS_HOTELS: Japanese-style business hotels.
            - PropertyType.RYOKAN: Japanese inns (Ryokan).
            Note: For vacation rentals (when vacation_rentals=True), additional property types may apply.
            See Google Vacation Rentals Property Types: https://serpapi.com/google-vacation-rentals-property-types
        amenities (List[Amenity], optional): List of amenities to filter results.
            Defaults to None. Options:
            - Amenity.FREE_PARKING: Free parking.
            - Amenity.PARKING: Parking (paid or free).
            - Amenity.INDOOR_POOL: Indoor pool.
            - Amenity.OUTDOOR_POOL: Outdoor pool.
            - Amenity.POOL: Any pool.
            - Amenity.FITNESS_CENTER: Fitness center.
            - Amenity.RESTAURANT: Restaurant.
            - Amenity.FREE_BREAKFAST: Free breakfast.
            - Amenity.SPA: Spa.
            - Amenity.BEACH_ACCESS: Beach access.
            - Amenity.CHILD_FRIENDLY: Child-friendly.
            - Amenity.BAR: Bar.
            - Amenity.PET_FRIENDLY: Pet-friendly.
            - Amenity.ROOM_SERVICE: Room service.
            - Amenity.FREE_WIFI: Free Wi-Fi.
            - Amenity.AIR_CONDITIONED: Air-conditioned.
            - Amenity.ALL_INCLUSIVE_AVAILABLE: All-inclusive available.
            - Amenity.WHEELCHAIR_ACCESSIBLE: Wheelchair accessible.
            - Amenity.EV_CHARGER: EV charger.
            Note: For vacation rentals, additional amenities may apply.
            See Google Vacation Rentals Amenities: https://serpapi.com/google-vacation-rentals-amenities
        rating (Rating, optional): Minimum rating filter. Defaults to None.
            Options:
            - Rating.THREE_POINT_FIVE_PLUS: 3.5+ rating.
            - Rating.FOUR_PLUS: 4.0+ rating.
            - Rating.FOUR_POINT_FIVE_PLUS: 4.5+ rating.
        hotel_class (List[HotelClass], optional): List of hotel star ratings to filter results.
            Defaults to None. Not available for vacation rentals. Options:
            - HotelClass.TWO_STAR: 2-star hotels.
            - HotelClass.THREE_STAR: 3-star hotels.
            - HotelClass.FOUR_STAR: 4-star hotels.
            - HotelClass.FIVE_STAR: 5-star hotels.
        free_cancellation (bool, optional): Filter for properties offering free cancellation. Defaults to None.
            Not available for vacation rentals.
        special_offers (bool, optional): Filter for properties with special offers. Defaults to None.
            Not available for vacation rentals.
        eco_certified (bool, optional): Filter for eco-certified properties. Defaults to None.
            Not available for vacation rentals.
        vacation_rentals (bool, optional): If True, search for vacation rentals instead of hotels. Defaults to None.
        bedrooms (int, optional): Minimum number of bedrooms for vacation rentals. Defaults to None.
            Only applicable when vacation_rentals=True.
        bathrooms (int, optional): Minimum number of bathrooms for vacation rentals. Defaults to None.
            Only applicable when vacation_rentals=True.
        children (int, optional): Number of children. Defaults to None (0).
        children_ages (List[int], optional): Ages of children (1 to 17). Must match the number of children specified.
            Defaults to None. Example: [5, 8] for two children aged 5 and 8.
        next_page_token (str, optional): Token for retrieving the next page of results. Defaults to None.
        api_key (str): SerpApi private key. Required. Replace "YOUR_API_KEY" with your actual key.

    Returns:
        Dict: Filtered JSON response from the API containing:
            - properties: List of properties (hotels or vacation rentals) with details:
                - type (str): Type of property (e.g., "hotel" or "vacation rental").
                - name (str): Name of the property (e.g., "Hong Kong SkyCity Marriott Hotel").
                - description (str): Brief description of the property.
                - link (str): URL to the property's website or booking page.
                - gps_coordinates (dict): Latitude and longitude of the property.
                - rate_per_night (dict): Pricing details with:
                    - lowest (str): Lowest price per night with currency (e.g., "$173").
                    - extracted_lowest (float): Numeric value of the lowest price (e.g., 173).
                - hotel_class (str): Star rating of the hotel (e.g., "5-star hotel").
                - overall_rating (float): Average guest rating (e.g., 4.3).
                - reviews (int): Number of guest reviews (e.g., 4201).
                - amenities (List[str]): List of amenities offered (e.g., ["Free Wi-Fi", "Indoor pool"]).
            - serpapi_pagination (dict): Pagination details with:
                - current_from (int): Start index of current page (e.g., 1).
                - current_to (int): End index of current page (e.g., 18).
                - next_page_token (str): Token for fetching the next page of results (e.g., "CBI=").
            If the request fails, returns a dictionary with an "error" key (e.g., {"error": "API request failed: <reason>"}).

    Raises:
        ValueError: If check_in_date or check_out_date is not in YYYY-MM-DD format, or if children_ages length does not match children count.
    """
    # Validate date format
    try:
        datetime.strptime(check_in_date, "%Y-%m-%d")
        datetime.strptime(check_out_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    # Validate children_ages matches children count
    if children is not None and children_ages is not None:
        if len(children_ages) != children:
            raise ValueError("Number of children_ages must match the number of children")

    # Build query parameters
    params = {
        "engine": "google_hotels",
        "q": query,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": currency,
        "gl": gl,
        "hl": hl,
        "api_key": api_key
    }

    # Add optional parameters if provided
    if sort_by:
        params["sort_by"] = sort_by.value  # Convert SortBy Enum to string value (e.g., "3")
    if min_price:
        params["min_price"] = min_price  # Minimum price filter for the search
    if max_price:
        params["max_price"] = max_price  # Maximum price filter for the search
    if property_types:
        params["property_types"] = ",".join([pt.value for pt in property_types])  # Convert PropertyType Enums to comma-separated string (e.g., "17,18")
    if amenities:
        params["amenities"] = ",".join([a.value for a in amenities])  # Convert Amenity Enums to comma-separated string (e.g., "35,6")
    if rating:
        params["rating"] = rating.value  # Convert Rating Enum to string value (e.g., "8")
    if hotel_class:
        params["hotel_class"] = ",".join([hc.value for hc in hotel_class])  # Convert HotelClass Enums to comma-separated string (e.g., "4,5")
    if free_cancellation is not None:
        params["free_cancellation"] = str(free_cancellation).lower()  # Boolean filter for free cancellation
    if special_offers is not None:
        params["special_offers"] = str(special_offers).lower()  # Boolean filter for special offers
    if eco_certified is not None:
        params["eco_certified"] = str(eco_certified).lower()  # Boolean filter for eco-certified properties
    if vacation_rentals is not None:
        params["vacation_rentals"] = str(vacation_rentals).lower()  # Boolean to search for vacation rentals instead of hotels
    if bedrooms:
        params["bedrooms"] = bedrooms  # Minimum number of bedrooms for vacation rentals
    if bathrooms:
        params["bathrooms"] = bathrooms  # Minimum number of bathrooms for vacation rentals
    if children:
        params["children"] = children  # Number of children for the booking
    if children_ages:
        params["children_ages"] = ",".join(map(str, children_ages))  # Comma-separated ages of children (e.g., "5,8")
    if next_page_token:
        params["next_page_token"] = next_page_token  # Token for fetching the next page of results

    # Make API request
    try:
        response = requests.get("https://serpapi.com/search.json", params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        # Filter response to include only 'properties' and 'serpapi_pagination'
        full_response = response.json()
        filtered_response = {
            "properties": full_response.get("properties", []),  # List of properties with details
            "serpapi_pagination": full_response.get("serpapi_pagination", {})  # Pagination details
        }
        return filtered_response
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}  # Return error message if request fails


def get_hotel_details(
    query: str,
    property_token: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    currency: str = "USD",
    gl: str = "us",
    hl: str = "en",
    children: Optional[int] = None,
    children_ages: Optional[List[int]] = None,
    api_key: str = "YOUR_API_KEY"
) -> Dict:
    """
    Retrieve details for a specific hotel or vacation rental using the SerpApi Google Hotels API.

    This function sends a GET request to the SerpApi Google Hotels API to fetch detailed information
    about a specific property identified by its `property_token`. The response includes details such as
    the property's name, address, phone number, prices, amenities, nearby places, ratings, and images.
    Use the `property_token` obtained from the `get_hotel_list` response to query a specific property.

    Args:
        query (str): The search query used in the original hotel list search (e.g., "Hong Kong"). Required.
        property_token (str): Unique token identifying the property (obtained from `get_hotel_list` response). Required.
        check_in_date (str): Check-in date in YYYY-MM-DD format (e.g., "2025-06-27"). Required.
        check_out_date (str): Check-out date in YYYY-MM-DD format (e.g., "2025-06-28"). Required.
        adults (int, optional): Number of adults. Defaults to 2.
        currency (str, optional): Currency code for prices (e.g., "USD", "EUR"). Defaults to "USD".
            See Google Travel Currencies: https://serpapi.com/google-travel-currencies
        gl (str, optional): Country code for localization (e.g., "us" for United States, "uk" for United Kingdom).
            Defaults to "us". See Google countries: https://serpapi.com/google-countries
        hl (str, optional): Language code for results (e.g., "en" for English, "fr" for French).
            Defaults to "en". See Google languages: https://serpapi.com/google-languages
        children (int, optional): Number of children. Defaults to None (0).
        children_ages (List[int], optional): Ages of children (1 to 17). Must match the number of children specified.
            Defaults to None. Example: [5, 8] for two children aged 5 and 8.
        api_key (str): SerpApi private key. Required. Replace "YOUR_API_KEY" with your actual key.

    Returns:
        Dict: JSON response from the API containing detailed information about the specified property,
            structured as follows:
            - search_metadata (dict): Metadata about the API request:
                - status (str): Status of the request (e.g., "Success").
                - created_at (str): Timestamp of the request (e.g., "2025-06-26 19:52:23 UTC").
            - search_parameters (dict): Parameters used in the request:
                - q (str): Search query (e.g., "Hong Kong").
                - check_in_date (str): Check-in date (e.g., "2025-06-27").
                - check_out_date (str): Check-out date (e.g., "2025-06-28").
                - adults (int): Number of adults (e.g., 2).
                - children (int, optional): Number of children (e.g., 2).
            - hotel (dict): Details of the property:
                - name (str): Name of the property (e.g., "Regal Airport Hotel Hong Kong").
                - description (str): Brief description of the property.
                - link (str): URL to the property's website or booking page.
                - address (str): Full address of the property (e.g., "9 Cheong Tat Road, Hong Kong International Airport Chek Lap Kok, Lantau Island, Hong Kong").
                - phone (str): Phone number of the property (e.g., "+852 2286 8888").
                - gps_coordinates (dict): Latitude and longitude of the property (e.g., {"latitude": 22.3186949, "longitude": 113.9343274}).
                - check_in_time (str): Check-in time (e.g., "2:00 PM").
                - check_out_time (str): Check-out time (e.g., "12:00 PM").
                - rates (dict): Pricing details:
                    - lowest (str): Lowest price per night with currency (e.g., "US$190").
                    - before_taxes (str): Price before taxes and fees (e.g., "US$174").
                - deal (str, optional): Description of any discount (e.g., "41% less than usual").
                - hotel_class (str): Star rating of the hotel (e.g., "5-star hotel").
                - overall_rating (float): Average guest rating (e.g., 4.0).
                - reviews (int): Number of guest reviews (e.g., 5681).
                - images (list): List of image dictionaries with:
                    - thumbnail (str): URL to a thumbnail image.
                - amenities (List[str]): List of amenities offered (e.g., ["6 restaurants", "Spa", "Gym", "Indoor/outdoor pools"]).
            - prices (dict): Pricing information from different sources:
                - sources (list): List of price sources, each with:
                    - source (str): Name of the booking source (e.g., "klook", "Priceline").
                    - rate (str): Price offered by the source (e.g., "US$190").
            - nearby_places (dict): Nearby points of interest and restaurants:
                - points_of_interest (list): List of nearby attractions, each with:
                    - name (str): Name of the attraction (e.g., "Hong Kong Disneyland").
                    - distance (str): Distance from the property (e.g., "18 km").
                    - rating (float): Rating of the attraction (e.g., 4.5).
                - restaurants (list): List of nearby restaurants, each with:
                    - name (str): Name of the restaurant (e.g., "Rouge 紅軒").
                    - type (str): Type of cuisine (e.g., "Cantonese").
                    - rating (float): Rating of the restaurant (e.g., 4.0).
            - reviews_summary (dict): Summary of guest reviews:
                - total (int): Total number of reviews (e.g., 5681).
                - breakdown (dict): Breakdown of star ratings (e.g., {"5_star": 2401, "4_star": 1749}).
                - top_categories (list): List of review categories, each with:
                    - name (str): Category name (e.g., "Location", "Service").
                    - rating (float): Rating for the category (e.g., 4.0).
            If the request fails, returns a dictionary with an "error" key (e.g., {"error": "API request failed: <reason>"}).

    Raises:
        ValueError: If check_in_date or check_out_date is not in YYYY-MM-DD format, or if children_ages length does not match children count.
    """
    # Validate date format
    try:
        datetime.strptime(check_in_date, "%Y-%m-%d")
        datetime.strptime(check_out_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    # Validate children_ages matches children count
    if children is not None and children_ages is not None:
        if len(children_ages) != children:
            raise ValueError("Number of children_ages must match the number of children")

    # Validate query parameter
    if not query:
        raise ValueError("Query parameter 'q' is required")

    # Build query parameters
    params = {
        "engine": "google_hotels",  # Specify Google Hotels API engine
        "q": query,  # Search query for context (required for property details)
        "property_token": property_token,  # Unique identifier for the property
        "check_in_date": check_in_date,  # Check-in date for booking
        "check_out_date": check_out_date,  # Check-out date for booking
        "adults": adults,  # Number of adults for the booking
        "currency": currency,  # Currency for pricing
        "gl": gl,  # Country code for localization
        "hl": hl,  # Language code for results
        "api_key": api_key  # SerpApi private key
    }

    # Add optional parameters
    if children:
        params["children"] = children  # Number of children for the booking
    if children_ages:
        params["children_ages"] = ",".join(map(str, children_ages))  # Comma-separated ages of children

    # Make API request
    try:
        response = requests.get("https://serpapi.com/search.json", params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return full response for property details
    except requests.HTTPError as e:
        # Capture detailed error message for debugging
        error_message = f"API request failed: {str(e)}"
        if e.response.status_code == 400:
            error_message += f"\nError Response: {e.response.text}"
        return {"error": error_message}  # Return detailed error message
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}  # Return error message for other request issues



def get_events(
    query: str,
    location: Optional[str] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    start: Optional[int] = None,
    htichips: Optional[List[str]] = None,
    api_key: str = ""
) -> Dict:
    """
    Retrieve a list of current events from the SerpApi Google Events API.

    This function sends a GET request to the SerpApi Google Events API to fetch events based on the provided
    search query and optional filters. The response includes event details such as title, date, address,
    ticket information, and venue details.

    Args:
        query (str): The search query, including the location (e.g., "Events in Austin, TX"). Required.
        location (str, optional): The city or region to originate the search from (e.g., "Austin, TX").
            If omitted, the location in the query is used. Cannot be used with uule.
        gl (str, optional): Country code for localization (e.g., "us" for United States, "uk" for United Kingdom).
            See Google countries: https://serpapi.com/google-countries
        hl (str, optional): Language code for results (e.g., "en" for English, "fr" for French).
            See Google languages: https://serpapi.com/google-languages
        start (int, optional): Result offset for pagination (e.g., 0 for first page, 10 for second page).
        htichips (List[str], optional): Filters for events. Options:
            - "date:today" - Today's events
            - "date:tomorrow" - Tomorrow's events
            - "date:week" - This week's events
            - "date:weekend" - This weekend's events
            - "date:next_week" - Next week's events
            - "date:month" - This month's events
            - "date:next_month" - Next month's events
            - "event_type:Virtual-Event" - Online events
            Multiple filters can be combined (e.g., ["date:today", "event_type:Virtual-Event"]).
        api_key (str): SerpApi private key. Required.

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
    params = {
        "engine": "google_events",
        "q": query,
        "api_key": api_key
    }
    if location:
        params["location"] = location
    if gl:
        params["gl"] = gl
    if hl:
        params["hl"] = hl
    if start is not None:
        params["start"] = start
    if htichips:
        params["htichips"] = ",".join(htichips)

    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("search_metadata", {}).get("status") != "Success":
            return {"error": f"API request failed: {data.get('error', 'Unknown error')}"}
        return {
            "search_metadata": data.get("search_metadata", {}),
            "search_parameters": data.get("search_parameters", {}),
            "events_results": data.get("events_results", [])
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}




def get_places(
    query: str,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    api_key: str = ""
) -> Dict:
    """
    Retrieve a list of top sights or places (e.g., attractions, restaurants) from the SerpApi Google Top Sights API.

    This function sends a GET request to the SerpApi Google Top Sights API to fetch a list of top sights or places
    based on the provided search query (e.g., "top sights in Paris" or "best restaurants in Paris"). The response
    includes categories, sights with details such as title, description, rating, reviews, and thumbnail, and a link
    to view more results.

    Args:
        query (str): The search query, including the type of place and location (e.g., "top sights in Paris" or
            "best restaurants in Paris"). Required.
        gl (str, optional): Country code for localization (e.g., "us" for United States, "fr" for France).
            See Google countries: https://serpapi.com/google-countries
        hl (str, optional): Language code for results (e.g., "en" for English, "fr" for French).
            See Google languages: https://serpapi.com/google-languages
        api_key (str): SerpApi private key. Required.

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
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }
    if gl:
        params["gl"] = gl
    if hl:
        params["hl"] = hl

    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("search_metadata", {}).get("status") != "Success":
            return {"error": f"API request failed: {data.get('error', 'Unknown error')}"}
        if "top_sights" not in data:
            return {"error": "No top sights found"}
        return {
            "search_metadata": data.get("search_metadata", {}),
            "search_parameters": data.get("search_parameters", {}),
            "top_sights": data.get("top_sights", {})
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}




def get_current_currency_rates(
    base: str,
    api_key: str = ""
    ) -> str:
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
        # Construct API URL
        # Note: CurrencyFreaks API's /convert/latest endpoint directly takes amount
        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}&base={base}"

        # Make API request
        response = requests.get(url, timeout=10) # Added timeout for robustness
        response.raise_for_status()  # Raise exception for HTTP errors (4xx or 5xx)

        # Parse JSON response
        data = response.json()

        json_string = json.dumps(data) 

        return json_string

    except requests.exceptions.RequestException as e:
        return f"Request error during currency conversion: {e}"


def get_current_date() -> Dict:
    """
      Retrieve the current date and time.

      Returns:
          A JSON object with the current date and time:
          {
              "date": str,  // e.g., "2025-06-26"
              "time": str,  // e.g., "23:48:00"
              "timezone": str  // e.g., "EDT"
          }
    """
    current = datetime.now()
    return {
        "date": current.strftime("%Y-%m-%d"),
        "time": current.strftime("%H:%M:%S"),
        "timezone": "EDT"  # Hardcoded for now; use pytz for dynamic timezone if needed
    }





# Example usage
if __name__ == "__main__":
    # Example: Get hotel list for Bali Resorts
    hotel_list = get_hotel_list(
        query="Hong Kong",
        check_in_date="2025-06-27",
        check_out_date="2025-06-28",
        adults=2,
        vacation_rentals=False,
        sort_by=SortBy.LOWEST_PRICE,  # Sort by lowest price
        property_types=[PropertyType.RESORTS, PropertyType.SPA_HOTELS],  # Filter for resorts and spa hotels
        amenities=[Amenity.FREE_WIFI, Amenity.POOL, Amenity.SPA],  # Filter for Free Wi-Fi, Pool, and Spa
        rating=Rating.FOUR_PLUS,  # 4.0+ rating
        hotel_class=[HotelClass.FOUR_STAR, HotelClass.FIVE_STAR],  # 4-star and 5-star hotels
        children=2,
        children_ages=[5, 8]
    )
    print("Hotel List:", hotel_list)

    # Example: Get details for a specific hotel using property_token
    # Test with the specific property_token from the error
    hotel_details_specific = get_hotel_details(
        query="Hong Kong",  # Assuming the original search was for Hong Kong
        property_token="ChcI0JG23bq2mJNiGgsvZy8xNTVzbWo5cRAB",
        check_in_date="2025-06-27",
        check_out_date="2025-06-28",
        adults=2,
        children=2,
        children_ages=[5, 8],
        api_key="1c283f5976c4f462d92d6ff81463a50f9614b8d05702c33dfad5549bb2beab2a"
    )
    print("Hotel Details (Specific Token):", hotel_details_specific)
