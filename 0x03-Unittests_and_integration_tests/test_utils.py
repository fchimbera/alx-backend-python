#!/usr/bin/env python3
"""
Unit tests for the access_nested_map function from utils module.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map


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

