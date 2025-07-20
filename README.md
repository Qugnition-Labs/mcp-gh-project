# MCP GitHub Project Management Server

A Model Context Protocol (MCP) server for managing GitHub project items (cards). This server enables AI assistants to interact with GitHub Projects v2, allowing you to create, read, update, and delete project items directly from your AI conversations.

## 🤖 Demo
![Animation](https://github.com/user-attachments/assets/fe292953-f813-488a-8348-7f49390db085)

## 🚀 Features

- **List GitHub Projects** - Browse projects for users, organizations, or repositories
- **Project Management** - Get detailed project information
- **Item Operations** - Create, read, update, and delete project items
- **Support for Multiple Content Types** - Issues, Pull Requests, and Draft Issues
- **Field Management** - Update custom project fields
- **Secure Authentication** - Uses GitHub Personal Access Tokens

## 📋 Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with appropriate permissions
- One of the supported AI tools (Claude Desktop/Code, OpenAI Codex, Google Gemini CLI)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/mcp-gh-project.git
cd mcp-gh-project
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install the package
pip install -e .

# Install development dependencies (optional, for building/testing)
pip install -e ".[dev]"
```

### 4. GitHub Authentication

Create a GitHub Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (for repository access)
   - `project` (for project management)
   - `read:org` (if using organization projects)

Set your token as an environment variable:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your token
```

## 🤖 AI Tool Integration

### Claude Desktop & Claude Code

#### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-gh-project": {
      "command": "/path/to/mcp-gh-project/venv/bin/python",
      "args": ["-m", "mcp_gh_project"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

#### Claude Code Configuration

For Claude Code (claude.ai/code), add to your project's `CLAUDE.md` file or configure in your MCP settings:

```json
{
  "mcpServers": {
    "mcp-gh-project": {
      "command": "python",
      "args": ["-m", "mcp_gh_project"],
      "cwd": "/path/to/mcp-gh-project",
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

### OpenAI Codex Integration

For OpenAI Codex or tools that support MCP, configure the server connection:

```python
import mcp
from mcp.client import ClientSession

# Connect to the MCP server
async def connect_to_github_mcp():
    session = ClientSession()
    await session.connect_subprocess(
        command="python",
        args=["-m", "mcp_gh_project"],
        env={"GITHUB_TOKEN": "your_token_here"}
    )
    return session
```

### Google Gemini CLI

Configure Gemini CLI to use the MCP server:

```bash
# Install Gemini CLI with MCP support
pip install google-generativeai mcp-client

# Configure MCP server
gemini config set mcp.servers.github.command "python -m mcp_gh_project"
gemini config set mcp.servers.github.env.GITHUB_TOKEN "your_token_here"
```

Or use a configuration file:

```yaml
# ~/.gemini/config.yaml
mcp:
  servers:
    github:
      command: "python"
      args: ["-m", "mcp_gh_project"]
      env:
        GITHUB_TOKEN: "your_github_token_here"
```

## 🛠️ Available Tools

The MCP server provides the following tools:

### `list_projects`
List GitHub projects for a user, organization, or repository.

**Parameters:**
- `owner` (required): GitHub username or organization name
- `repo` (optional): Repository name to list repository-specific projects

**Example:**
```
List all projects for the "microsoft" organization
```

### `get_project`
Get detailed information about a specific project.

**Parameters:**
- `project_id` (required): The project ID

**Example:**
```
Get details for project ID "PVT_kwDOBkn5os4ABTQ6"
```

### `list_project_items`
List all items (issues, PRs, draft issues) in a project.

**Parameters:**
- `project_id` (required): The project ID

**Example:**
```
Show all items in project "PVT_kwDOBkn5os4ABTQ6"
```

### `create_project_item`
Create a new item in a project.

**Parameters:**
- `project_id` (required): The project ID
- `content_type` (required): "ISSUE", "PULL_REQUEST", or "DRAFT_ISSUE"
- `content_id` (optional): ID of existing issue/PR (required for ISSUE/PULL_REQUEST)
- `title` (optional): Title for draft issues
- `body` (optional): Body content for draft issues

**Example:**
```
Create a draft issue titled "Fix documentation" in project "PVT_kwDOBkn5os4ABTQ6"
```

### `update_project_item`
Update field values of a project item.

**Parameters:**
- `project_id` (required): The project ID
- `item_id` (required): The project item ID
- `field_updates` (optional): Dictionary of field names and values

**Example:**
```
Update the status field of item "PVTI_lADOBkn5os4ABTQ6zgCc" to "In Progress"
```

### `delete_project_item`
Remove an item from a project.

**Parameters:**
- `project_id` (required): The project ID  
- `item_id` (required): The project item ID

**Example:**
```
Remove item "PVTI_lADOBkn5os4ABTQ6zgCc" from project "PVT_kwDOBkn5os4ABTQ6"
```

## 💡 Usage Examples

Once configured with your AI tool, you can use natural language commands:

### Project Discovery
```
"Show me all projects for the facebook organization"
"List projects in the microsoft/vscode repository"
"What projects does the user octocat have?"
```

### Project Management
```
"Get details about project PVT_kwDOBkn5os4ABTQ6"
"Show all items in the main project"
"Create a new draft issue called 'Update dependencies' in the project"
```

### Item Operations
```
"Add issue #123 to the project board"
"Move the documentation task to the 'Done' column"
"Remove the outdated feature request from the project"
```

## 🔧 Development

### Running Tests

```bash
# Run all tests
npm run test

# Or run individually
python tests/test_server.py
python tests/test_compile.py
```

### Linting and Formatting

```bash
# Check code quality
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run typecheck
```

### Building

```bash
# Install development dependencies first
pip install -e ".[dev]"

# Build distribution packages
npm run build
```

## 🐛 Troubleshooting

### Common Issues

#### "GitHub token is required" Error
- Ensure your `GITHUB_TOKEN` environment variable is set
- Verify the token has the correct scopes (`repo`, `project`)
- Check that the token hasn't expired

#### "Project not found" Error
- Verify you have access to the project
- Ensure the project ID is correct
- Check that the project is a GitHub Projects v2 (not classic projects)

#### MCP Server Connection Issues
- Verify the Python path in your configuration
- Check that all dependencies are installed
- Ensure the virtual environment is activated in the configuration

#### Permission Denied
- Verify your GitHub token has the necessary permissions
- For organization projects, ensure you're a member with appropriate access
- Check repository permissions for repository-specific projects

### Debug Mode

Run the server with debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m mcp_gh_project
```

### Logs

Check MCP client logs for connection and communication issues:
- **Claude Desktop**: Check the application logs
- **Claude Code**: Look in the developer console
- **Custom implementations**: Enable MCP client logging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For support and questions:
- Open an issue on GitHub
- Check the [GitHub Projects API documentation](https://docs.github.com/en/graphql/reference/objects#projectv2)
- Review the [MCP specification](https://modelcontextprotocol.io/introduction)

---

**Built with ❤️ by [Qugnition Labs](https://github.com/qugnition-labs)**
