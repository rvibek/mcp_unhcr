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
from typing import Any, Optional, Union

import requests
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
from smithery.decorators import smithery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ConfigSchema(BaseModel):
    """Configuration schema for Smithery."""
    debug_mode: bool = Field(default=False, description="Enable debug logging")


class UNHCRAPIClient:
    """Client for UNHCR API."""
    
    BASE_URL = "https://api.unhcr.org/population/v1"

    def _fetch(self, endpoint: str,
             coo: Optional[str] = None,
             coa: Optional[str] = None,
             year: Optional[Union[str, int]] = None,
             coo_all: bool = False,
             coa_all: bool = False,
             pop_type: Optional[bool] = None) -> dict[str, Any]:
        """
        Generic function to fetch data from various UNHCR API endpoints.
        """
        params = {"cf_type": "ISO"}
        
        if coo:
            params["coo"] = coo
        if coa:
            params["coa"] = coa
        if coo_all:
            params["coo_all"] = "true"
        if coa_all:
            params["coa_all"] = "true"
        
        if pop_type is True:
            params["pop_type"] = "true"            
        
        if year is None:
            # Default to 2025 as per previous implementation logic
            params["year[]"] = "2025"
        else:
            year_str = str(year)
            if "," in year_str:
                years = [y.strip() for y in year_str.split(",")]
                params["year[]"] = years
            else:
                params["year[]"] = year_str
        
        url = f"{self.BASE_URL}/{endpoint}/"
        
        try:
            logger.info(f"Fetching UNHCR {endpoint} data with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching UNHCR {endpoint} data: {e}")
            return {"error": str(e), "status": "error"}

    def get_population(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                      year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                      coa_all: bool = False) -> dict[str, Any]:
        return self._fetch("population", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    def get_demographics(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                         year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                         coa_all: bool = False, pop_type: bool = False) -> dict[str, Any]:
        return self._fetch("demographics", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all, pop_type=pop_type)

    def get_asylum_applications(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                               year: Optional[Union[str, int]] = None,
                               coo_all: bool = False, coa_all: bool = False) -> dict[str, Any]:
        return self._fetch("asylum-applications", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    def get_asylum_decisions(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                            year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                            coa_all: bool = False) -> dict[str, Any]:
        return self._fetch("asylum-decisions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    def get_solutions(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                      year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                      coa_all: bool = False) -> dict[str, Any]:
        return self._fetch("solutions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)


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
