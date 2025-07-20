#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    TestGithubOrgClient class to test the GithubOrgClient.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        
        # Define the expected payload for the mocked get_json call
        expected_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_payload

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org()

        # Construct the expected URL that get_json should have been called with
        expected_url = f"https://api.github.com/orgs/{org_name}"

        # Assert that get_json was called exactly once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # Assert that the result matches the expected payload
        self.assertEqual(result, expected_payload)

