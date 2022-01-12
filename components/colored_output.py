class ColoredOutput:

    __err: str = "\x1b[2;31;40m"
    __info: str = "\x1b[2;33;40m"
    __ok: str = "\x1b[2;32;40m"
    __end: str = "\x1b[0m"

    def print_info(self, text: str) -> None:
        print(f"{self.__info}{text}{self.__end}")

    def print_error(self, text: str) -> None:
        print(f"{self.__err}{text}{self.__end}")

    def print_ok(self, text: str) -> None:
        print(f"{self.__ok}{text}{self.__end}")
