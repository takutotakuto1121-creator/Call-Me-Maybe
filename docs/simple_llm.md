# Simple LLM
普段LLMとはGUI上で会話のような形式で文章のやり取りを行なっている人が多いでしょう。これを、`encode`, `decode`, `get_logits_from_input_ids` のみを用いて実装するにはどうすれば良いのかを考えます。

LLMは、文章が与えられると、それを単語などの最小単位(トークン)に分割し、最小単位ごとに対応する数字IDを割り当てます(エンコード)。次にそのトークンIDのリストを受け取り、次にくるトークンを予測します。これを何回も繰り返します。次に来るトークンを何回も予測して、最後にIDを文字に直し(デコード)て出力します。

これをそのままコードにすると以下のようになります。

```python
from llm_sdk import Small_LLM_Model


class SimpleLLM:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model

    def generate(
            self, prompt: str, max_new_tokens: int = 50
            ) -> str:
        # エンコード
        token_ids: list[int] = self.model.encode(prompt).tolist()[0]

        for _ in range(max_new_tokens):
            # 次に来るトークンの確率をlogitsに
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)

            # 一番確率が高いトークンをmax_token_idに
            next_token_id = max(range(len(logits)), key=lambda i: logits[i])
            # トークンを決定してまた次のトークンを予測するためにループを繰り返す
            token_ids.append(next_token_id)

        # デコード
        result = self.model.decode(token_ids)
        return result
```

これが何も強制しない時のLLMの使用方法になります。

では、ここからどの部分に介入すれば自分が望む形式の出力に強制できるのでしょうか。それは、次に来るトークンの確率のリスト`logits`の生成過程です。この過程に介入して、次のトークンがもし適さないトークンであれば、その確率を手動で*-inf*に飛ばし、新たな`masked logits`を作成すれば良いです。