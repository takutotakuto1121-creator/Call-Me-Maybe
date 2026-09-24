from enum import Enum, auto
from pydantic import BaseModel, Field

class Mode(Enum):
    START = auto()                # 値の開始を待つ（'{' のみ許可）
    OBJ_KEY_OR_CLOSE = auto()     # '{'の後 or ','の後: KEY or '}'
    OBJ_COLON = auto()            # VALUEの後: ':'
    OBJ_VALUE = auto()            # ':' の後: VALUE
    OBJ_COMMA_OR_CLOSE = auto()   # VALUEの後: ',' か '}'
    DONE = auto()                 # トップレベルの "{...}" が完成  


class NumState(Enum):
    START = auto()                # 値の開始を待つ(-の直後もこれ)
    INT_ZERO = auto()             # 整数部が0
    INT = auto()                  # 整数部が0以外
    FRAC_START = auto()           # .の直後
    FRAC = auto()                 # 少数部の数字を書いている途中
    EXP_START = auto()            # e/Eの直後
    EXP_SIGN = auto()             # e+/e-の直後
    EXP = auto()                  # 指数部の数字を書いている途中


class JsonState(BaseModel):
    mode: Mode = Field(default=Mode.START)
    numstate: NumState = Field(default=NumState.START)
    string_len: int = Field(default=0)
    in_brace: bool = Field(default=False)
    in_string: bool = Field(default=False)
    in_number: bool = Field(default=False)
    in_key: bool = Field(default=False)
    in_value: bool = Field(default=False)
    escaped: bool = Field(default=False)
    allow_close: bool = Field(default=False)
    has_prompt: bool = Field(default=False)
    has_name: bool = Field(default=False)
    has_returns: bool = Field(default=False)
    is_space: bool = Field(default=False)


class JsonChecker:
    def __init__(self) -> None:
        self.state = JsonState()

    def snapshot(self) -> JsonState:
        return self.state.model_copy(deep=True)

    def restore(self, snapshot: JsonState):
        self.state = snapshot.model_copy(deep=True)

    def check(self, token_text: str) -> bool:
        for c in token_text:
            if not self.check_char(c):
                return False
        return True

    def check_char(self, c: str) -> bool:
        # ---- 文字列の中にいる場合は優先的に処理 ----
        if self.state.in_string:
            if c == '"':
                if self.state.string_len == 0:
                    return False
                self.state.in_string = False
                self.state.string_len = 0
                if self.state.in_key:
                    self.state.mode = Mode.OBJ_COLON
                    self.state.in_key = False
                elif self.state.in_value:
                    self.state.mode = Mode.OBJ_COMMA_OR_CLOSE
                    self.state.in_value = False
                else:
                    return False
            self.state.string_len += 1
            return True

        # ---- 文字列の外、Modeごとに判断 ----
        if self.state.mode == Mode.START:
            if c == "{" and self.state.is_space is False:
                self.state.is_space = True
                return True
            if (c == " " or c == "\n") and self.state.is_space is True:
                if c == '"':
                    self.state.mode = Mode.OBJ_KEY_OR_CLOSE
                    self.state.is_space = False
                else:
            if c == ""


            else:
                return False

        elif self.state.mode == Mode.OBJ_KEY_OR_CLOSE:
            if c == " " or c == "\n":
                return True
            elif c == '"':
                self.state.in_string = True
                self.state.in_key = True
                return True
            elif c == "}" and self.state.allow_close:
                self.state.mode = Mode.DONE
                return True
            else:
                return False

        elif self.state.mode == Mode.OBJ_COLON:
            if c == ":":
                self.state.mode = Mode.OBJ_VALUE
                return True
            else:
                return False

        elif self.state.mode == Mode.OBJ_VALUE:
            if c == '"':
                self.state.in_string = True
                self.state.in_value = True
                return True
            else:
                return False

        elif self.state.mode == Mode.OBJ_COMMA_OR_CLOSE:
            if c == ",":
                self.state.mode = Mode.OBJ_KEY_OR_CLOSE
                self.state.allow_close = False
                return True
            elif c == "}":
                self.state.mode = Mode.DONE
                return True
            else:
                return False

        else:
            return False

    def is_completed(self) -> bool:
        return self.state.mode == Mode.DONE
