#!/usr/bin/env python3
"""
Unit tests for the access_nested_map function from utils module.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map
from unittest.mock import patch, Mock
from utils import get_json
from utils import memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    TestAccessNestedMap class to test the access_nested_map function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: dict, path: tuple, expected: any) -> None:
        """
        Tests that the access_nested_map function returns the expected result
        for various valid nested map and path inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(self, nested_map: dict, path: tuple, expected_exception: type) -> None:
        """
        Tests that the access_nested_map function raises a KeyError
        with the expected message for invalid inputs.
        """
        with self.assertRaises(expected_exception) as cm:
            access_nested_map(nested_map, path)
        # Check the exception message for the specific key that caused the error
        if path == ("a",):
            self.assertEqual(str(cm.exception), "'a'")
        elif path == ("a", "b"):
            self.assertEqual(str(cm.exception), "'b'")


class TestGetJson(unittest.TestCase):
    """
    TestGetJson class to test the get_json function.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url: str, test_payload: dict) -> None:
        """
        Tests that get_json returns the expected result and that requests.get
        is called exactly once with the correct URL.
        """
        # Create a Mock object for the response
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        # Patch requests.get to return our mock_response
        with patch('requests.get', return_value=mock_response) as mock_get:
            result = get_json(test_url)

            # Assert that requests.get was called exactly once with the test_url
            mock_get.assert_called_once_with(test_url)

            # Assert that the output of get_json is equal to test_payload
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    TestMemoize class to test the memoize decorator.
    """
    def test_memoize(self) -> None:
        """
        Tests that a_method is called only once when a_property is accessed twice,
        demonstrating the memoization effect.
        """
        class TestClass:
            """
            A test class to demonstrate memoization.
            """
            def a_method(self) -> int:
                """
                A simple method that returns 42.
                """
                return 42

            @memoize
            def a_property(self) -> int:
                """
                A property that calls a_method and is memoized.
                """
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            test_instance = TestClass()
            # Call a_property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property
            # Assert that a_method was called exactly once
            mock_method.assert_called_once()
            # Assert that the correct result is returned
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
