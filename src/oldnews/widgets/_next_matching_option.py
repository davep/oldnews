"""Support code for OptionLists that want to find things."""

##############################################################################
# Python imports.
from typing import Callable

##############################################################################
# BagOfStuff imports.
from bagofstuff.itertools import Direction, starting_at


##############################################################################
def next_matching_option[T](
    options: list[T],
    current_highlight: int | None,
    direction: Direction,
    matching: Callable[[T], bool] | None = None,
) -> T | None:
    """Return a list of `OptionList` options after the highlight.

    Args:
        options: The options from the given option list.
        current_highlight: The current highlighted option.
        direction: The direction to work in.
        matching: Optional filter to apply to the list.

    Returns:
        The next matching option, or `None` if there isn't one.

    Notes:
        If there is no highlight, we default at position 0.
    """
    matching = matching or (lambda _: True)
    if current_highlight is None:
        current_highlight = 0
    else:
        current_highlight += 1 if direction == "forward" else -1
    return next(
        (
            option
            for option in starting_at(options, current_highlight, direction)
            if matching(option)
        ),
        None,
    )


##############################################################################
# Re-export the direction type.
__all__ = ["Direction"]

### _next_matching_option.py ends here
