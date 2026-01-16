"""Support code for OptionLists that want to find things."""

##############################################################################
# Python imports.
from typing import Callable, Iterator, Literal

##############################################################################
# Textual imports.
from textual.widgets import OptionList

##############################################################################
type HighlightDirection = Literal["next", "previous"]
"""Type of a unread search direction."""


##############################################################################
def options_after_highlight[T](
    option_list: OptionList,
    options: list[T],
    direction: HighlightDirection,
    option_filter: Callable[[T], bool] | None = None,
) -> Iterator[T]:
    """Return a list of `OptionList` options after the highlight.

    Args:
        option_list: The `OptionList` to work against.
        options: The options from the given option list.
        direction: The direction to consider as 'after'.
        option_filter: Optional filter to apply to the list.

    Returns:
        An iterator of options.

    Notes:
        If there is no highlight, we default at position 0.

        The options are taken as a parameter, rather than just been pulled
        out of `option_list`, so that you have a chance to `cast` the list
        to the desired type, which in turn ensures that the return type
        matches.
    """
    option_filter = option_filter or (lambda _: True)
    highlight = option_list.highlighted or 0
    options = list(reversed(options)) if direction == "previous" else options
    highlight = (len(options) - highlight - 1) if direction == "previous" else highlight
    return (
        option
        for option in [*options[highlight:], *options[0:highlight]][1:]
        if option_filter(option)
    )


### _after_highlight.py ends here
