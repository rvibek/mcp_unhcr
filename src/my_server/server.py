#!/usr/bin/env python3
"""
UNHCR Population Data MCP Server

This MCP server provides access to various UNHCR endpoints through the Model Context Protocol.
It allows querying data around forcibly displaced persons by country of origin, country of asylum, and year(s), as well as provide data on Refugee Status Determination (RSD) Applications and Refugee Status Determination (RSD) decisions

API Endpoint: https://api.unhcr.org/population/v1/
"""

import argparse
import inspect
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, Optional, Union

import requests
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from smithery.decorators import smithery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigSchema(BaseModel):
    pass

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
        
    if year is None:
        params["year[]"] = "2024"
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
        coo: Country of origin filter (ISO3 code, comma-separated for multiple)
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
        year: Year filter (comma-separated for multiple years) - defaults to 2024
        coo_all: Set to True when analyzing the ORIGIN COUNTRIES of asylum seekers
        coa_all: Set to True when analyzing the ASYLUM COUNTRIES where applications were filed
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
        coo: Country of origin filter (ISO3 code, comma-separated for multiple)
        coa: Country of asylum filter (ISO3 code, comma-separated for multiple)
        year: Year filter (comma-separated for multiple years) - defaults to 2024
        coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY
        coa_all: Set to True when analyzing decisions breakdown BY COUNTRY
    """
    return fetch_unhcr_api_data("asylum-decisions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

@mcp.tool()
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
        year: Year filter (comma-separated for multiple years) - defaults to 2024
        coo_all: Set to True when analyzing decisions breakdown BY NATIONALITY
        coa_all: Set to True when analyzing decisions breakdown BY COUNTRY
    """
    return fetch_unhcr_api_data("solutions", coo=coo, coa=coa, year=year, coo_all=coo_all, coa_all=coa_all)

@smithery.server(config_schema=ConfigSchema)
def create_server():
    """Create and return a FastMCP server instance."""
    return mcp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true", help="Run a minimal HTTP JSON-RPC endpoint for Smithery scans")
    args = parser.parse_args()

    if args.http:
        # Build a simple mapping of tool functions to call directly
        tools: Dict[str, Callable] = {
            "get_population_data": get_population_data,
            "get_rsd_applications": get_rsd_applications,
            "get_rsd_decisions": get_rsd_decisions,
            "get_solutions": get_solutions,
        }

        class SimpleJSONRPCHandler(BaseHTTPRequestHandler):
            def log_request_info(self, body: str = None):
                # Log headers and a truncated body to help remote debugging
                try:
                    headers = {k: v for k, v in self.headers.items()}
                    logger.info(f"Incoming request path={self.path} headers={headers}")
                    if body is not None:
                        body_preview = (body[:1000] + '...') if len(body) > 1000 else body
                        logger.info(f"Incoming request body (truncated): {body_preview}")
                except Exception:
                    logger.exception("Failed to log request info")

            def do_GET(self):
                # Simple health endpoint so scanners can probe with GET
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                resp = {"status": "ok", "server": "unhcr-mcp"}
                body = json.dumps(resp).encode('utf-8')
                logger.info(f"Health check GET {self.path} -> 200")
                self.wfile.write(body)
            def _set_headers(self, status=200):
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()

            def do_OPTIONS(self):
                self._set_headers()

            def do_POST(self):
                # Read request body robustly: support Content-Length and chunked transfer encoding
                transfer_encoding = self.headers.get('Transfer-Encoding', '').lower()
                if 'chunked' in transfer_encoding:
                    # Read chunked body
                    chunks = []
                    while True:
                        # Read chunk size line
                        line = self.rfile.readline()
                        if not line:
                            break
                        try:
                            chunk_size = int(line.strip().split(b';')[0], 16)
                        except Exception:
                            break
                        if chunk_size == 0:
                            # consume trailer and final CRLF
                            self.rfile.readline()
                            break
                        chunk = self.rfile.read(chunk_size)
                        chunks.append(chunk)
                        # consume CRLF after chunk
                        self.rfile.read(2)
                    body = b''.join(chunks).decode('utf-8')
                else:
                    length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(length).decode('utf-8')
                try:
                    self.log_request_info(body)
                    payload = json.loads(body)
                except Exception:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "invalid json"}).encode())
                    return

                # Minimal handling for initialize
                if payload.get('method') == 'initialize':
                    result = {
                        "capabilities": {
                            "tools": [
                                {"name": name, "params": [p for p in inspect.signature(func).parameters.keys()]} 
                                for name, func in tools.items()
                            ]
                        }
                    }
                    response = {"jsonrpc": "2.0", "id": payload.get('id'), "result": result}
                    self._set_headers(200)
                    self.wfile.write(json.dumps(response).encode())
                    return

                # Route to tool functions if they exist
                method = payload.get('method')
                if method in tools:
                    params = payload.get('params', {})
                    try:
                        # Call tool function (pass only matching kwargs)
                        sig = inspect.signature(tools[method])
                        call_kwargs = {k: v for k, v in params.items() if k in sig.parameters}
                        res = tools[method](**call_kwargs)
                        response = {"jsonrpc": "2.0", "id": payload.get('id'), "result": res}
                        self._set_headers(200)
                        self.wfile.write(json.dumps(response).encode())
                    except Exception as e:
                        response = {"jsonrpc": "2.0", "id": payload.get('id'), "error": {"code": -32000, "message": str(e)}}
                        self._set_headers(500)
                        self.wfile.write(json.dumps(response).encode())
                    return

                # Unknown method
                response = {"jsonrpc": "2.0", "id": payload.get('id'), "error": {"code": -32601, "message": "Method not found"}}
                self._set_headers(404)
                self.wfile.write(json.dumps(response).encode())

        host = '0.0.0.0'
        port = int(__import__('os').environ.get('PORT', 8080))
        server = HTTPServer((host, port), SimpleJSONRPCHandler)

        def serve():
            logger.info(f"Starting minimal HTTP JSON-RPC server on {host}:{port}")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass

        t = threading.Thread(target=serve, daemon=True)
        t.start()
        print("HTTP MCP probe server running. Press Ctrl+C to stop.")
        t.join()
    else:
        # Run the server over stdio (default FastMCP behavior)
        print("MCP server running. Press Ctrl+C to stop.")
        mcp.run()
