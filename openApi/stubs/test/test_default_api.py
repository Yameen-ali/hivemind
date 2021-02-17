"""
    Hivemind OpenAPI Specification

    An OpenAPI specification for Hivemind  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


import unittest

import openapi_client
from openapi_client.api.default_api import DefaultApi  # noqa: E501


class TestDefaultApi(unittest.TestCase):
    """DefaultApi unit test stubs"""

    def setUp(self):
        self.api = DefaultApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_bridge_account_notifications(self):
        """Test case for bridge_account_notifications

        """
        pass

    def test_bridge_does_user_follow_any_lists(self):
        """Test case for bridge_does_user_follow_any_lists

        """
        pass

    def test_bridge_get_account_posts(self):
        """Test case for bridge_get_account_posts

        """
        pass

    def test_bridge_get_community(self):
        """Test case for bridge_get_community

        """
        pass

    def test_bridge_get_community_context(self):
        """Test case for bridge_get_community_context

        """
        pass

    def test_bridge_get_profile(self):
        """Test case for bridge_get_profile

        """
        pass

    def test_bridge_list_all_subscriptions(self):
        """Test case for bridge_list_all_subscriptions

        """
        pass

    def test_bridge_list_communities(self):
        """Test case for bridge_list_communities

        """
        pass

    def test_bridge_list_community_roles(self):
        """Test case for bridge_list_community_roles

        """
        pass

    def test_bridge_list_pop_communities(self):
        """Test case for bridge_list_pop_communities

        """
        pass

    def test_bridge_list_subscribers(self):
        """Test case for bridge_list_subscribers

        """
        pass


if __name__ == '__main__':
    unittest.main()
