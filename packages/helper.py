"""Collection of helper functions."""
import collections


def tree():
    """Create an infinite dictionary."""
    return collections.defaultdict(tree)
