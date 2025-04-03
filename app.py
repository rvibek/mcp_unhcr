#!/usr/bin/env python3
"""
UNHCR Population Data MCP Server

This MCP server provides access to UNHCR population data through the Model Context Protocol.
It allows querying population statistics by country of origin, country of asylum, and year.

API Endpoint: https://api.unhcr.org/population/v1/population/
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlencode

from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("UNHCR Population Data")

# Base URL for the UNHCR API
UNHCR_API_BASE_URL = "https://api.unhcr.org/population/v1/population/"

def fetch_unhcr_data(coo: Optional[str] = None, 
                    coa: Optional[str] = None, 
                    year: Optional[Union[str, int]] = None) -> Dict[str, Any]:
    """
    Fetch data from the UNHCR Population API.
    
    Args:
        coo: Country of origin (ISO 3-letter code, comma-separated for multiple)
        coa: Country of asylum (ISO 3-letter code, comma-separated for multiple)
        year: Year(s) to filter by (comma-separated for multiple years)
        
    Returns:
        Dict containing the API response
    """
    params = {"cf_type": "ISO"}
    
    if coo:
        params["coo"] = coo
    if coa:
        params["coa"] = coa
    if year:
        params["year"] = str(year)
    
    url = UNHCR_API_BASE_URL
    
    try:
        logger.info(f"Fetching UNHCR data with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching UNHCR data: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool()
def get_population_data(coo: Optional[str] = None, 
                        coa: Optional[str] = None, 
                        year: Optional[Union[str, int]] = None) -> Dict[str, Any]:
    """
    Get population data from UNHCR.
    
    Args:
        coo: Country of origin filter (ISO 3-letter code, comma-separated for multiple)
        coa: Country of asylum filter (ISO 3-letter code, comma-separated for multiple)
        year: Year filter (comma-separated for multiple years)
        
    Returns:
        Population data from UNHCR
    """
    return fetch_unhcr_data(coo=coo, coa=coa, year=year)

@mcp.tool()
def get_refugee_count(coo: str, coa: Optional[str] = None, year: Optional[Union[str, int]] = None) -> Dict[str, Any]:
    """
    Get refugee count for specific country of origin.
    
    Args:
        coo: Country of origin (ISO 3-letter code)
        coa: Optional country of asylum filter (ISO 3-letter code)
        year: Optional year filter
        
    Returns:
        Refugee count data
    """
    data = fetch_unhcr_data(coo=coo, coa=coa, year=year)
    
    # Process the data to extract just the refugee counts
    if "items" in data and data["items"]:
        result = {
            "country_of_origin": coo,
            "total_refugees": 0,
            "by_year": {}
        }
        
        for item in data["items"]:
            year_val = item.get("year", "unknown")
            refugees = item.get("refugees", 0)
            
            result["total_refugees"] += refugees
            
            if year_val not in result["by_year"]:
                result["by_year"][year_val] = 0
            result["by_year"][year_val] += refugees
            
        return result
    else:
        return {"error": "No data found", "status": "error"}

@mcp.tool()
def get_asylum_stats(coa: str, year: Optional[Union[str, int]] = None) -> Dict[str, Any]:
    """
    Get asylum statistics for a specific country of asylum.
    
    Args:
        coa: Country of asylum (ISO 3-letter code)
        year: Optional year filter
        
    Returns:
        Asylum statistics
    """
    data = fetch_unhcr_data(coa=coa, year=year)
    
    # Process the data to extract asylum statistics
    if "items" in data and data["items"]:
        result = {
            "country_of_asylum": coa,
            "total_refugees_hosted": 0,
            "countries_of_origin": {},
            "by_year": {}
        }
        
        for item in data["items"]:
            year_val = item.get("year", "unknown")
            refugees = item.get("refugees", 0)
            origin = item.get("coo_name", "Unknown")
            
            result["total_refugees_hosted"] += refugees
            
            # Track by country of origin
            if origin not in result["countries_of_origin"]:
                result["countries_of_origin"][origin] = 0
            result["countries_of_origin"][origin] += refugees
            
            # Track by year
            if year_val not in result["by_year"]:
                result["by_year"][year_val] = 0
            result["by_year"][year_val] += refugees
            
        return result
    else:
        return {"error": "No data found", "status": "error"}

@mcp.resource("unhcr://countries")
def get_countries() -> str:
    """
    Get a list of countries with their ISO codes.
    
    Returns:
        A formatted string with country information
    """
    # Make a request to get some data that will include country information
    data = fetch_unhcr_data(year="2022")
    
    countries = set()
    if "items" in data:
        for item in data["items"]:
            if "coo_name" in item and "coo" in item:
                countries.add((item["coo"], item["coo_name"]))
            if "coa_name" in item and "coa" in item:
                countries.add((item["coa"], item["coa_name"]))
    
    # Sort countries by name
    countries = sorted(list(countries), key=lambda x: x[1])
    
    # Format the output
    result = "# UNHCR Country Codes\n\n"
    result += "ISO Code | Country Name\n"
    result += "---------|-------------\n"
    
    for code, name in countries:
        result += f"{code} | {name}\n"
    
    return result

@mcp.resource("unhcr://stats/{year}")
def get_yearly_stats(year: str) -> str:
    """
    Get global refugee statistics for a specific year.
    
    Args:
        year: The year to get statistics for
        
    Returns:
        A formatted string with yearly statistics
    """
    data = fetch_unhcr_data(year=year)
    
    if "items" in data and data["items"]:
        total_refugees = sum(item.get("refugees", 0) for item in data["items"])
        total_asylum_seekers = sum(item.get("asylum_seekers", 0) for item in data["items"])
        total_idps = sum(item.get("idps", 0) for item in data["items"])
        
        # Get top countries of origin
        origin_counts = {}
        for item in data["items"]:
            origin = item.get("coo_name", "Unknown")
            refugees = item.get("refugees", 0)
            if origin not in origin_counts:
                origin_counts[origin] = 0
            origin_counts[origin] += refugees
        
        top_origins = sorted(origin_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get top countries of asylum
        asylum_counts = {}
        for item in data["items"]:
            asylum = item.get("coa_name", "Unknown")
            refugees = item.get("refugees", 0)
            if asylum not in asylum_counts:
                asylum_counts[asylum] = 0
            asylum_counts[asylum] += refugees
        
        top_asylums = sorted(asylum_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Format the output
        result = f"# Global Refugee Statistics for {year}\n\n"
        result += f"Total refugees: {total_refugees:,}\n"
        result += f"Total asylum seekers: {total_asylum_seekers:,}\n"
        result += f"Total internally displaced persons: {total_idps:,}\n\n"
        
        result += "## Top 10 Countries of Origin\n\n"
        result += "Country | Refugee Count\n"
        result += "--------|-------------\n"
        for country, count in top_origins:
            result += f"{country} | {count:,}\n"
        
        result += "\n## Top 10 Countries of Asylum\n\n"
        result += "Country | Refugee Count\n"
        result += "--------|-------------\n"
        for country, count in top_asylums:
            result += f"{country} | {count:,}\n"
        
        return result
    else:
        return f"No data available for year {year}"

@mcp.resource("unhcr://country/{country_code}")
def get_country_profile(country_code: str) -> str:
    """
    Get a profile for a specific country, showing both origin and asylum statistics.
    
    Args:
        country_code: ISO 3-letter country code
        
    Returns:
        A formatted string with country profile
    """
    # Get data as country of origin
    origin_data = fetch_unhcr_data(coo=country_code)
    
    # Get data as country of asylum
    asylum_data = fetch_unhcr_data(coa=country_code)
    
    country_name = "Unknown"
    
    # Try to get the country name
    if "items" in origin_data and origin_data["items"]:
        country_name = origin_data["items"][0].get("coo_name", "Unknown")
    elif "items" in asylum_data and asylum_data["items"]:
        country_name = asylum_data["items"][0].get("coa_name", "Unknown")
    
    result = f"# {country_name} ({country_code}) Refugee Profile\n\n"
    
    # Process origin data
    if "items" in origin_data and origin_data["items"]:
        total_refugees_origin = sum(item.get("refugees", 0) for item in origin_data["items"])
        
        # Get top countries of asylum for this origin
        asylum_counts = {}
        for item in origin_data["items"]:
            asylum = item.get("coa_name", "Unknown")
            refugees = item.get("refugees", 0)
            if asylum not in asylum_counts:
                asylum_counts[asylum] = 0
            asylum_counts[asylum] += refugees
        
        top_asylums = sorted(asylum_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        result += f"## Refugees from {country_name}\n\n"
        result += f"Total refugees: {total_refugees_origin:,}\n\n"
        
        result += "### Top 5 Countries of Asylum\n\n"
        result += "Country | Refugee Count\n"
        result += "--------|-------------\n"
        for country, count in top_asylums:
            result += f"{country} | {count:,}\n"
    else:
        result += f"## Refugees from {country_name}\n\n"
        result += "No data available\n\n"
    
    # Process asylum data
    if "items" in asylum_data and asylum_data["items"]:
        total_refugees_asylum = sum(item.get("refugees", 0) for item in asylum_data["items"])
        
        # Get top countries of origin for this asylum
        origin_counts = {}
        for item in asylum_data["items"]:
            origin = item.get("coo_name", "Unknown")
            refugees = item.get("refugees", 0)
            if origin not in origin_counts:
                origin_counts[origin] = 0
            origin_counts[origin] += refugees
        
        top_origins = sorted(origin_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        result += f"\n## Refugees in {country_name}\n\n"
        result += f"Total refugees hosted: {total_refugees_asylum:,}\n\n"
        
        result += "### Top 5 Countries of Origin\n\n"
        result += "Country | Refugee Count\n"
        result += "--------|-------------\n"
        for country, count in top_origins:
            result += f"{country} | {count:,}\n"
    else:
        result += f"\n## Refugees in {country_name}\n\n"
        result += "No data available\n"
    
    return result

if __name__ == "__main__":
    # Run the server in development mode
    mcp.run()
