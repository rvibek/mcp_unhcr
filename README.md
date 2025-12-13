# UNHCR Refugee Statistics

## Description
This MCP (Model Context Protocol) server provides access to UNHCR data through a standardized interface. It allows AI agents to query data related to forcibly displaced persons, including population statistics, Refugee Status Determination (RSD) applications, and RSD decisions. The data can be filtered by country of origin, country of asylum, and year(s).

## Features
- **Population Data**: Get statistics on refugees, asylum seekers, and stateless persons.
- **Demographics**: Breakdown by age and sex.
- **RSD Applications**: Query asylum applications data.
- **RSD Decisions**: Query refugee status determination decisions.
- **Solutions**: Data on resettlement, naturalization, and returns.

## Usage
This server is designed to be used with MCP clients (like Claude Desktop, Smithery, etc.).

### Tools
- `get_population_data`
- `get_demographics_data`
- `get_rsd_applications`
- `get_rsd_decisions`
- `get_solutions`

## License
MIT
