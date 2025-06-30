# Flight Search MCP Server
[![smithery badge](https://smithery.ai/badge/@alan5543/flight-scraper)](https://smithery.ai/server/@alan5543/flight-scraper)

## Introduction
The Flight Search MCP Server enables Large Language Models (LLMs) to retrieve detailed flight information from Kayak without requiring an API key. Using web scraping, it collects comprehensive data on flights, including prices, schedules, airlines, baggage allowances, and more. This server integrates seamlessly with MCP-compatible clients (e.g., Claude Desktop) to enhance flight search and analysis capabilities.

## Tools
The server provides one tool for scraping flight data, detailed below with its function name, parameters, and return value for clarity:

### `scrape_flights_tool`
- **Function**: `scrape_flights_tool(departure_airport: str, arrival_airport: str, departure_date: str, return_date: Optional[str] = None, adults: int = 2, students: int = 0, children: List[str] = [], plane_type: str = "economy", sort_option: str = "price_a", carry_on_free: Optional[int] = 1, checked_bags_free: Optional[int] = None, stops: Optional[int] = None, max_price: Optional[int] = 6000, alliance: Optional[str] = None, include_airlines: Optional[Set[str]] = None, exclude_airlines: Optional[Set[str]] = None, wifi_only: bool = False, start_index: int = 0, end_index: int = 15) -> str`
- **Description**: Scrapes flight data from Kayak for specified airports and dates, supporting both one-way and round-trip searches with customizable filters and pagination.
- **Parameters**:
  - `departure_airport: str`: 3-letter IATA code for the departure airport (e.g., "YYZ" for Toronto).
  - `arrival_airport: str`: 3-letter IATA code for the arrival airport (e.g., "HKG" for Hong Kong).
  - `departure_date: str`: Departure date in YYYY-MM-DD format (e.g., "2025-07-01").
  - `return_date: Optional[str]`: Return date in YYYY-MM-DD format (e.g., "2025-07-25"). Set to `None` for one-way flights (default: None).
  - `adults: int`: Number of adult passengers (age 12+). Default: 2.
  - `students: int`: Number of student passengers (age 12+ with student fare eligibility). Default: 0.
  - `children: List[str]`: List of child passenger types: "11" (age 2-11), "1S" (toddler under 2 with seat), "1L" (infant under 2 on lap). Default: [].
  - `plane_type: str`: Cabin class: "economy", "premium", "business", or "first". Default: "economy".
  - `sort_option: str`: Sort order for results: "bestflight_a" (best flights), "price_a" (cheapest), "price_b" (most expensive), "duration_a" (quickest), "duration_b" (slowest), "depart_a" (earliest takeoff), "depart_b" (latest takeoff), "arrive_a" (earliest landing), "arrive_b" (latest landing), "departReturn_a" (earliest return takeoff), "departReturn_b" (latest return takeoff), "arriveReturn_a" (earliest return landing), "arriveReturn_b" (latest return landing). Default: "price_a".
  - `carry_on_free: Optional[int]`: Minimum number of free carry-on bags. Set to `None` for no preference. Default: 1.
  - `checked_bags_free: Optional[int]`: Minimum number of free checked bags. Set to `None` for no preference. Default: None.
  - `stops: Optional[int]`: Maximum number of stops (0 for direct flights). Set to `None` for no preference. Default: None.
  - `max_price: Optional[int]`: Maximum price in CAD. Set to `None` for no price limit. Default: 6000.
  - `alliance: Optional[str]`: Airline alliance: "VALUE_ALLIANCE", "ONE_WORLD", "SKY_TEAM", "STAR_ALLIANCE". Set to `None` for no preference. Default: None.
  - `include_airlines: Optional[Set[str]]`: Set of 2-letter IATA airline codes to include (e.g., {"AC", "UA"}). Set to `None` for no inclusion filter. Default: None.
  - `exclude_airlines: Optional[Set[str]]`: Set of 2-letter IATA airline codes to exclude (e.g., {"NK", "F9"}). Set to `None` for no exclusion filter. Default: None.
  - `wifi_only: bool`: If `True`, only include flights with Wi-Fi available. Default: False.
  - `start_index: int`: Starting index of flight results to return (0-based, inclusive). Default: 0.
  - `end_index: int`: Ending index of flight results to return (inclusive). Must be >= `start_index`. Default: 15.
- **Returns**: A string summarizing flight results, with each flight separated by "---". Each flight includes:
  - Price (in CAD).
  - Outbound and return (if applicable) flight details: departure/arrival times, airports, airlines, duration, and stops.
  - Stop details (if any): airport codes, names, and layover durations.
  - Baggage: Number of free carry-on and checked bags.
  - Fare types and available booking sites.
  - Booking link.
  - Total results count and any additional notes.
  If no flights are found or an error occurs, returns an error message with the total results count (e.g., "No flights found: No flight results found\nTotal results: 0").

## Manual Configuration
To set up the Flight Scraper MCP Server locally:
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   ```
2. **Set Up UV**:
   Install UV (a Python package and project manager). Follow the official UV documentation for installation instructions.
3. **Install Dependencies**:
   Install required Python packages using UV:
   ```bash
   uv pip install requests beautifulsoup4 httpx
   ```
4. **Configure MCP Client**:
   Add the following to your MCP client configuration (e.g., Claude Desktop):
   ```json
   "flight-search-mcp": {
       "command": "uv",
       "args": [
           "--directory",
           "YOUR_CLONED_FOLDER",
           "run",
           "main.py"
       ]
   }
   ```
   Replace `YOUR_CLONED_FOLDER` with the path to the cloned repository.

## Remote MCP Server Configuration
The Flight Scraper MCP Server is hosted remotely at [https://smithery.ai/server/@alan5543/flight-scraper](https://smithery.ai/server/@alan5543/flight-scraper). To use it:
1. Visit [https://smithery.ai](https://smithery.ai) and sign in or create an account.
2. Go to the server page: [https://smithery.ai/server/@alan5543/flight-scraper](https://smithery.ai/server/@alan5543/flight-scraper).
3. Click "Add to Client" or follow Smithery.ai's integration instructions.
4. Update your MCP client (e.g., Claude Desktop) to use the remote server URL. Check your client's documentation for details on configuring remote MCP servers.
5. Test the connection to confirm the server is accessible and working.