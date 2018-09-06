from functools import wraps


def int_property_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        value = func(*args)
        try:
            return int(value)
        except (TypeError, ValueError):
            # If there is no value, default to None. None is statistically
            # different from 0 as a player/team who played an entire game and
            # contributed nothing is different from one who didn't play at all.
            # This enables flexibility for end-users to decide whether they
            # want to fill the empty value with any specific number (such as 0
            # or an average/median for the category) or keep it empty depending
            # on their use-case.
            return None
    return wrapper


def float_property_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        value = func(*args)
        try:
            return float(value)
        except (TypeError, ValueError):
            # If there is no value, default to None. None is statistically
            # different from 0 as a player/team who played an entire game and
            # contributed nothing is different from one who didn't play at all.
            # This enables flexibility for end-users to decide whether they
            # want to fill the empty value with any specific number (such as 0
            # or an average/median for the category) or keep it empty depending
            # on their use-case.
            return None
    return wrapper
