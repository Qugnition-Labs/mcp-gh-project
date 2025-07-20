"""Main MCP server implementation for GitHub project management."""

import asyncio
import logging
from typing import Any

import mcp.server.stdio
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from mcp_gh_project.github_client import GitHubClient
from mcp_gh_project.tools import TOOLS

logger = logging.getLogger(__name__)

server = Server("mcp-gh-project")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return TOOLS


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}

    try:
        github_client = GitHubClient()

        if name == "list_projects":
            result = await github_client.list_projects(
                owner=arguments.get("owner"), repo=arguments.get("repo")
            )
        elif name == "get_project":
            result = await github_client.get_project(project_id=arguments["project_id"])
        elif name == "list_project_items":
            result = await github_client.list_project_items(
                project_id=arguments["project_id"]
            )
        elif name == "create_project_item":
            result = await github_client.create_project_item(
                project_id=arguments["project_id"],
                content_type=arguments["content_type"],
                content_id=arguments.get("content_id"),
                title=arguments.get("title"),
                body=arguments.get("body"),
            )
        elif name == "update_project_item":
            result = await github_client.update_project_item(
                project_id=arguments["project_id"],
                item_id=arguments["item_id"],
                field_updates=arguments.get("field_updates", {}),
            )
        elif name == "delete_project_item":
            result = await github_client.delete_project_item(
                project_id=arguments["project_id"], item_id=arguments["item_id"]
            )
        else:
            return _handle_unknown_tool(name)

        return [types.TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.exception("Error calling tool %s", name)
        return [types.TextContent(type="text", text=f"Error: {e!s}")]


async def main() -> None:
    """Main entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-gh-project",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def _handle_unknown_tool(name: str) -> list[types.TextContent]:
    """Handle unknown tool calls."""
    error_msg = f"Unknown tool: {name}"
    raise ValueError(error_msg)


if __name__ == "__main__":
    asyncio.run(main())
