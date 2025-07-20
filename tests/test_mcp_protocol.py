#!/usr/bin/env python3
"""Test MCP protocol communication without hanging."""

import asyncio
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from typing import Optional


async def test_mcp_protocol():
    """Test MCP protocol by sending initialization and list_tools requests."""

    # Set a dummy token to avoid initialization errors
    env = os.environ.copy()
    env["GITHUB_TOKEN"] = "dummy_token_for_testing"

    print("Starting MCP server process...")

    # Get the project root directory (parent of tests directory)
    project_root = Path(__file__).parent.parent

    # Start the server process
    process = await asyncio.create_subprocess_exec(
        "python",
        "-m",
        "mcp_gh_project",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        cwd=str(project_root),
    )

    try:
        # Test 1: Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("Sending initialization request...")
        init_json = json.dumps(init_request) + "\n"
        process.stdin.write(init_json.encode())
        await process.stdin.drain()

        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                process.stdout.readline(), timeout=5.0
            )
            if response_line:
                response = json.loads(response_line.decode().strip())
                print(
                    f"✅ Received initialization response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}"
                )
            else:
                print("❌ No response to initialization")
                return False
        except asyncio.TimeoutError:
            print("❌ Timeout waiting for initialization response")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False

        # Test 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }

        print("Sending initialized notification...")
        initialized_json = json.dumps(initialized_notification) + "\n"
        process.stdin.write(initialized_json.encode())
        await process.stdin.drain()

        # Test 3: Send list_tools request
        list_tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

        print("Sending list_tools request...")
        tools_json = json.dumps(list_tools_request) + "\n"
        process.stdin.write(tools_json.encode())
        await process.stdin.drain()

        # Read tools response
        try:
            response_line = await asyncio.wait_for(
                process.stdout.readline(), timeout=5.0
            )
            if response_line:
                response = json.loads(response_line.decode().strip())
                tools = response.get("result", {}).get("tools", [])
                print(f"✅ Received {len(tools)} tools from server")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"   - {tool.get('name', 'Unknown')}")
                if len(tools) > 3:
                    print(f"   ... and {len(tools) - 3} more")
                return True
            print("❌ No response to list_tools")
            return False
        except asyncio.TimeoutError:
            print("❌ Timeout waiting for list_tools response")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False

    except Exception as e:
        print(f"❌ Error during protocol test: {e}")
        return False
    finally:
        # Clean shutdown
        print("Shutting down server...")
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            print("Force killing server process...")
            process.kill()
            await process.wait()


if __name__ == "__main__":
    print("=== Testing MCP Protocol Communication ===")
    print("Note: This test requires the MCP server to be installed.")
    print("Run 'pip install -e .' first if you haven't already.")
    
    try:
        success = asyncio.run(test_mcp_protocol())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
