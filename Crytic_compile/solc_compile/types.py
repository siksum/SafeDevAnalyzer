"""
Handle the platform type
"""

from enum import IntEnum


class Type(IntEnum):
    """
    Represent the different platform
    """

    NOT_IMPLEMENTED = 0
    SOLC = 1

    def __str__(self) -> str:  # pylint: disable=too-many-branches
        """Return a string representation

        Raises:
            ValueError: If the type is missing in __str__ (it should not happen)

        Returns:
            str: string representation
        """
        if self == Type.SOLC:
            return "solc"
        raise ValueError
