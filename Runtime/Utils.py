"""Collection of helper functions."""
import collections

CMD_NULL = 0
CMD_CONTINUE = -1
CMD_EXIT = -2


def tree():
    """Create an infinite dictionary."""
    return collections.defaultdict(tree)
