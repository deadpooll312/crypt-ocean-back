import random
import string


def get_random_number():
    return random.randint(100000, 999999)


def get_random_string():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
