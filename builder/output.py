import sys

### Output ###
# ANSI escape codes, disabled when the output is not a terminal
_COLOR = sys.stdout.isatty()

_BOLD = "\033[1m" if _COLOR else ""
_CYAN = "\033[36m" if _COLOR else ""
_GREEN = "\033[32m" if _COLOR else ""
_RED = "\033[31m" if _COLOR else ""
_YELLOW = "\033[33m" if _COLOR else ""
_RESET = "\033[0m" if _COLOR else ""


def bold(text: str) -> str:
    """
    Structure: table headers and lines the user has to act on.
    """
    return f"{_BOLD}{text}{_RESET}"


def cyan(text: str) -> str:
    """
    Identifier: environment names.
    """
    return f"{_CYAN}{text}{_RESET}"


def green(text: str) -> str:
    """
    Exists: a directory, volume or secret already present on disk.
    """
    return f"{_GREEN}{text}{_RESET}"


def red(text: str) -> str:
    """
    Irreversible: data being destroyed, before and after the fact.
    """
    return f"{_RED}{text}{_RESET}"


def yellow(text: str) -> str:
    """
    Reserved only for bootstrap admin password, that user must copy.
    Shown only once.
    """
    return f"{_YELLOW}{text}{_RESET}"
