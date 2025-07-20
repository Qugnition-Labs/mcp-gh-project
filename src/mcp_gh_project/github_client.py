"""GitHub API client for project management operations."""

import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class GitHubProject(BaseModel):
    """GitHub project model."""

    id: str
    number: int
    title: str
    body: Optional[str] = None
    state: str
    url: str
    owner: Dict[str, Any]


class GitHubProjectItem(BaseModel):
    """GitHub project item model."""

    id: str
    type: str
    content: Optional[Dict[str, Any]] = None
    field_values: Dict[str, Any]
    project: Dict[str, Any]


class GitHubClient:
    """Client for interacting with GitHub's GraphQL API for project management."""

    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub client."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            msg = "GitHub token is required. Set GITHUB_TOKEN environment variable."
            raise ValueError(msg)

        self.base_url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
        }

    async def _execute_query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub's API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                msg = f"GraphQL errors: {data['errors']}"
                raise Exception(msg)

            return data.get("data", {})

    async def list_projects(
        self, owner: Optional[str] = None, repo: Optional[str] = None
    ) -> List[GitHubProject]:
        """List GitHub projects for a user, organization, or repository."""
        if repo and owner:
            query = """
            query($owner: String!, $repo: String!) {
                repository(owner: $owner, name: $repo) {
                    projectsV2(first: 100) {
                        nodes {
                            id
                            number
                            title
                            shortDescription
                            public
                            url
                            owner {
                                ... on User { name }
                                ... on Organization { name }
                            }
                        }
                    }
                }
            }
            """
            variables = {"owner": owner, "repo": repo}
            data = await self._execute_query(query, variables)
            projects_data = (
                data.get("repository", {}).get("projectsV2", {}).get("nodes", [])
            )
        elif owner:
            query = """
            query($owner: String!) {
                repositoryOwner(login: $owner) {
                    ... on User {
                        projectsV2(first: 100) {
                            nodes {
                                id
                                number
                                title
                                shortDescription
                                public
                                url
                                owner {
                                    ... on User { name }
                                }
                            }
                        }
                    }
                    ... on Organization {
                        projectsV2(first: 100) {
                            nodes {
                                id
                                number
                                title
                                shortDescription
                                public
                                url
                                owner {
                                    ... on Organization { name }
                                }
                            }
                        }
                    }
                }
            }
            """
            variables = {"owner": owner}
            data = await self._execute_query(query, variables)
            projects_data = (
                data.get("repositoryOwner", {}).get("projectsV2", {}).get("nodes", [])
            )
        else:
            msg = "Either 'owner' or both 'owner' and 'repo' must be provided"
            raise ValueError(msg)

        return [
            GitHubProject(
                id=project["id"],
                number=project["number"],
                title=project["title"],
                body=project.get("shortDescription"),
                state="open" if project.get("public") else "private",
                url=project["url"],
                owner=project["owner"],
            )
            for project in projects_data
        ]

    async def get_project(self, project_id: str) -> GitHubProject:
        """Get a specific GitHub project by ID."""
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    id
                    number
                    title
                    shortDescription
                    public
                    url
                    owner {
                        login
                        ... on User { name }
                        ... on Organization { name }
                    }
                }
            }
        }
        """
        variables = {"projectId": project_id}
        data = await self._execute_query(query, variables)
        project_data = data.get("node")

        if not project_data:
            raise ValueError(f"Project with ID {project_id} not found")

        return GitHubProject(
            id=project_data["id"],
            number=project_data["number"],
            title=project_data["title"],
            body=project_data.get("shortDescription"),
            state="open" if project_data.get("public") else "private",
            url=project_data["url"],
            owner=project_data["owner"],
        )

    async def list_project_items(self, project_id: str) -> List[GitHubProjectItem]:
        """List items in a GitHub project."""
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: 100) {
                        nodes {
                            id
                            type
                            content {
                                ... on Issue {
                                    id
                                    number
                                    title
                                    body
                                    state
                                    url
                                }
                                ... on PullRequest {
                                    id
                                    number
                                    title
                                    body
                                    state
                                    url
                                }
                                ... on DraftIssue {
                                    id
                                    title
                                    body
                                }
                            }
                            fieldValues(first: 20) {
                                nodes {
                                    ... on ProjectV2ItemFieldTextValue {
                                        text
                                        field {
                                            ... on ProjectV2FieldCommon {
                                                name
                                            }
                                        }
                                    }
                                    ... on ProjectV2ItemFieldNumberValue {
                                        number
                                        field {
                                            ... on ProjectV2FieldCommon {
                                                name
                                            }
                                        }
                                    }
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                        name
                                        field {
                                            ... on ProjectV2FieldCommon {
                                                name
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"projectId": project_id}
        data = await self._execute_query(query, variables)
        items_data = data.get("node", {}).get("items", {}).get("nodes", [])

        return [
            GitHubProjectItem(
                id=item["id"],
                type=item["type"],
                content=item.get("content"),
                field_values={
                    field_value.get("field", {}).get("name", ""): (
                        field_value.get("text")
                        or field_value.get("number")
                        or field_value.get("name")
                    )
                    for field_value in item.get("fieldValues", {}).get("nodes", [])
                    if field_value.get("field", {}).get("name")
                },
                project={"id": project_id},
            )
            for item in items_data
        ]

    async def create_project_item(
        self,
        project_id: str,
        content_type: str,
        content_id: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
    ) -> GitHubProjectItem:
        """Create a new item in a GitHub project."""
        if content_type == "DRAFT_ISSUE":
            mutation = """
            mutation($projectId: ID!, $title: String!, $body: String) {
                addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
                    projectItem {
                        id
                        type
                        content {
                            ... on DraftIssue {
                                id
                                title
                                body
                            }
                        }
                    }
                }
            }
            """
            variables = {
                "projectId": project_id,
                "title": title or "New Draft Issue",
                "body": body,
            }
            data = await self._execute_query(mutation, variables)
            item_data = data.get("addProjectV2DraftIssue", {}).get("projectItem")
        else:
            mutation = """
            mutation($projectId: ID!, $contentId: ID!) {
                addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                    item {
                        id
                        type
                        content {
                            ... on Issue {
                                id
                                number
                                title
                                body
                                state
                                url
                            }
                            ... on PullRequest {
                                id
                                number
                                title
                                body
                                state
                                url
                            }
                        }
                    }
                }
            }
            """
            if not content_id:
                raise ValueError("content_id is required for non-draft issues")

            variables = {"projectId": project_id, "contentId": content_id}
            data = await self._execute_query(mutation, variables)
            item_data = data.get("addProjectV2ItemById", {}).get("item")

        if not item_data:
            msg = "Failed to create project item"
            raise Exception(msg)

        return GitHubProjectItem(
            id=item_data["id"],
            type=item_data["type"],
            content=item_data.get("content"),
            field_values={},
            project={"id": project_id},
        )

    async def update_project_item(
        self, project_id: str, item_id: str, field_updates: Dict[str, Any]
    ) -> GitHubProjectItem:
        """Update a project item's field values."""
        # This is a simplified implementation - actual field updates require field IDs
        # which would need to be retrieved first
        query = """
        query($itemId: ID!) {
            node(id: $itemId) {
                ... on ProjectV2Item {
                    id
                    type
                    content {
                        ... on Issue {
                            id
                            number
                            title
                            body
                            state
                            url
                        }
                        ... on PullRequest {
                            id
                            number
                            title
                            body
                            state
                            url
                        }
                        ... on DraftIssue {
                            id
                            title
                            body
                        }
                    }
                }
            }
        }
        """
        variables = {"itemId": item_id}
        data = await self._execute_query(query, variables)
        item_data = data.get("node")

        if not item_data:
            raise ValueError(f"Project item with ID {item_id} not found")

        return GitHubProjectItem(
            id=item_data["id"],
            type=item_data["type"],
            content=item_data.get("content"),
            field_values=field_updates,
            project={"id": project_id},
        )

    async def delete_project_item(self, project_id: str, item_id: str) -> bool:
        """Delete a project item."""
        mutation = """
        mutation($projectId: ID!, $itemId: ID!) {
            deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) {
                deletedItemId
            }
        }
        """
        variables = {"projectId": project_id, "itemId": item_id}
        data = await self._execute_query(mutation, variables)
        return bool(data.get("deleteProjectV2Item", {}).get("deletedItemId"))
