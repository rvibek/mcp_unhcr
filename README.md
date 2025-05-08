# UNHCR Population Data MCP Server

This MCP (Model Context Protocol) server provides access to UNHCR data through a standardized interface. It allows AI agents to query data related to forcibly displaced persons, including population statistics, Refugee Status Determination (RSD) applications, and RSD decisions. The data can be filtered by country of origin, country of asylum, and year(s).

This server interacts with the [UNHCR Population Statistics APIs](https://api.unhcr.org/).

## Features

- Query forcibly displaced population data.
- Query Refugee Status Determination (RSD) application data.
- Query Refugee Status Determination (RSD) decision data.
- Filter data by country of origin (ISO3 code), country of asylum (ISO3 code), and year(s).
- Option to break down results by all countries of origin and countries of asylum

## Connect to MCP Server

To access the server, open your web browser and visit the following URL:
[https://smithery.ai/server/@rvibek/mcp_unhcr](https://smithery.ai/server/@rvibek/mcp_unhcr)

Configure the MCP host/client as needed.

[![smithery badge](https://smithery.ai/badge/@rvibek/mcp_unhcr)](https://smithery.ai/server/@rvibek/mcp_unhcr)

## API Endpoints and Query Parameters

The server fetches data from the following base URL: `https://api.unhcr.org/population/v1/` using these specific endpoints:
- `population/`
- `asylum-applications/`
- `asylum-decisions/`

Key query parameters used by the server when calling the UNHCR API:
- `cf_type`: Always set to "ISO".
- `coo`: Country of origin filter (ISO3 code, comma-separated for multiple).
- `coa`: Country of asylum filter (ISO3 code, comma-separated for multiple).
- `year[]`: Year(s) to filter by (e.g., "2023" or ["2022", "2023"]). Defaults to "2024" if not provided.
- `coo_all`: Set to "true" if results should be broken down by all countries of origin.
- `coa_all`: Set to "true" if results should be broken down by all countries of asylum.


## MCP Tools

The server exposes the following tools:

### `get_population_data`

Get population data from UNHCR.

**Parameters:**
- `coo` (optional): Country of origin filter (ISO3 code, comma-separated for multiple).
- `coa` (optional): Country of asylum filter (ISO3 code, comma-separated for multiple).
- `year` (optional): Year filter (comma-separated for multiple years, or a single year). Defaults to 2024 if not provided.
- `coo_all` (optional, boolean): If `True`, break down results by all countries of origin. Defaults to `False`.
- `coa_all` (optional, boolean): If `True`, break down results by all countries of asylum. Defaults to `False`.

### `get_rsd_applications`

Get RSD application data from UNHCR.

**Parameters:**
- `coo` (optional): Country of origin filter (ISO3 code, comma-separated for multiple).
- `coa` (optional): Country of asylum filter (ISO3 code, comma-separated for multiple).
- `year` (optional): Year filter (comma-separated for multiple years, or a single year). Defaults to 2024 if not provided.
- `coo_all` (optional, boolean): If `True`, break down results by all countries of origin. Defaults to `False`.
- `coa_all` (optional, boolean): If `True`, break down results by all countries of asylum. Defaults to `False`.

### `get_rsd_decisions`

Get RSD decision data from UNHCR.

**Parameters:**
- `coo` (optional): Country of origin filter (ISO3 code, comma-separated for multiple).
- `coa` (optional): Country of asylum filter (ISO3 code, comma-separated for multiple).
- `year` (optional): Year filter (comma-separated for multiple years, or a single year). Defaults to 2024 if not provided.
- `coo_all` (optional, boolean): If `True`, break down results by all countries of origin. Defaults to `False`.
- `coa_all` (optional, boolean): If `True`, break down results by all countries of asylum. Defaults to `False`.



## To-do
- Add `year_from` and `year_to` parameter
- Include `nowcasting` endpoint
- Include `resettlement` endpoint


## License

MIT

## Acknowledgments

This project uses data from the [UNHCR Refugee Population Statistics Database](https://www.unhcr.org/refugee-statistics/).
