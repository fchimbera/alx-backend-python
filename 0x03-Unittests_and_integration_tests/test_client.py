#!/usr/bin/env python3
"""
Test file for client.py
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called once with the expected argument.
        """
        # Define the expected return value for get_json
        expected_org_data = {"login": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = expected_org_data

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org

        # Assert that get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

        # Assert that the result is the expected organization data
        self.assertEqual(result, expected_org_data)

    def test_public_repos_url(self):
        """
        Tests that _public_repos_url returns the correct value based on a mocked org property.
        """
        # Define the payload that the mocked org property will return
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        mock_org_payload = {"repos_url": expected_repos_url}

        # Use patch as a context manager to mock the 'org' property
        # PropertyMock is used because 'org' is a property (due to @memoize)
        with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = mock_org_payload

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("testorg")

            # Call the _public_repos_url property
            result = client._public_repos_url

            # Assert that the 'org' property was called
            mock_org.assert_called_once()

            # Assert that the result is the expected repos URL
            self.assertEqual(result, expected_repos_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Tests that GithubOrgClient.public_repos returns the expected list of repos,
        and that mocked methods/properties are called once.
        """
        # Define the payload for get_json (repos_payload)
        mock_repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_repos_payload

        # Define the expected list of repository names
        expected_repos = ["repo1", "repo2", "repo3"]

        # Use patch as a context manager to mock _public_repos_url property
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            # Set the return value for the mocked _public_repos_url
            mock_public_repos_url.return_value = "https://api.github.com/orgs/testorg/repos"

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("testorg")

            # Call the public_repos method
            result_repos = client.public_repos()

            # Assert that _public_repos_url was called once
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once
            mock_get_json.assert_called_once()

            # Assert that the list of repos matches the expected list
            self.assertEqual(result_repos, expected_repos)

