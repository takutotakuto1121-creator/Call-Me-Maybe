from enum import Enum, auto
from pydantic import BaseModel, Field


class Mode(Enum):
    START_SPACE = auto()
    START = auto()

    PROMPT_LINE_BREAK = auto()
    PROMPT_SPACE = auto()
    PROMPT_KEY = auto()
    PROMPT_VALUE = auto()
    PROMPT_COMMA = auto()

    NAME_LINE_BREAK = auto()
    NAME_SPACE = auto()
    NAME_KEY = auto()
    NAME_VALUE = auto()
    NAME_COMMA = auto()

    PARAMETER_LINE_BREAK = auto()
    PARAMETER_SPACE = auto()
    PARAMETER_KEY = auto()

    PARAMETER_VALUE_KEY = auto()
    PARAMETER_VALUE_COLON_SPACE = auto()
    PARAMETER_VALUE_VALUE = auto()
    PARAMETER_VALUE_COMMA_SPACE_QUOTE_OR_CLOSE = auto()

    END_LINE_BREAK = auto()
    END_SPACE = auto()
    END = auto()
    DONE = auto()


class NumState(Enum):
    START = auto()
    MINUS = auto()
    INT_ZERO = auto()
    INT = auto()
    FRAC_START = auto()
    FRAC = auto()
    EXP_START = auto()
    EXP_SIGN = auto()
    EXP = auto()


class JsonState(BaseModel):
    mode: Mode = Field(default=Mode.START_SPACE)
    num_state: NumState = Field(default=NumState.START)
    in_string: bool = Field(default=False)
    in_number: bool = Field(default=False)
    literal_target: str = Field(default=False)
    literal_num: int = Field(default=0)
    tfn_target: str = Field(default="")
    tfn_num: int = Field(default=0)
    space_num: int = Field(default=0)


class JsonChecker:
    PROMPT = "prompt"
    NAME = "name"
    PARAMETER = "parameter"

    def __init__(self) -> None:
        self.state = JsonState()
        self.PROMPT = '"prompt": '
        self.NAME = '"name"': '
        self.PARAMETER = '"parameter": '

    def snapshot(self) -> JsonState:
        return self.state.model_copy(deep=True)

    def restore(self, snapshot: JsonState) -> None:
        self.state = snapshot.model_copy(deep=True)

    def check(self, token_text: str) -> bool:
        for c in token_text:
            if not self.check_char(c):
                return False
        return True

    def is_completed(self) -> bool:
        return self.state.mode == Mode.DONE

    def check_char(self, c: str) -> bool:
        mode = self.state.mode
        # ---- オブジェクト内は先に ----
        if self.state.in_string:
            return self.feed_string(c)

        if self.state.in_number:
            return self.feed_number(c)

        if self.state.literal_target:
            return self.feed_literal(c)

        if self.state.tfn_target:
            return self.feed_tfn(c)

        #---- それ以外はModeで ----
        if mode == Mode.START_SPACE:
            if c == " ":
                self.state.space_num += 1
                if self.state.space_num == 2:
                    self.state.mode = Mode.START
                    self.state.space_num = 0
                return True
            else:
                return False

        elif mode == Mode.START:
            if c == "{":
                self.state.mode = Mode.PROMPT_LINE_BREAK
                return True
            else:
                return False

        elif mode == Mode.PROMPT_LINE_BREAK:
            if c == "\n":
                self.state.mode = Mode.PROMPT_SPACE
                return True
            else:
                return False

        elif mode == Mode.PROMPT_SPACE:
            if c == " ":
                self.state.space_num += 1
                if self.state.space_num == 4:
                    self.state.mode = Mode.PROMPT_KEY
                    self.state.space_num = 0
                    self.state.target = "prompt"
                return True
            else:
                return False

        elif mode == Mo



    def feed_string(self, c: str) -> bool:
        if c == '"':
            self.state.in_string = False
            if self.state.mode == Mode.PROMPT_VALUE:
                self.state.mode = Mode.PROMPT_COMMA
            elif self.state.mode == Mode.NAME_VALUE:
                self.state.mode = Mode.NAME_COMMA
            elif self.state.mode == Mode.PARAMETER_VALUE_KEY:
                self.state.mode = Mode.PARAMETER_VALUE_COLON_SPACE
            elif self.state.mode == Mode.PARAMETER_VALUE_VALUE:
                self.state.mode = Mode.PARAMETER_VALUE_COMMA_SPACE_QUOTE_OR_CLOSE
            return True
        else:
            return True

    def _feed_number(self, c: str) -> bool:
        s = self.state.num_state
        # ---- 数字なら ----
        if c.isdigit():
            if s == NumState.START:
                self.state.num_state = NumState.INT_ZERO if c == "0" else NumState.INT
            elif s == NumState.MINUS:
                self.state.num_state = NumState.INT_ZERO if c == "0" else NumState.INT
            elif s == NumState.INT_ZERO:
                return False  # 先頭ゼロの後に数字は続けられない
            elif s == NumState.INT:
                pass  # 続けて数字OK
            elif s == NumState.FRAC_START:
                self.state.num_state = NumState.FRAC
            elif s == NumState.FRAC:
                pass
            elif s == NumState.EXP_START or s == NumState.EXP_SIGN:
                self.state.num_state = NumState.EXP
            elif s == NumState.EXP:
                pass
            return True

        # ---- 数字以外なら ----
        if c == "." and s in (NumState.INT_ZERO, NumState.INT):
            self.state.num_state = NumState.FRAC_START
            return True

        if c in "eE" and s in (NumState.INT_ZERO, NumState.INT, NumState.FRAC):
            self.state.num_state = NumState.EXP_START
            return True

        if c in "+-" and s == NumState.EXP_START:
            self.state.num_state = NumState.EXP_SIGN
            return True

        # 数値として続けられない文字が来た → 数値を終了し、通常モードで再処理
        if s not in (NumState.INT_ZERO, NumState.INT, NumState.FRAC, NumState.EXP):
            return False

        self.state.in_number = False
        self.state.mode = Mode.PARAMETER_VALUE_COMMA_SPACE_QUOTE_OR_CLOSE
        return self.check_char(c)

    def feed_literal(self, c: str) -> bool:
        target = self.state.literal_target
        num = self.state.literal_num
        if num > len(target) or target[num] != c:
            return False
        self.state.literal_num +=  1
        if self.state.literal_num == len(target):
            if target == PROMPT:
                self.state.mode = Mode.PROMPT_VALUE
            elif target == NAME:
                self.state.mode = Mode.NAME_VALUE
            elif target == PARAMETER:
                self.state.mode = Mode.PARAMETER_VALUE
            self.state.literal_target = ""
            self.state.literal_num = 0

        return True

    def _feed_tfn(self, c: str) -> bool:
        target = self.state.tfn_target
        pos = self.state.tfn_pos
        if pos >= len(target) or target[pos] != c:
            return False
        self.state.tfn_pos += 1
        if self.state.tfn_pos == len(target):
            self.state.tfn_target = ""
            self.state.tfn_pos = 0
            self.state.mode = Mode.PARAMETER_VALUE_COMMA_SPACE_QUOTE_OR_CLOSE
        return True
