#!/usr/bin/env python3
"""
Check that the new domain analysis routes are properly registered
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app


def check_routes():
    """Check that all expected routes are registered"""
    print("🔍 CHECKING REGISTERED ROUTES")
    print("=" * 50)
    
    # Get all routes from the FastAPI app
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method != 'HEAD':  # Skip HEAD methods
                    routes.append(f"{method} {route.path}")
    
    # Expected new routes
    expected_new_routes = [
        "GET /api/euring/domains/{domain}/fields",
        "GET /api/euring/domains/{domain}/compatibility/{fromVersion}/{toVersion}",
        "GET /api/euring/domains/export/{domain}"
    ]
    
    print("All registered routes:")
    for route in sorted(routes):
        print(f"  {route}")
    
    print("\nChecking for new domain analysis routes:")
    for expected_route in expected_new_routes:
        if expected_route in routes:
            print(f"  ✓ {expected_route}")
        else:
            print(f"  ✗ {expected_route} - NOT FOUND")
    
    # Check existing domain routes are still there
    existing_domain_routes = [
        "GET /api/euring/domains/{domain}/evolution",
        "GET /api/euring/domains/{domain}/compare/{version1}/{version2}",
        "GET /api/euring/domains/timeline"
    ]
    
    print("\nChecking existing domain routes:")
    for existing_route in existing_domain_routes:
        if existing_route in routes:
            print(f"  ✓ {existing_route}")
        else:
            print(f"  ✗ {existing_route} - NOT FOUND")
    
    print("\n" + "=" * 50)
    print("✅ Route registration check completed")


if __name__ == "__main__":
    check_routes()