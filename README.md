# Travel Agent MCP Server
[![smithery badge](https://smithery.ai/badge/@alan5543/travel-agent-mcp-server)](https://smithery.ai/server/@alan5543/travel-agent-mcp-server)

## Introduction
The Travel Agent MCP Server empowers Large Language Models (LLMs) to function as a travel agent by leveraging the SerpApi and CurrencyFreaks APIs to search for travel-related information. It supports hotel searches, detailed hotel information retrieval, event and place searches, and currency rate lookups, making it ideal for planning trips and accommodations. This server integrates seamlessly with MCP-compatible clients (e.g., Claude Desktop) and requires `SERPAPI_KEY` and `CURRENCYFREAKS_API_KEY` for operation.

## Demo Video


https://github.com/user-attachments/assets/0773b2ae-d49b-482f-a6fe-6173e387a4bf



## Tools
The server provides five tools to assist with travel planning, each with detailed parameters and return values for clarity:

### `search_hotels`
- **Function**: `search_hotels(query: str, check_in_date: str, check_out_date: str, adults: int = 2, currency: str = "USD", gl: str = "us", hl: str = "en", sort_by: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, property_types: Optional[List[str]] = None, amenities: Optional[List[str]] = None, rating: Optional[str] = None, hotel_class: Optional[List[str]] = None, free_cancellation: Optional[bool] = None, special_offers: Optional[bool] = None, eco_certified: Optional[bool] = None, vacation_rentals: Optional[bool] = None, bedrooms: Optional[int] = None, bathrooms: Optional[int] = None, children: Optional[int] = None, children_ages: Optional[List[int]] = None, next_page_token: Optional[str] = None) -> Dict`
- **Description**: Searches for hotels or vacation rentals in a specified location using the SerpApi Google Hotels API, with customizable filters and pagination support.
- **Parameters**:
  - `query: str`: Location to search (e.g., "Hong Kong"). Required.
  - `check_in_date: str`: Check-in date in YYYY-MM-DD format (e.g., "2025-06-27"). Required.
  - `check_out_date: str`: Check-out date in YYYY-MM-DD format (e.g., "2025-06-28"). Required.
  - `adults: int`: Number of adults (default: 2).
  - `currency: str`: Currency code for prices (e.g., "USD", "EUR"). Default: "USD".
  - `gl: str`: Country code for localization (e.g., "us", "uk"). Default: "us".
  - `hl: str`: Language code for results (e.g., "en", "fr"). Default: "en".
  - `sort_by: Optional[str]`: Sorting option: "LOWEST_PRICE", "HIGHEST_RATING", "MOST_REVIEWED". Default: None.
  - `min_price: Optional[float]`: Minimum price per night. Default: None.
  - `max_price: Optional[float]`: Maximum price per night. Default: None.
  - `property_types: Optional[List[str]]`: Property types to filter (e.g., "BEACH_HOTELS", "RESORTS", "APARTMENT_HOTELS"). Default: None.
  - `amenities: Optional[List[str]]`: Amenities to filter (e.g., "FREE_WIFI", "POOL", "PET_FRIENDLY"). Default: None.
  - `rating: Optional[str]`: Minimum rating: "THREE_POINT_FIVE_PLUS", "FOUR_PLUS", "FOUR_POINT_FIVE_PLUS". Default: None.
  - `hotel_class: Optional[List[str]]`: Hotel star ratings: "TWO_STAR", "THREE_STAR", "FOUR_STAR", "FIVE_STAR". Default: None.
  - `free_cancellation: Optional[bool]`: Filter for free cancellation. Default: None.
  - `special_offers: Optional[bool]`: Filter for special offers. Default: None.
  - `eco_certified: Optional[bool]`: Filter for eco-certified properties. Default: None.
  - `vacation_rentals: Optional[bool]`: If True, search for vacation rentals. Default: None.
  - `bedrooms: Optional[int]`: Minimum bedrooms for vacation rentals. Default: None.
  - `bathrooms: Optional[int]`: Minimum bathrooms for vacation rentals. Default: None.
  - `children: Optional[int]`: Number of children. Default: None.
  - `children_ages: Optional[List[int]]`: Ages of children (1-17). Must match `children` count. Default: None.
  - `next_page_token: Optional[str]`: Token for next page of results. Default: None.
- **Returns**: A JSON dictionary containing:
  - `properties`: List of properties with details like type, name, description, link, GPS coordinates, rate per night, hotel class, rating, reviews, amenities, and property token.
  - `serpapi_pagination`: Pagination details (current range, next page token).
  - If failed: `{"error": str}` (e.g., "API request failed: <reason>").

### `find_hotel_detail`
- **Function**: `find_hotel_detail(query: str, property_token: str, check_in_date: str, check_out_date: str, adults: int = 2, currency: str = "USD", gl: str = "us", hl: str = "en", children: Optional[int] = None, children_ages: Optional[List[int]] = None) -> Dict`
- **Description**: Retrieves detailed information for a specific hotel or vacation rental using a `property_token` from `search_hotels`.
- **Parameters**:
  - `query: str`: Original search query (e.g., "Hong Kong"). Required.
  - `property_token: str`: Unique token from `search_hotels`. Required.
  - `check_in_date: str`: Check-in date in YYYY-MM-DD format (e.g., "2025-06-27"). Required.
  - `check_out_date: str`: Check-out date in YYYY-MM-DD format (e.g., "2025-06-28"). Required.
  - `adults: int`: Number of adults (default: 2).
  - `currency: str`: Currency code for prices (e.g., "USD"). Default: "USD".
  - `gl: str`: Country code for localization (e.g., "us"). Default: "us".
  - `hl: str`: Language code for results (e.g., "en"). Default: "en".
  - `children: Optional[int]`: Number of children. Default: None.
  - `children_ages: Optional[List[int]]`: Ages of children (1-17). Must match `children` count. Default: None.
- **Returns**: A JSON dictionary with:
  - `search_metadata`: Status and creation time.
  - `search_parameters`: Query details.
  - `hotel`: Name, description, link, address, phone, GPS coordinates, check-in/out times, rates, deal, hotel class, rating, reviews, images, amenities.
  - `prices`: List of source-rate pairs.
  - `nearby_places`: Points of interest and restaurants with names, distances, and ratings.
  - `reviews_summary`: Total reviews, star breakdown, and top categories.
  - If failed: `{"error": str}` (e.g., "API request failed: <reason>").

### `search_events`
- **Function**: `search_events(query: str, location: Optional[str] = None, gl: Optional[str] = None, hl: Optional[str] = None, start: Optional[int] = None, filters: Optional[List[str]] = None) -> Dict`
- **Description**: Searches for current events in a specified location using the SerpApi Google Events API.
- **Parameters**:
  - `query: str`: Search query with location (e.g., "Events in Austin, TX"). Required.
  - `location: Optional[str]`: City or region (e.g., "Austin, TX"). Default: None (uses query location).
  - `gl: Optional[str]`: Country code for localization (e.g., "us"). Default: None.
  - `hl: Optional[str]`: Language code for results (e.g., "en"). Default: None.
  - `start: Optional[int]`: Result offset for pagination (e.g., 0 for first page). Default: None.
  - `filters: Optional[List[str]]`: Event filters (e.g., "date:today", "event_type:Virtual-Event"). Default: None.
- **Returns**: A JSON dictionary with:
  - `search_metadata`: Status and creation time.
  - `search_parameters`: Query and engine details.
  - `events_results`: List of events with title, date, address, link, description, ticket info, venue details, and thumbnail.
  - If failed: `{"error": str}` (e.g., "API request failed: <reason>").

### `search_places`
- **Function**: `search_places(query: str, gl: Optional[str] = None, hl: Optional[str] = None) -> Dict`
- **Description**: Searches for top sights or places (e.g., attractions, restaurants) using the SerpApi Google Top Sights API.
- **Parameters**:
  - `query: str`: Search query with place type and location (e.g., "top sights in Paris"). Required.
  - `gl: Optional[str]`: Country code for localization (e.g., "us"). Default: None.
  - `hl: Optional[str]`: Language code for results (e.g., "en"). Default: None.
- **Returns**: A JSON dictionary with:
  - `search_metadata`: Status and creation time.
  - `search_parameters`: Query and engine details.
  - `top_sights`: Categories and sights with title, link, description, rating, reviews, thumbnail, and show-more link.
  - If failed: `{"error": str}` (e.g., "No top sights found").

### `get_latest_currency_rates`
- **Function**: `get_latest_currency_rates(base: str) -> Dict`
- **Description**: Retrieves the latest currency exchange rates using the CurrencyFreaks API.
- **Parameters**:
  - `base: str`: Base currency code (e.g., "USD"). Required.
- **Returns**: A JSON dictionary with:
  - `date`: Timestamp of rates.
  - `base`: Base currency code.
  - `rates`: Dictionary of currency codes and their exchange rates.
  - If failed: `{"error": str}` (e.g., "Unexpected error: <reason>").

### `current_date`
- **Function**: `current_date() -> Dict`
- **Description**: Retrieves the current date, time, and timezone for accurate time-sensitive queries.
- **Parameters**: None.
- **Returns**: A JSON dictionary with:
  - `date`: Current date (e.g., "2025-06-30").
  - `time`: Current time (e.g., "17:18:00").
  - `timezone`: Current timezone (e.g., "EDT").
  - If failed: `{"error": str}` (e.g., "Failed to get current date: <reason>").

## Obtaining API Keys
To use the Travel Agent MCP Server, you need to set up an .env file with `SERPAPI_KEY` and `CURRENCYFREAKS_API_KEY`. Follow these steps to obtain them:
1. **SERPAPI_KEY**:
   - Visit [https://serpapi.com/](https://serpapi.com/).
   - Sign up for an account and verify your email.
   - Navigate to your dashboard and locate your API key under account settings.
   - Copy the key for use in the configuration.
2. **CURRENCYFREAKS_API_KEY**:
   - Visit [https://currencyfreaks.com/](https://currencyfreaks.com/).
   - Register for an account.
   - Find your API key in the account settings or dashboard.
   - Copy the key for use in the configuration.

## Manual Configuration
To set up the Travel Agent MCP Server locally:
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   ```

2. **Set Up UV**:
   Install UV (a Python package and project manager). Follow the official UV documentation for installation instructions.

3. **Configure MCP Client**:
   Add the following to your MCP client configuration (e.g., Claude Desktop), including your API keys:
   ```json
   "travel-agent-mcp-server": {
       "command": "uv",
       "args": [
           "--directory",
           "YOUR_CLONED_FOLDER",
           "run",
           "main.py"
       ],
       "env": {
           "SERPAPI_KEY": "your_serpapi_key",
           "CURRENCYFREAKS_API_KEY": "your_currencyfreaks_api_key"
       }
   }
   ```
   Replace `YOUR_CLONED_FOLDER` with the path to the cloned repository, and replace `your_serpapi_key` and `your_currencyfreaks_api_key` with the actual keys obtained from SerpApi and CurrencyFreaks.

## Remote MCP Server Configuration
The Travel Agent MCP Server is hosted remotely at [https://smithery.ai/server/@alan5543/travel-agent-mcp-server](https://smithery.ai/server/@alan5543/travel-agent-mcp-server). To use it:
1. Visit [https://smithery.ai](https://smithery.ai) and sign in or create an account.
2. Go to the server page: [https://smithery.ai/server/@alan5543/travel-agent-mcp-server](https://smithery.ai/server/@alan5543/travel-agent-mcp-server).
3. Click "Add to Client" or follow Smithery.ai's integration instructions.
4. Update your MCP client (e.g., Claude Desktop) to use the remote server URL. Check your client's documentation for details on configuring remote MCP servers.
5. Ensure your API keys (`SERPAPI_KEY` and `CURRENCYFREAKS_API_KEY`) are configured on the remote server via Smithery.ai or as instructed in the platform's documentation.
6. Test the connection to confirm the server is accessible and working.
