def print_error(text: str) -> None:
    print(f"\x1b[4;31;40m{text}\x1b[0m")


def print_info(text: str) -> None:
    print(f"\x1b[2;33;40m{text}\x1b[0m")


def print_ok(text: str) -> None:
    print(f"\x1b[2;32;40m{text}\x1b[0m")
