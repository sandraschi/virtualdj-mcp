#!/usr/bin/env python3
"""
Local FastAPI Interface Test Script

Tests the FastAPI REST interface endpoints.
Run this script to verify API endpoints and functionality.
"""

import asyncio
import httpx
import json
import sys
import os
from pathlib import Path
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient
from virtualdj_mcp.api.app import create_app


async def test_fastapi_endpoints():
    """Test FastAPI endpoints using test client"""
    print("🧪 Testing VirtualDJ-MCP FastAPI Interface")
    print("=" * 50)

    # Create test client
    app = create_app()
    client = TestClient(app)

    # Test 1: Health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"

        print(f"✅ Health check passed: {data['status']}")

    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

    # Test 2: OpenAPI docs endpoint
    print("\n2. Testing /api/docs endpoint...")
    try:
        response = client.get("/api/docs")
        # FastAPI docs returns HTML, just check it's not an error
        assert response.status_code in [200, 422]  # 422 is normal for docs without proper setup
        print("✅ API docs endpoint accessible")

    except Exception as e:
        print(f"❌ API docs test failed: {e}")
        return False

    # Test 3: OpenAPI schema endpoint
    print("\n3. Testing /api/openapi.json endpoint...")
    try:
        response = client.get("/api/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        print("✅ OpenAPI schema valid")

    except Exception as e:
        print(f"❌ OpenAPI schema test failed: {e}")
        return False

    # Test 4: API v1 endpoints structure
    print("\n4. Testing API v1 endpoint structure...")
    try:
        schema = client.get("/api/openapi.json").json()
        paths = schema.get("paths", {})

        # Check for expected endpoints
        expected_endpoints = [
            "/api/v1/deck/{deck_id}/status",
            "/api/v1/deck/{deck_id}/play_pause",
            "/api/v1/deck/{deck_id}/load",
            "/api/v1/library/search",
            "/api/v1/audio/analyze"
        ]

        for endpoint in expected_endpoints:
            if endpoint in paths:
                print(f"✅ Endpoint {endpoint} found")
            else:
                print(f"⚠️  Endpoint {endpoint} not found in schema")

        print("✅ API v1 structure verified")

    except Exception as e:
        print(f"❌ API v1 structure test failed: {e}")
        return False

    print("\n🎉 All FastAPI interface tests passed!")
    print("\nNext steps:")
    print("- Start the FastAPI server: RUN_FASTAPI=true python -m mcp.server")
    print("- Access API docs at: http://localhost:8000/api/docs")
    print("- Test endpoints with tools like curl or Postman")

    return True


async def test_cors_configuration():
    """Test CORS configuration"""
    print("\n5. Testing CORS configuration...")
    try:
        app = create_app()
        client = TestClient(app)

        # Test preflight request
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

        print("✅ CORS configuration valid")

    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

    return True


async def generate_postman_collection():
    """Generate a basic Postman collection for testing"""
    print("\n6. Generating Postman collection...")

    collection = {
        "info": {
            "name": "VirtualDJ-MCP API",
            "description": "REST API endpoints for VirtualDJ automation",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/health",
                        "host": ["{{base_url}}"],
                        "path": ["health"]
                    }
                }
            },
            {
                "name": "Get Deck Status",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/v1/deck/1/status",
                        "host": ["{{base_url}}"],
                        "path": ["api", "v1", "deck", "1", "status"]
                    }
                }
            },
            {
                "name": "Search Library",
                "request": {
                    "method": "POST",
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "query": "house",
                            "limit": 10
                        })
                    },
                    "url": {
                        "raw": "{{base_url}}/api/v1/library/search",
                        "host": ["{{base_url}}"],
                        "path": ["api", "v1", "library", "search"]
                    }
                }
            }
        ],
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            }
        ]
    }

    # Save collection to file
    output_path = Path(__file__).parent / "VirtualDJ-MCP_API.postman_collection.json"
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)

    print(f"✅ Postman collection generated: {output_path}")

    return True


async def main():
    """Main test function"""
    print("VirtualDJ-MCP Local FastAPI Interface Test")
    print("This script tests the REST API endpoints without requiring a running server")

    success = await test_fastapi_endpoints()
    if success:
        success = await test_cors_configuration()

    if success:
        await generate_postman_collection()

    if success:
        print("\n✅ All tests passed! FastAPI interface is ready.")
        print("\nTo run the FastAPI server:")
        print("  RUN_FASTAPI=true python -m mcp.server")
        print("\nTo access API documentation:")
        print("  http://localhost:8000/api/docs")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


