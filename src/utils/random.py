import binascii
import os

from typeguard import typechecked


@typechecked
def random_token(length: int = 40) -> str:
    """
    Returns a random token with given length.
    """
    return binascii.hexlify(os.urandom(length))[:length].decode('ascii')
