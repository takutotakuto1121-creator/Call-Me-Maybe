# Json Checker
文字列を受け取り、その文字列が適切に指定されたJSONの形式を満たしているかをチェックするクラスです。

作成するJsonは以下の形式です。

```json
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {
        "type": "number"
      },
      "b": {
        "type": "number"
      }
    },
    "returns": {
      "type": "number"
    }
  },
```

このJSONに対して、自分は今どこにいるのか、状態を列挙します。状態を列挙したクラスが以下のModeクラスです。

```python
from enum import Enum, auto

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
```


name, description, parametersそれぞれのkey, valueのどの部分に今現在いるのかという情報を持っておきます。

例えば、今NAME_LINE_BREAKにいるなら、次に来るのは改行("\n")しか許されないので、次のトークンが改行で始まるならTrue, 始まらないならFalseを返します。のように各状態で次に来てもいいトークンかそうでないトークンかを判定しています。

jsonの形式については[json.org](json.org)を参照してください。

あとはコードを読めばわかると思います。
