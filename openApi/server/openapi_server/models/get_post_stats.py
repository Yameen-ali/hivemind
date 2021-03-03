# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class GetPostStats(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, flag_weight=None, gray=None, hide=None, total_votes=None):  # noqa: E501
        """GetPostStats - a model defined in OpenAPI

        :param flag_weight: The flag_weight of this GetPostStats.  # noqa: E501
        :type flag_weight: float
        :param gray: The gray of this GetPostStats.  # noqa: E501
        :type gray: bool
        :param hide: The hide of this GetPostStats.  # noqa: E501
        :type hide: bool
        :param total_votes: The total_votes of this GetPostStats.  # noqa: E501
        :type total_votes: int
        """
        self.openapi_types = {
            'flag_weight': float,
            'gray': bool,
            'hide': bool,
            'total_votes': int
        }

        self.attribute_map = {
            'flag_weight': 'flag_weight',
            'gray': 'gray',
            'hide': 'hide',
            'total_votes': 'total_votes'
        }

        self._flag_weight = flag_weight
        self._gray = gray
        self._hide = hide
        self._total_votes = total_votes

    @classmethod
    def from_dict(cls, dikt) -> 'GetPostStats':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GetPost_stats of this GetPostStats.  # noqa: E501
        :rtype: GetPostStats
        """
        return util.deserialize_model(dikt, cls)

    @property
    def flag_weight(self):
        """Gets the flag_weight of this GetPostStats.


        :return: The flag_weight of this GetPostStats.
        :rtype: float
        """
        return self._flag_weight

    @flag_weight.setter
    def flag_weight(self, flag_weight):
        """Sets the flag_weight of this GetPostStats.


        :param flag_weight: The flag_weight of this GetPostStats.
        :type flag_weight: float
        """
        if flag_weight is None:
            raise ValueError("Invalid value for `flag_weight`, must not be `None`")  # noqa: E501

        self._flag_weight = flag_weight

    @property
    def gray(self):
        """Gets the gray of this GetPostStats.


        :return: The gray of this GetPostStats.
        :rtype: bool
        """
        return self._gray

    @gray.setter
    def gray(self, gray):
        """Sets the gray of this GetPostStats.


        :param gray: The gray of this GetPostStats.
        :type gray: bool
        """
        if gray is None:
            raise ValueError("Invalid value for `gray`, must not be `None`")  # noqa: E501

        self._gray = gray

    @property
    def hide(self):
        """Gets the hide of this GetPostStats.


        :return: The hide of this GetPostStats.
        :rtype: bool
        """
        return self._hide

    @hide.setter
    def hide(self, hide):
        """Sets the hide of this GetPostStats.


        :param hide: The hide of this GetPostStats.
        :type hide: bool
        """
        if hide is None:
            raise ValueError("Invalid value for `hide`, must not be `None`")  # noqa: E501

        self._hide = hide

    @property
    def total_votes(self):
        """Gets the total_votes of this GetPostStats.


        :return: The total_votes of this GetPostStats.
        :rtype: int
        """
        return self._total_votes

    @total_votes.setter
    def total_votes(self, total_votes):
        """Sets the total_votes of this GetPostStats.


        :param total_votes: The total_votes of this GetPostStats.
        :type total_votes: int
        """
        if total_votes is None:
            raise ValueError("Invalid value for `total_votes`, must not be `None`")  # noqa: E501

        self._total_votes = total_votes
