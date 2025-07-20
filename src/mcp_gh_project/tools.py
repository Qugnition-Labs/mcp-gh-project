"""MCP tool definitions for GitHub project management."""

from mcp import types

TOOLS = [
    types.Tool(
        name="list_projects",
        description="List GitHub projects for a user, organization, or repository",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "The owner (user or organization) of the projects",
                },
                "repo": {
                    "type": "string",
                    "description": "Optional repository name to list projects for a specific repo",
                },
            },
            "required": ["owner"],
        },
    ),
    types.Tool(
        name="get_project",
        description="Get details of a specific GitHub project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "The ID of the project to retrieve",
                }
            },
            "required": ["project_id"],
        },
    ),
    types.Tool(
        name="list_project_items",
        description="List all items (issues, PRs, draft issues) in a GitHub project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "The ID of the project to list items for",
                }
            },
            "required": ["project_id"],
        },
    ),
    types.Tool(
        name="create_project_item",
        description="Create a new item in a GitHub project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "The ID of the project to add the item to",
                },
                "content_type": {
                    "type": "string",
                    "enum": ["ISSUE", "PULL_REQUEST", "DRAFT_ISSUE"],
                    "description": "The type of content to add to the project",
                },
                "content_id": {
                    "type": "string",
                    "description": "The ID of the existing issue or PR (required for ISSUE and PULL_REQUEST types)",
                },
                "title": {"type": "string", "description": "Title for draft issues"},
                "body": {
                    "type": "string",
                    "description": "Body content for draft issues",
                },
            },
            "required": ["project_id", "content_type"],
        },
    ),
    types.Tool(
        name="update_project_item",
        description="Update field values of a project item",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "The ID of the project containing the item",
                },
                "item_id": {
                    "type": "string",
                    "description": "The ID of the project item to update",
                },
                "field_updates": {
                    "type": "object",
                    "description": "Dictionary of field names and their new values",
                    "additionalProperties": True,
                },
            },
            "required": ["project_id", "item_id"],
        },
    ),
    types.Tool(
        name="delete_project_item",
        description="Remove an item from a GitHub project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "The ID of the project containing the item",
                },
                "item_id": {
                    "type": "string",
                    "description": "The ID of the project item to delete",
                },
            },
            "required": ["project_id", "item_id"],
        },
    ),
]
