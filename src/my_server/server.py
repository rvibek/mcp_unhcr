#!/usr/bin/env python3
"""
UNHCR Population Data MCP Server

This MCP server provides access to various UNHCR endpoints through the Model Context Protocol.
It allows querying data around forcibly displaced persons by country of origin, country of asylum, and year(s), as well as provide data on Refugee Status Determination (RSD) Applications and Refugee Status Determination (RSD) decisions

API Endpoint: https://api.unhcr.org/population/v1/
"""

import logging
from typing import Any, Dict, Optional, Union

import requests
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from smithery.decorators import smithery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigSchema(BaseModel):
    pass

@smithery.server(config_schema=ConfigSchema)
def create_server():
    """Create and return a FastMCP server instance."""

    server = FastMCP(name="UNHCR API Data")

    def fetch_unhcr_api_data(endpoint: str,
                             coo: Optional[str] = None,
                             coa: Optional[str] = None,
                             year: Optional[Union[str, int]] = None,
                             coo_all: bool = False,
                             coa_all: bool = False,
                             pop_type: bool = False) -> Dict[str, Any]:
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
        
        if pop_type:
            params["pop_type"] = "true"
            
        if year is None:
            params["year[]"] = "2025"
        else:
            year_str = str(year)
            if "," in year_str:
                years = [y.strip() for y in year_str.split(",")]
                params["year[]"] = years
            else:
                params["year[]"] = year_str
        
        base_url = "https://api.unhcr.org/population/v1"
        url = f"{base_url}/{endpoint}/"
        
        try:
            logger.info(f"Fetching UNHCR {endpoint} data with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching UNHCR {endpoint} data: {e}")
            return {"error": str(e), "status": "error"}

    @server.tool()
    def get_population_data(coo: Optional[str] = None, 
                            coa: Optional[str] = None, 
                            year: Optional[Union[str, int]] = None,
                            coo_all: bool = False,
                            coa_all: bool = False) -> Dict[str, Any]:
        """
        Get forcibly displaced population data from UNHCR.
        
        Args:
            coo: Country of origin (ISO3 code) - Use for questions about forcibly displaced populations FROM a specific country
            coa: Country of asylum (ISO3 code) - Use for questions about forcibly displaced populations IN a specific country
            year: Year to filter by (defaults to 2025)
            coo_all: Set to True when breaking down results by ORIGIN country
            coa_all: Set to True when breaking down results by ASYLUM country
        """
        return fetch_unhcr_api_data("population", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)
    

    @server.tool()
    def get_demographics_data(coo: Optional[str] = None, 
                            coa: Optional[str] = None, 
                            year: Optional[Union[str, int]] = None,
                            coo_all: bool = False,
                            coa_all: bool = False,
                            pop_type: bool = False) -> Dict[str, Any]:
        """
        Get forcibly displaced populations demographics data from UNHCR. It shows breakdown by age and sex when available.
        
        Args:
            coo: Country of origin (ISO3 code) - Use for questions about forcibly displaced populations FROM a specific country
            coa: Country of asylum (ISO3 code) - Use for questions about forcibly displaced populations IN a specific country
            year: Year to filter by (defaults to 2025)
            coo_all: Set to True when breaking down results by ORIGIN country
            coa_all: Set to True when breaking down results by ASYLUM country
            pop_type: Set to True when asked about specific population types (e.g., refugees, asylum seekers, stateless persons)
        """
        return fetch_unhcr_api_data("demographics", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all, pop_type=pop_type)
    


    @server.tool()
    def get_rsd_applications(coo: Optional[str] = None, 
                            coa: Optional[str] = None, 
                            year: Optional[Union[str, int]] = None,
                            coo_all: bool = False,
                            coa_all: bool = False,) -> Dict[str, Any]:
        
        """
        Get RSD application data from UNHCR.
        
        Args:
            coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            year: Year filter (comma-separated for multiple years) - defaults to 2024
            coo_all: Set to True when analyzing the ORIGIN COUNTRIES of asylum seekers
            coa_all: Set to True when analyzing the ASYLUM COUNTRIES where applications were filed
        """
        return fetch_unhcr_api_data("asylum-applications", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    @server.tool()
    def get_rsd_decisions(coo: Optional[str] = None, 
                         coa: Optional[str] = None, 
                         year: Optional[Union[str, int]] = None,
                         coo_all: bool = False,
                         coa_all: bool = False) -> Dict[str, Any]:
        """
        Get Refugee Status Determination (RSD) decision data from UNHCR.
        
        Args:
            coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            year: Year filter (comma-separated for multiple years) - defaults to 2025
            coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY
            coa_all: Set to True when analyzing decisions breakdown BY COUNTRY
        """
        return fetch_unhcr_api_data("asylum-decisions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    @server.tool()
    def get_solutions(coo: Optional[str] = None, 
                         coa: Optional[str] = None, 
                         year: Optional[Union[str, int]] = None,
                         coo_all: bool = False,
                         coa_all: bool = False) -> Dict[str, Any]:
        """
        Get figures on durable solutions from UNHCR which includes refugee returnees (returned_refugees), resettlement, naturalisation, retuned IDPs (returned_idps)
        
        Args:
            coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            year: Year filter (comma-separated for multiple years) - defaults to 2025
            coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY
            coa_all: Set to True when analyzing decisions breakdown BY COUNTRY
        """
        return fetch_unhcr_api_data("solutions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    return server
