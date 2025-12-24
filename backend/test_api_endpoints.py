#!/usr/bin/env python3
"""
Test script to verify API endpoints are properly registered
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

def test_api_routes():
    """Test that all expected routes are registered"""
    print("=== Testing API Route Registration ===\n")
    
    # Get all routes from the FastAPI app
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method != 'HEAD':  # Skip HEAD methods
                    routes.append(f"{method} {route.path}")
    
    # Expected domain evolution endpoints
    expected_domain_endpoints = [
        "GET /api/euring/domains/{domain}/evolution",
        "GET /api/euring/domains/{domain}/compare/{version1}/{version2}",
        "GET /api/euring/domains/timeline"
    ]
    
    print("All registered routes:")
    for route in sorted(routes):
        print(f"  {route}")
    
    print(f"\nTotal routes: {len(routes)}")
    
    # Check for domain evolution endpoints
    print("\nChecking for domain evolution endpoints:")
    for endpoint in expected_domain_endpoints:
        found = any(endpoint in route for route in routes)
        status = "✓" if found else "✗"
        print(f"  {status} {endpoint}")
    
    # Check for existing endpoints
    existing_endpoints = [
        "GET /api/euring/recognize",
        "GET /api/euring/convert", 
        "GET /api/euring/versions",
        "GET /api/euring/health"
    ]
    
    print("\nChecking for existing endpoints:")
    for endpoint in existing_endpoints:
        found = any(endpoint in route for route in routes)
        status = "✓" if found else "✗"
        print(f"  {status} {endpoint}")
    
    print("\n=== Route registration test completed ===")

if __name__ == "__main__":
    test_api_routes()