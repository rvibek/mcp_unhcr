#!/usr/bin/env python3
"""
UNHCR forcibly displaced populations Data MCP Server
"""
import logging
import os
from typing import Any, Dict, Optional, Union

import requests
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from smithery.decorators import smithery

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigSchema(BaseModel):
    enabled: bool = True


@smithery.server(config_schema=ConfigSchema)
def create_server(config: ConfigSchema):
    server = FastMCP(name="UNHCR API Data")

    def fetch_unhcr_api_data(
        endpoint: str,
        coo: Optional[str] = None,
        coa: Optional[str] = None,
        year: Optional[Union[str, int]] = None,
        coo_all: bool = False,
        coa_all: bool = False,
        pop_type: Optional[bool] = None
    ) -> Dict[str, Any]:
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

        if year is not None:
            year_str = str(year)
            if "," in year_str:
                params["year[]"] = [y.strip() for y in year_str.split(",")]
            else:
                params["year[]"] = year_str

        url = f"https://api.unhcr.org/population/v1/{endpoint}/"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"UNHCR API unavailable: {e}")
            return {"data": [], "warning": "UNHCR API unavailable"}

    @server.tool()
    def get_population_data(
        coo: Optional[str] = None,
        coa: Optional[str] = None,
        year: Optional[Union[str, int]] = None,
        coo_all: bool = False,
        coa_all: bool = False
    ) -> Dict[str, Any]:
        return fetch_unhcr_api_data(
            "population",
            coo=coo,
            coa=coa,
            year=year,
            coo_all=coo_all,
            coa_all=coa_all
        )

    return server


if __name__ == "__main__":
    server = create_server(ConfigSchema())
    server.run(host="0.0.0.0", port=int(os.getenv("PORT", "3333")))
