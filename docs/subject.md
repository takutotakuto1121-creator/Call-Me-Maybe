# Subject Requirement
## Summary
LLMを用いて、自然言語のプロンプトを構造化された関数呼び出しに変換するツールを作成します。

例えば、*What is the sum of 40 and 2?*というプロンプトが与えられれば、以下の内容を返します。

- 関数の名前: fn_add_numbers
- 引数: {"a": 40.0, "b": 2.0}

**Constrained Decoding**を用いて、100%正確なJSON形式のアウトプットをすることが求められます。
## LLM Model
**Qwen/Qwen3-0.6B**を使用します。
`torch`, `transformers`, `huggingface_hub`などを直接使用するのは禁止で、llm_sdkのSmall_LLM_Modelクラスをラッパーとして用います。
Small_LLM_Modelは以下のメソッドを提供します。
1. def encode(self, text: str) -> torch.Tensor:  
文字列をエンコードします。
2. def decode(self, ids: torch.Tensor | list[int]) -> str:   
トークンIDのリストをでコードします。
3. def get_logits_from_input_ids(self, input_ids: list[int]) -> list[float]:   
トークンIDのリストを受け取り、それを元に次に来るトークンの確率のリストを返します。
4.  def get_path_to_vocab_file(self) -> str:
トークンIDとトークンの対応表（辞書）へのパスを返します

## Constrained Decoding
LLMは、文章が与えられると、それを単語などの最小単位(トークン)に分割し、最小単位ごとに対応する数字IDを割り当てます(エンコード)。次にそのトークンIDのリストを受け取り、次にくるトークンを予測します。これを何回も繰り返します。次に来るトークンを何回も予測して、最後にIDを文字に直し(デコード)て出力します。

このうち、次に来るトークンを予測するプロセスに介入し、指定した形式の出力になるようにするのが、**Constrained Decoding** です。

今回はこのConstrainde Decodingを用いて、100%正確なJSONの形式を満たすようにします。

## Performance and Reliability
出力は以下の条件を満たす必要があります。
- 90%以上正確な関数選択と引数選択を行うこと。
- 100%完璧なJSON出力にすること。
- 標準的なハードウェアで5分以内に実行可能なこと。
- 完璧なエラーハンドリングをすること。

## Input Files
プログラムは、以下のような形式のプロンプトが書かれたJSONファイルを受け取ります。
```json
[
  {
    "prompt": "What is the sum of 2 and 3?"
  },
  {
    "prompt": "What is the sum of 265 and 345?"
  },
  {
    "prompt": "Greet shrek"
  },
  {
    "prompt": "Greet john"
  },
  {
    "prompt": "Reverse the string'hello'"
  }
  ...
]
```

また、使用可能な関数が書かれたJSONファイルも受け取ります。
```json
[
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
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  {
    "name": "fn_reverse_string",
    "description": "Reverse a string and return the reversed result.",
    "parameters": {
      "s": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  ...
]
```

## Output Files
プログラムは以下のような形式のJSONファイルを出力します。100%正確なJSON形式になる必要があります。また、項目も**Qwen/Qwen3-0.6B**で90%以上正確に出力される必要があります。
```json
[
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
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  {
    "name": "fn_reverse_string",
    "description": "Reverse a string and return the reversed result.",
    "parameters": {
      "s": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
...
]
```



