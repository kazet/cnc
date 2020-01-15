import random
import string

from typeguard import typechecked


@typechecked
def random_token(length: int = 40) -> str:
    """
    Returns a random token with given length.
    """
    # XXX not cryptographically-secure
    result = ''
    for _ in range(length):
        result += random.choice(string.ascii_letters + string.digits)
    return result
