#!/usr/bin/env python3
"""
UNHCR Population Data MCP Server

This MCP server provides access to various UNHCR endpoints through the Model Context Protocol.
It allows querying data around forcibly displaced persons by country of origin, country of asylum, and year(s), as well as provide data on Refugee Status Determination (RSD) Applications and Refugee Status Determination (RSD) decisions

API Endpoint: https://api.unhcr.org/population/v1/
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import requests
from mcp.server.fastmcp import Context, FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("UNHCR API Data")

def fetch_unhcr_api_data(endpoint: str,
                         coo: Optional[str] = None,
                         coa: Optional[str] = None,
                         year: Optional[Union[str, int]] = None,
                         coo_all: bool = False) -> Dict[str, Any]:
    """
    Generic function to fetch data from various UNHCR API endpoints.
    
    Args:
        endpoint: API endpoint name ("population", "asylum-applications", or "asylum-decisions")
        coo: Country of origin (ISO3 code, comma-separated for multiple)
        coa: Country of asylum (ISO3 code, comma-separated for multiple)
        year: Year(s) to filter by (comma-separated for multiple years), defaults to 2024 if not provided
        coo_all: If True, break down results by all countries of origin
        
    Returns:
        Dict containing the API response
    """
    params = {"cf_type": "ISO"}
    
    if coo:
        params["coo"] = coo
    if coa:
        params["coa"] = coa
    if coo_all:
        params["coo_all"] = "true"  # API expects a string "true", not a boolean
        
    # Handle the year parameter
    if year is None:
        params["year[]"] = "2024"  # Default to 2024
    else:
        # Convert year to string and split by comma if multiple years are provided
        year_str = str(year)
        if "," in year_str:
            years = [y.strip() for y in year_str.split(",")]
            params["year[]"] = years  # Pass as a list for multiple years
        else:
            params["year[]"] = year_str  # Single year as a string
    
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


# Now update the MCP tool functions to include the coo_all parameter:

@mcp.tool()
def get_population_data(coo: Optional[str] = None, 
                        coa: Optional[str] = None, 
                        year: Optional[Union[str, int]] = None,
                        coo_all: bool = False) -> Dict[str, Any]:
    """
    Get population data from UNHCR.
    
    Args:
        coo: Country of origin filter (ISO3 code, comma-separated for multiple)
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
        year: Year filter (comma-separated for multiple years)
        coo_all: If True, break down results by all countries of origin
        
    Returns:
        Population data from UNHCR
    """
    return fetch_unhcr_api_data("population", coo=coo, coa=coa, year=year, coo_all=coo_all)


@mcp.tool()
def get_rsd_applications(coo: Optional[str] = None, 
                        coa: Optional[str] = None, 
                        year: Optional[Union[str, int]] = None,
                        coo_all: bool = False) -> Dict[str, Any]:
    """
    Get RSD application data from UNHCR.
    
    Args:
        coo: Country of origin filter (ISO3 code, comma-separated for multiple)
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
        year: Year filter (comma-separated for multiple years)
        coo_all: If True, break down results by all countries of origin
        
    Returns:
        UNHCR RSD Applications data in a country of asylum
    """
    return fetch_unhcr_api_data("asylum-applications", coo=coo, coa=coa, year=year, coo_all=coo_all)


@mcp.tool()
def get_rsd_decisions(coo: Optional[str] = None, 
                     coa: Optional[str] = None, 
                     year: Optional[Union[str, int]] = None,
                     coo_all: bool = False) -> Dict[str, Any]:
    """
    Get RSD decision data from UNHCR.
    
    Args:
        coo: Country of origin filter (ISO3 code, comma-separated for multiple)
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
        year: Year filter (comma-separated for multiple years)
        coo_all: If True, break down results by all countries of origin
        
    Returns:
        UNHCR RSD Decisions data in a country of asylum
    """
    return fetch_unhcr_api_data("asylum-decisions", coo=coo, coa=coa, year=year, coo_all=coo_all)


if __name__ == "__main__":
    # Run the server
    print("MCP server running in development mode. Press Ctrl+C to stop.")
    mcp.run()
