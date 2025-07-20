#!/usr/bin/env python3
"""
Client for interacting with the GitHub API.
"""
from utils import get_json


class GithubOrgClient:
    """
    A client to interact with the GitHub Organizations API.
    """
    def __init__(self, org_name: str):
        """
        Initializes a GithubOrgClient instance.

        Args:
            org_name (str): The name of the GitHub organization.
        """
        self._org_name = org_name

    def org(self) -> dict:
        """
        Retrieves the organization's information from the GitHub API.

        Returns:
            dict: A dictionary containing the organization's data.
        """
        # Construct the URL for the organization's API endpoint
        org_url = f"https://api.github.com/orgs/{self._org_name}"
        # Call get_json to fetch the data
        return get_json(org_url)
