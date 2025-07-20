#!/usr/bin/env python3
"""Simple test to verify MCP server functionality."""

import subprocess
import sys
import os

def test_server_import():
    """Test that all server components can be imported."""
    try:
        cmd = [
            sys.executable, "-c", 
            """
import sys
sys.path.insert(0, '/home/luciano/projects/mcp-gh-project/src')

try:
    from mcp_gh_project.server import server, main
    from mcp_gh_project.tools import TOOLS  
    from mcp_gh_project.github_client import GitHubClient
    print('SUCCESS: All imports work')
    print(f'Tools available: {len(TOOLS)}')
    
    # Test basic functionality
    client = GitHubClient('dummy')
    print('SUCCESS: GitHub client initialization works')
    
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/luciano/projects/mcp-gh-project")
        
        if result.returncode == 0:
            print("✅ Server imports and initializes successfully")
            print(result.stdout.strip())
            return True
        else:
            print("❌ Import test failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running import test: {e}")
        return False

def test_server_help():
    """Test server help/version information."""
    try:
        # Test if we can at least import the server module
        cmd = [
            sys.executable, "-c",
            "import mcp_gh_project; print('Module import successful')"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/luciano/projects/mcp-gh-project")
        
        if result.returncode == 0:
            print("✅ MCP module can be imported")
            return True
        else:
            print("❌ Module import failed")
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing module: {e}")
        return False

if __name__ == "__main__":
    print("=== Simple MCP Server Tests ===")
    
    # Activate virtual environment first
    venv_python = "/home/luciano/projects/mcp-gh-project/venv/bin/python"
    if os.path.exists(venv_python):
        # Use the virtual environment python
        old_executable = sys.executable
        sys.executable = venv_python
        
        success1 = test_server_import()
        success2 = test_server_help()
        
        sys.executable = old_executable
    else:
        success1 = test_server_import()
        success2 = test_server_help()
    
    if success1 and success2:
        print("\n🎉 MCP server is properly compiled and ready!")
        print("\nThe server freezing issue is normal behavior:")
        print("- MCP servers listen on stdin/stdout for JSON-RPC messages")
        print("- They wait for client connections via the MCP protocol")
        print("- Use with Claude Desktop or other MCP clients")
    else:
        print("\n❌ Some tests failed")
    
    sys.exit(0 if (success1 and success2) else 1)