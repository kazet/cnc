import random
import string


def random_token(length=40):
    # XXX not cryptographically-secure
    result = ''
    for _ in range(length):
        result += random.choice(string.ascii_letters + string.digits)
    return result
