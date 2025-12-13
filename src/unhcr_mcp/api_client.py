import logging
from typing import Any, Dict, Optional, Union
import requests

logger = logging.getLogger(__name__)

class UNHCRAPIClient:
    """Client for UNHCR API."""
    
    BASE_URL = "https://api.unhcr.org/population/v1"

    def _fetch(self, endpoint: str,
             coo: Optional[str] = None,
             coa: Optional[str] = None,
             year: Optional[Union[str, int]] = None,
             coo_all: bool = False,
             coa_all: bool = False,
             pop_type: Optional[bool] = None) -> Dict[str, Any]:
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
                      coa_all: bool = False) -> Dict[str, Any]:
        return self._fetch("population", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    def get_demographics(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                         year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                         coa_all: bool = False, pop_type: bool = False) -> Dict[str, Any]:
        return self._fetch("demographics", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all, pop_type=pop_type)

    def get_asylum_applications(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                               year: Optional[Union[str, int]] = None,
                               coo_all: bool = False, coa_all: bool = False) -> Dict[str, Any]:
        return self._fetch("asylum-applications", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    def get_asylum_decisions(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                            year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                            coa_all: bool = False) -> Dict[str, Any]:
        return self._fetch("asylum-decisions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

    def get_solutions(self, coo: Optional[str] = None, coa: Optional[str] = None, 
                      year: Optional[Union[str, int]] = None, coo_all: bool = False, 
                      coa_all: bool = False) -> Dict[str, Any]:
        return self._fetch("solutions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)
