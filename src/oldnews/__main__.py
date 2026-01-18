"""The main entry point to the application."""

##############################################################################
# Python imports.
from argparse import ArgumentParser, Namespace
from inspect import cleandoc
from operator import attrgetter

##############################################################################
# Local imports.
from . import __doc__, __version__
from .data import initialise_database, reset_data
from .oldnews import OldNews


##############################################################################
def get_args() -> Namespace:
    """Get the command line arguments.

    Returns:
        The arguments.
    """

    # Build the parser.
    parser = ArgumentParser(
        prog="oldnews",
        description=__doc__,
        epilog=f"v{__version__}",
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information",
        action="version",
        version=f"%(prog)s v{__version__}",
    )

    # Add --theme
    parser.add_argument(
        "-t",
        "--theme",
        help="Set the theme for the application (see `themes` command for available themes)",
    )

    # Allow for commands on the command line.
    sub_parser = parser.add_subparsers(
        dest="command", help="Available commands", required=False
    )

    # Add the 'license' command.
    sub_parser.add_parser(
        "license",
        aliases=["licence"],
        help="Show license information",
    )

    # Add the 'bindings' command.
    sub_parser.add_parser(
        "bindings",
        help="List commands that can have their bindings changed",
    )

    # Add the 'themes' command.
    sub_parser.add_parser(
        "themes", help="List the available themes that can be used with --theme"
    )

    # Add the 'reset' command.
    sub_parser.add_parser(
        "reset", help="Remove all data downloaded from TheOldReader"
    ).add_argument(
        "-l", "--logout", help="Force a logout from TheOldReader", action="store_true"
    )

    # Finally, parse the command line.
    return parser.parse_args()


##############################################################################
def show_bindable_commands() -> None:
    """Show the commands that can have bindings applied."""
    from rich.console import Console
    from rich.markup import escape

    from .screens import Main

    console = Console(highlight=False)
    for command in sorted(Main.COMMAND_MESSAGES, key=attrgetter("__name__")):
        if command().has_binding:
            console.print(
                f"[bold]{escape(command.__name__)}[/] [dim italic]- {escape(command.tooltip())}[/]"
            )
            console.print(
                f"    [dim italic]Default: {escape(command.binding().key)}[/]"
            )


##############################################################################
def show_themes() -> None:
    """Show the available themes."""
    for theme in sorted(OldNews(Namespace(theme=None)).available_themes):
        if theme != "textual-ansi":
            print(theme)


##############################################################################
def main() -> None:
    """Main entry function."""
    match (args := get_args()).command:
        case "reset":
            reset_data(args.logout)
            print("Local data erased")
            if args.logout:
                print("Login token removed")
        case "license" | "licence":
            print(cleandoc(OldNews.HELP_LICENSE))
        case "bindings":
            show_bindable_commands()
        case "themes":
            show_themes()
        case _:
            initialise_database()
            OldNews(args).run()


### __main__.py ends here
