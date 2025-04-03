# UNHCR Population Data MCP Server

This MCP (Model Context Protocol) server provides access to UNHCR population data through a standardized interface. It allows AI agents to query refugee statistics by country of origin, country of asylum, and year.

## Features

- Query population data with flexible filtering by country of origin, country of asylum, and year
- Get refugee counts for specific countries of origin
- Get asylum statistics for countries hosting refugees
- Access country profiles with both origin and asylum statistics
- View global refugee statistics by year

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or another Python package manager

### Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd unhcr-mcp-server
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running Locally

To run the server locally in development mode:

```bash
python app.py
```

This will start the MCP server in development mode, allowing you to interact with it using the MCP Inspector or other MCP clients.

### Deploying to Smithery.ai

This server is configured for deployment on [Smithery.ai](https://smithery.ai/), a platform for hosting MCP servers.

1. Add your server to Smithery (or claim it if it's already listed)
2. Click Deploy on the Smithery Deployments tab on your server page

## API Endpoint

This server interacts with the UNHCR Population API:

```
https://api.unhcr.org/population/v1/population/
```

### Query Parameters

- `cf_type`: Always set to "ISO"
- `coo`: Country of origin filter (ISO 3-letter country codes, comma-separated for multiple)
- `coa`: Country of asylum filter (ISO 3-letter country codes, comma-separated for multiple)
- `year`: Year filter (comma-separated for multiple years)

## MCP Tools

### `get_population_data`

Get raw population data from UNHCR with optional filtering.

**Parameters:**
- `coo` (optional): Country of origin filter (ISO 3-letter code, comma-separated for multiple)
- `coa` (optional): Country of asylum filter (ISO 3-letter code, comma-separated for multiple)
- `year` (optional): Year filter (comma-separated for multiple years)

### `get_refugee_count`

Get refugee count for a specific country of origin.

**Parameters:**
- `coo`: Country of origin (ISO 3-letter code)
- `coa` (optional): Country of asylum filter (ISO 3-letter code)
- `year` (optional): Year filter

### `get_asylum_stats`

Get asylum statistics for a specific country of asylum.

**Parameters:**
- `coa`: Country of asylum (ISO 3-letter code)
- `year` (optional): Year filter

## MCP Resources

### `unhcr://countries`

Get a list of countries with their ISO codes.

### `unhcr://stats/{year}`

Get global refugee statistics for a specific year.

**Parameters:**
- `year`: The year to get statistics for

### `unhcr://country/{country_code}`

Get a profile for a specific country, showing both origin and asylum statistics.

**Parameters:**
- `country_code`: ISO 3-letter country code

## License

MIT

## Acknowledgments

This project uses data from the [UNHCR Refugee Population Statistics Database](https://www.unhcr.org/refugee-statistics/).
