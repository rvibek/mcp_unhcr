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
                         coo_all: bool = False,
                         coa_all: bool = False) -> Dict[str, Any]:
    """
    Generic function to fetch data from various UNHCR API endpoints.
    
    Args:
        endpoint: API endpoint name to query. Options:
            - "population" - For refugee population statistics
            - "asylum-applications" - For RSD application statistics
            - "asylum-decisions" - For RSD decision outcomes
        
        coo: Country of origin filter (ISO3 code, comma-separated for multiple)
            Example: "KEN" for Kenya, "TIB,SOM,ETH" for Tibet, Somalia and Ethiopia
        
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
            Example: "UGA" for Uganda, "KEN,TZA" for Kenya and Tanzania
        
        year: Year filter (comma-separated for multiple years), defaults to 2024 if not provided
            Example: "2024" or "2022,2023,2024"
        
        coo_all: Set to True when requesting data breakdown by countries of origin
            - This parameter tells the API to return data for ALL countries of origin
            - Critical for analyzing which nationalities are present in a given asylum country
        
        coa_all: Set to True when requesting data breakdown by countries of asylum
            - This parameter tells the API to return data for ALL countries of asylum
            - Critical for analyzing which countries are hosting refugees from a given origin
        
        Technical details:
        - The API expects string "true" values for boolean parameters
        - Year is passed as "year[]" parameter to the API
        - Multiple years require array-style parameter formatting
        
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
    if coa_all:
        params["coa_all"] = "true"  # API expects a string "true", not a boolean
        
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
                        coo_all: bool = False,
                        coa_all: bool = False) -> Dict[str, Any]:
    """
    Get refugee population data from UNHCR.
    
    Args:
        coo: Country of origin (ISO3 code) - Use for questions about refugees FROM a specific country
        coa: Country of asylum (ISO3 code) - Use for questions about refugees IN a specific country
        year: Year to filter by (defaults to 2024)
        coo_all: Set to True when breaking down results by ORIGIN country
        coa_all: Set to True when breaking down results by ASYLUM country
    
    Important:
        - For "Where are refugees from COUNTRY living?" use coo="COUNTRY" and coa_all=True
        - For "How many refugees are living in COUNTRY?" use coa="COUNTRY"
        - For "What countries do refugees in COUNTRY come from?" use coa="COUNTRY" and coo_all=True
        
    Returns:
        Population data from UNHCR
    """
    return fetch_unhcr_api_data("population", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)


@mcp.tool()
def get_rsd_applications(coo: Optional[str] = None, 
                        coa: Optional[str] = None, 
                        year: Optional[Union[str, int]] = None,
                        coo_all: bool = False,
                        coa_all: bool = False) -> Dict[str, Any]:
    """
    Get RSD application data from UNHCR.
    
    Args:
        coo: Country of origin filter (ISO3 code, comma-separated for multiple) - Use for questions about asylum seekers FROM a specific country
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple) - Use for questions about asylum applications IN a specific country
        year: Year filter (comma-separated for multiple years) - defaults to 2024 if not provided
        coo_all:  Set to True when analyzing the ORIGIN COUNTRIES of asylum seekers
            - Use when answering: "Which nationalities applied for asylum in Germany?"
        coa_all: Set to True when analyzing the ASYLUM COUNTRIES where applications were filed
            - Use when answering: "Where did Syrians apply for asylum?" (breakdown by country)
            - Do NOT use when answering: "How many asylum applications were filed in Germany?"
        
        Important query patterns:
        - "How many [nationality] people applied for asylum in [country]?"
            → Use coo="[nationality code]" and coa="[country code]"
        
        - "Where did [nationality] people apply for asylum?"
            → Use coo="[nationality code]" and coa_all=True
        
        - "Who applied for asylum in [country]?"
            → Use coa="[country code]" and coo_all=True
        
        - "How many asylum applications were there in [year]?"
            → Use year="[year]" with appropriate coo/coa filters if needed
        
    Returns:
        UNHCR RSD Applications data in a country of asylum
    """
    return fetch_unhcr_api_data("asylum-applications", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)


@mcp.tool()
def get_rsd_decisions(coo: Optional[str] = None, 
                     coa: Optional[str] = None, 
                     year: Optional[Union[str, int]] = None,
                     coo_all: bool = False,
                     coa_all: bool = False) -> Dict[str, Any]:
    """
    Get Refugee Status Determination (RSD) decision data from UNHCR.
    
    Args:
        coo: Country of origin filter (ISO3 code, comma-separated for multiple) - Use for questions about asylum decisions FOR people FROM a specific country
             Example: "SYR" for Syria, "AFG,IRQ" for Afghanistan and Iraq
        
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple) - Use for questions about asylum decisions MADE IN a specific country
             Example: "DEU" for Germany, "FRA,ITA" for France and Italy
        
        year: Year filter (comma-separated for multiple years) - defaults to 2024 if not provided
             Example: "2023" or "2022,2023,2024" for multiple years
        
        coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY of asylum seekers
            - Use when answering: "Which nationalities received asylum decisions in Germany?"
            - Use when answering: "What was the approval rate for different nationalities in France?"
        
        coa_all: Set to True when analyzing decisions breakdown BY COUNTRY where decisions were made
            - Use when answering: "Where did Syrians receive asylum decisions?" (breakdown by country)
            - Use when answering: "Which countries approved/rejected the most Eritrean asylum claims?"
        
    Important query patterns:
        - "How many [nationality] people were granted/rejected asylum in [country]?"
            → Use coo="[nationality code]" and coa="[country code]"
        
        - "Where did [nationality] people receive positive/negative asylum decisions?"
            → Use coo="[nationality code]" and coa_all=True
        
        - "What was the asylum approval rate for different nationalities in [country]?"
            → Use coa="[country code]" and coo_all=True
        
        - "How many asylum decisions were made in [year]?"
            → Use year="[year]" with appropriate coo/coa filters if needed
        
        - "What was the recognition rate for [nationality] refugees in [country]?"
            → Use coo="[nationality code]" and coa="[country code]"
        
    Returns:
        UNHCR RSD Decision data including counts of recognized, rejected, and otherwise closed cases
        with statistics on recognition rates and processing efficiency
    """
    return fetch_unhcr_api_data("asylum-decisions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)


if __name__ == "__main__":
    # Run the server
    print("MCP server running. Press Ctrl+C to stop.")
    mcp.run()
