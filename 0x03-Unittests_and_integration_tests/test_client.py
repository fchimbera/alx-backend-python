#!/usr/bin/env python3
"""
Test file for client.py
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import fixtures # Import the fixtures


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
        expected_org_data = {
            "login": org_name,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = expected_org_data

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org

        # Assert that get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

        # Assert that the result is the expected organization data
        self.assertEqual(result, expected_org_data)

    def test_public_repos_url(self):
        """
        Tests that _public_repos_url returns the correct value based on a
        mocked org property.
        """
        # Define the payload that the mocked org property will return
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        mock_org_payload = {"repos_url": expected_repos_url}

        # Use patch as a context manager to mock the 'org' property
        # PropertyMock is used because 'org' is a property (due to @memoize)
        with patch(
            'client.GithubOrgClient.org', new_callable=PropertyMock
        ) as mock_org:
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
        Tests that GithubOrgClient.public_repos returns the expected list of
        repos, and that mocked methods/properties are called once.
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
        with patch(
            'client.GithubOrgClient._public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            # Set the return value for the mocked _public_repos_url
            mock_public_repos_url.return_value = \
                "https://api.github.com/orgs/testorg/repos"

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

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": {"key": "my_license"}, "name": "repo"},
         "my_license", True),
        ({"license": {"key": "other_license"}, "name": "repo"},
         "my_license", False),
        ({}, "my_license", False),  # Test with no license key
        ({"license": {}}, "my_license", False),  # Test with empty license dict
        ({"license": {"key": None}}, "my_license", False)  # Test with None
    ])
    def test_has_license(self, repo, license_key, expected_return):
        """
        Tests that GithubOrgClient.has_license returns the correct boolean
        value.
        """
        # Call the static method has_license directly
        result = GithubOrgClient.has_license(repo, license_key)

        # Assert that the result matches the expected return value
        self.assertEqual(result, expected_return)


@parameterized_class(fixtures)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up class-level mocks for requests.get.
        This patcher will be started once for each parameterized class.
        """
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        # Define the side effect for requests.get
        def side_effect_func(url):
            mock_response = Mock()
            # Use cls.org_payload and cls.repos_payload as they are
            # class attributes for each parameterized instance
            if url == cls.org_payload["repos_url"].replace("/repos", ""):
                # This is the URL for the organization data
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                # This is the URL for the repositories data
                mock_response.json.return_value = cls.repos_payload
            else:
                # Fallback for unexpected URLs, can raise an error or return empty
                mock_response.json.return_value = {}
            return mock_response

        cls.mock_get.side_effect = side_effect_func

    def setUp(self):
        """
        Reset the mock's call count and history before each test method.
        This ensures a clean mock for every test within a parameterized class.
        """
        self.mock_get.reset_mock()

    @classmethod
    def tearDownClass(cls):
        """
        Stop the patcher after all tests in the class have run.
        This ensures the mock is properly cleaned up for each parameterized class.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Tests the public_repos method in an integration context.
        """
        # Create an instance of GithubOrgClient using the org name from fixture
        org_name = self.org_payload["login"]
        client = GithubOrgClient(org_name)

        # Call the public_repos method
        result = client.public_repos()

        # Assert that the result matches the expected_repos from the fixture
        self.assertEqual(result, self.expected_repos)

        # Assert that requests.get was called twice (once for org, once for repos)
        # The exact URLs depend on the org_payload
        org_url = GithubOrgClient.ORG_URL.format(org=org_name)
        repos_url = self.org_payload["repos_url"]

        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)
        self.assertEqual(self.mock_get.call_count, 2)

    def test_public_repos_with_license(self):
        """
        Tests the public_repos method with a license filter in an integration
        context.
        """
        # Create an instance of GithubOrgClient using the org name from fixture
        org_name = self.org_payload["login"]
        client = GithubOrgClient(org_name)

        # Call the public_repos method with 'apache-2.0' license
        result = client.public_repos(license="apache-2.0")

        # Assert that the result matches the apache2_repos from the fixture
        self.assertEqual(result, self.apache2_repos)

        # Assert that requests.get was called twice (once for org, once for repos)
        # The exact URLs depend on the org_payload
        org_url = GithubOrgClient.ORG_URL.format(org=org_name)
        repos_url = self.org_payload["repos_url"]

        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)
        self.assertEqual(self.mock_get.call_count, 2)
