#!/usr/bin/env python3
"""
UNHCR Forcibly Displaced Populations MCP Server

This MCP server provides access to various UNHCR endpoints through the Model Context Protocol.
It allows querying data around forcibly displaced persons by country of origin, country of asylum,
and year(s), as well as provide data on Refugee Status Determination (RSD) Applications and
Refugee Status Determination (RSD) decisions.

API Endpoint: https://api.unhcr.org/population/v1/
"""

import logging
import os
from typing import Any
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from smithery.decorators import smithery

from unhcr_mcp.api_client import UNHCRAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ConfigSchema(BaseModel):
    """Configuration schema for Smithery."""
    pass


@smithery.server(config_schema=ConfigSchema)
def create_server() -> FastMCP:
    """
    Create and return a FastMCP server instance.

    Returns:
        Configured FastMCP server
    """
    # Set environment variable to allow any host header
    os.environ["ALLOWED_HOSTS"] = "*"

    # Initialize the server
    server = FastMCP(name="UNHCR API Data")

    # Initialize API client
    api_client = UNHCRAPIClient()

    @server.tool()
    def get_population_data(
        coo: str | None = None,
        coa: str | None = None,
        year: str | int | None = None,
        coo_all: bool = False,
        coa_all: bool = False,
    ) -> dict[str, Any]:
        """
        Get forcibly displaced populations like refugees, asylum seekers, stateless persons data from UNHCR.

        Args:
            coo: Country of origin (ISO3 code) - Use for questions about refugees FROM a specific country
            coa: Country of asylum (ISO3 code) - Use for questions about refugees IN a specific country
            year: Year to filter by (defaults to 2025)
            coo_all: Set to True when breaking down results by ORIGIN country
            coa_all: Set to True when breaking down results by ASYLUM country

        Returns:
            Population data from UNHCR API
        """
        return api_client.get_population(
            coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all
        )

    @server.tool()
    def get_demographics_data(
        coo: str | None = None,
        coa: str | None = None,
        year: str | int | None = None,
        coo_all: bool = False,
        coa_all: bool = False,
        pop_type: bool = False,
    ) -> dict[str, Any]:
        """
        Get forcibly displaced populations demographics data from UNHCR. It shows breakdown by age and sex when available.

        Args:
            coo: Country of origin (ISO3 code) - Use for questions about forcibly displaced populations FROM a specific country
            coa: Country of asylum (ISO3 code) - Use for questions about forcibly displaced populations IN a specific country
            year: Year to filter by (defaults to 2025)
            coo_all: Set to True when breaking down results by ORIGIN country
            coa_all: Set to True when breaking down results by ASYLUM country
            pop_type: Set to True when asked about specific population types (e.g., refugees, asylum seekers, stateless persons)

        Returns:
            Demographics data from UNHCR API
        """
        return api_client.get_demographics(
            coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all, pop_type=pop_type
        )

    @server.tool()
    def get_rsd_applications(
        coo: str | None = None,
        coa: str | None = None,
        year: str | int | None = None,
        coo_all: bool = False,
        coa_all: bool = False,
    ) -> dict[str, Any]:
        """
        Get RSD application data from UNHCR.

        Args:
            coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            year: Year filter (comma-separated for multiple years) - defaults to 2025
            coo_all: Set to True when analyzing the ORIGIN COUNTRIES of asylum seekers
            coa_all: Set to True when analyzing the ASYLUM COUNTRIES where applications were filed

        Returns:
            RSD application data from UNHCR API
        """
        return api_client.get_asylum_applications(
            coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all
        )

    @server.tool()
    def get_rsd_decisions(
        coo: str | None = None,
        coa: str | None = None,
        year: str | int | None = None,
        coo_all: bool = False,
        coa_all: bool = False,
    ) -> dict[str, Any]:
        """
        Get Refugee Status Determination (RSD) decision data from UNHCR.

        Args:
            coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            year: Year filter (comma-separated for multiple years) - defaults to 2025
            coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY
            coa_all: Set to True when analyzing decisions breakdown BY COUNTRY

        Returns:
            RSD decision data from UNHCR API
        """
        return api_client.get_asylum_decisions(
            coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all
        )

    @server.tool()
    def get_solutions(
        coo: str | None = None,
        coa: str | None = None,
        year: str | int | None = None,
        coo_all: bool = False,
        coa_all: bool = False,
    ) -> dict[str, Any]:
        """
        Get figures on durable solutions from UNHCR which includes refugee returnees (returned_refugees), resettlement, naturalisation, retuned IDPs (returned_idps)

        Args:
            coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            year: Year filter (comma-separated for multiple years) - defaults to 2025
            coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY
            coa_all: Set to True when analyzing decisions breakdown BY COUNTRY

        Returns:
            Solutions data from UNHCR API
        """
        return api_client.get_solutions(
            coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all
        )

    return server


def main() -> None:
    """
    Main entry point for the MCP server.
    """
    logger.info("Starting UNHCR MCP Server")
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()

