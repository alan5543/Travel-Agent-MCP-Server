# --- MCP Server Configuration ---
mcp_server_configs = [
        # {
        #     "name": "travel_server",
        #     "command": "python",
        #     "args": ["../airbnb_mcp_server/main.py"],
        #     "env": None,
        # },
        {
            "name": "airbnb_mcp_server",
            "command": "uv",
            "args": ["run","../airbnb_mcp_server/main.py"],
            "env": None,
        },
        {
            "name": "flight_server",
            "command": "python",
            "args": ["../flight_mcp_server/main.py"],
            "env": None,
        },
        {
            "name": "serp_server",
            "command": "python",
            "args": ["../serp_mcp_server/main.py"],
            "env": {
                "SERPAPI_KEY": "1c283f5976c4f462d92d6ff81463a50f9614b8d05702c33dfad5549bb2beab2a",
                "CURRENCYFREAKS_API_KEY": "5eac297d6e8144bf940f38a6a038e502"
            },
        },
        {
            "name": "fetch_server",
            "command": "uvx",
            "args": ["mcp-server-fetch", "--user-agent=TravelBuddyBot/1.0"],
            "env": None,
        },
                {
            "name": "wikipedia-mcp",
            "command": "uvx",
            "args": ["wikipedia-mcp"],
            "env": None,
        },
        {
        "name": "sequential_thinking",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "env": None
    }
    ]