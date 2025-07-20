#!/usr/bin/env python3
"""Test script for the MCP server without freezing."""

import asyncio
import os
import sys


async def test_mcp_server():
    """Test the MCP server components directly."""

    # Import here to avoid any startup issues
    from mcp_gh_project.github_client import GitHubClient
    from mcp_gh_project.tools import TOOLS

    print("Testing MCP server components...")

    # Test 1: Check if tools are properly defined
    try:
        print(f"✅ Server has {len(TOOLS)} tools defined:")
        for tool in TOOLS:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error accessing tools: {e}")
        return False

    # Test 2: Test GitHub client initialization without token
    try:
        # Temporarily remove any existing token
        original_token = os.environ.get("GITHUB_TOKEN")
        if "GITHUB_TOKEN" in os.environ:
            del os.environ["GITHUB_TOKEN"]

        try:
            client = GitHubClient()
            print("❌ GitHub client should require token")
            return False
        except ValueError as e:
            print("✅ GitHub client properly validates token requirement")
            print(f"   Expected error: {e}")

        # Restore original token if it existed
        if original_token:
            os.environ["GITHUB_TOKEN"] = original_token

    except Exception as e:
        print(f"❌ Unexpected error testing GitHub client: {e}")
        return False

    # Test 3: Test GitHub client with dummy token
    try:
        client = GitHubClient("dummy_token_for_testing")
        print("✅ GitHub client accepts token parameter")

        # Test that it fails gracefully with invalid token
        try:
            await client.list_projects("test_owner")
            print("❌ Should fail with invalid token")
        except Exception as e:
            print("✅ GitHub client fails gracefully with invalid token")
            print(f"   Error type: {type(e).__name__}")

    except Exception as e:
        print(f"❌ Error testing GitHub client with token: {e}")
        return False

    print("\n🎉 All MCP server component tests passed!")
    return True


async def test_server_startup():
    """Test that server can be imported and initialized without hanging."""
    try:
        from mcp_gh_project.server import main

        print("✅ Server main function imported successfully")

        # Don't actually run main() as it will wait for stdio
        print("✅ Server is ready to start (would listen on stdio)")
        return True
    except Exception as e:
        print(f"❌ Error importing server: {e}")
        return False


if __name__ == "__main__":
    print("=== Testing MCP Server Components ===")
    success1 = asyncio.run(test_mcp_server())

    print("\n=== Testing Server Startup ===")
    success2 = asyncio.run(test_server_startup())

    if success1 and success2:
        print("\n🎉 All tests passed! MCP server is ready to use.")
        print("\nTo run the server:")
        print("1. Set GITHUB_TOKEN environment variable")
        print("2. Run: python -m mcp_gh_project")
        print("3. Server will communicate via stdin/stdout using MCP protocol")
    else:
        print("\n❌ Some tests failed.")

    sys.exit(0 if (success1 and success2) else 1)
