# Json Checker
A class that receives a string and checks whether it correctly satisfies the specified JSON format.

The JSON to be produced has the following format:

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

For this JSON, we enumerate the states describing where we currently are. The class enumerating these states is the Mode class below.

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


We keep track of which part (key or value) of name, description, or parameters we are currently in.

For example, if we are currently in NAME_LINE_BREAK, the only thing allowed next is a newline ("\n"), so we return True if the next token starts with a newline and False otherwise. In this way, each state determines whether a token is allowed to come next.

For the JSON format, see [json.org](https://www.json.org).

The rest should be clear from reading the code.
