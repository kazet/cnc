import typing
from unittest.mock import MagicMock

Numeric = typing.Union[int, float]


def mockable(cls):
    """
    Builds a type annotation that supports both a type and mocks.

    For example, mockable(BaseMachine) is a type annotation that supports
    both BaseMachine and a mock.

    The typeguard PR to support mocks is open at this moment (2020-01-15):
    https://github.com/agronholm/typeguard/issues/96
    """
    return typing.Union[cls, MagicMock]
