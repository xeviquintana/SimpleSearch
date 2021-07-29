class Scanner:
    def __init__(self, exit_word: str, prompt: str) -> None:
        self._exit_word = exit_word
        self._prompt = prompt

    @property
    def exit_word(self) -> str:
        return self._exit_word

    @property
    def prompt(self) -> str:
        return self._prompt

    def read_input_as_string(self) -> str:
        return str(input(self._prompt))

    def is_exit_statement(self, line: str) -> bool:
        return line == self.exit_word
