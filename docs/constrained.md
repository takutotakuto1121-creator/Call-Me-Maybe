# Constrained LLM
では、ここからどの部分に介入すれば自分が望む形式の出力に強制できるのでしょうか。それは、次に来るトークンの確率のリスト`logits`の生成過程です。この過程に介入して、次のトークンがもし適さないトークンであれば、その確率を手動で**-inf**に飛ばし、新たな`masked logits`を作成すれば、そのトークンは次のトークンとして選ばれることは無くなるので、トークン選択の際に、適しているトークンのうち、確率が最も高いトークンが選択されることになります。SimpleLLMを改良して以下のConstrainedLLMを作成します。

```python
from llm_sdk import Small_LLM_Model


class ConstrainedLLM:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model

    def check_json(self, next_token_id: int) -> bool:
        next_token_text = self.model.decode(next_token_id)
        return self.checker.check(next_token_text)

    def generate(
            self, prompt: str, max_new_tokens: int = 50
            ) -> str:
        # エンコード
        token_ids: list[int] = self.model.encode(prompt).tolist()[0]

        for _ in range(max_new_tokens):
            # 次に来るトークンの確率をlogitsに
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)

            # ---- ここで何かしらのチェックを行う ----
            masked_logits = ...
            # ------------

            # 一番確率が高いトークンをmax_token_idに(logitsをmasked_logitsに変更)
            next_token_id = max(range(len(masked_logits)), key=lambda i: masked_logits[i])
            # トークンを決定してまた次のトークンを予測するためにループを繰り返す
            token_ids.append(next_token_id)

        # デコード
        result = self.model.decode(token_ids)
        return result
```

以上の場所で何かしらのチェックを行い、以下の`logits`を`masked_logits`に変更すれば良いです。

何かしらのチェッカー(`self.checker`)でチェックを行いますがは今は置いておきます。

例えば以下のような方法が考えられます。

```python
masked_logits = []

for index, logit in enumerate(logits):
    if not self.check_json(token_ids, index):
        logit = -math.inf
        masked_logits.append(logit)
```

indexは、logitsの数分だけ0から順番に取り出しているため、これは**token_id**を表します。**全て**のtoken_idに対してチェックを行い、それがJSONの形式に敵さなければそのIDの`masked_logits`は-infに飛ばします。そのため、適しているtoken_IDのみが選択されるようになります。全てが-infになる場合の例外処理行うべきですが簡単のために一旦スルーします。

ただ、この実装では毎回全てのトークン１つを選択するごとにトークンIDを選択するごとに全てのトークンIDを呼び出し、全てのトークンIDに対してチェックを行うので、かなり処理に時間がかかってしまいます。

そこで、以下のように順番を少し入れ替えてみます。

```python
masked_logits = [-math.inf] * len(logits)
sorted_indices = sorted(
    range(len(logits)),
    key=lambda i: logits[i],
    reverse=True
    )

for index in sorted_indecies:
    if self.check_json(token_ids, index):
        masked_logits[index] = logits[index]
        break
```

まずlogitが大きい順にindexを並び替えた`sorted_indecies`を作成します。この順番にindexを取り出していき、チェックをかけていき、JSONフォーマットに適したものが出てきた時点でbreakでループを抜け出します。

全てに対してチェックを行い、不適なindexのligitを-infに飛ばしてそのうちの最大logitのindexを次のトークンIDとする作業と、先にlogitが大きい順でindexを並び替えて、順番に適しているか判断して、適していればそのindexをトークンIDとする作業では、結局同じindexを取ることになります。

よって同じ結果が出てくるのに対して、前者では全てに対してチェックを毎回行いのでとんでもない数のチェックが必要になり、後者ではチェックをしていき一度的してものが出てきた時点でチェックのループを抜けるので必要なチェック数が桁違いに減ります。なのでこの実装の方が圧倒的に実行速度が速くなり、速度が大幅に改善されました。

課題の指示で、* You set logits for invalid tokens (those breaking the schema or structure) tonegative infinity.*とあるので、`masked_logits`を作る必要があり、少し不格好になって入る点はありますが。

あと一点著しくスピードを損ねている点があります。それは以下の部分です。

```python
    def check_json(self, next_token_id: int) -> bool:
        next_token_text = self.model.decode(next_token_id)
        return self.checker.check(next_token_text)
```

毎回`next_token_id`を`decode`しています。`decode`は処理が遅いので、毎回呼び出していては処理がとても遅くなってしまいます。そのため、decodeを呼び出す回数はなるべく少なくしたいです。

よって最初と最後に一回ずつ呼び出す形式にします。最初にdecodeを呼び出し、それを辞書にしておき、`check_json`ではその辞書を用いてトークンIDをトークンのテキストの変換を行うようにします。以上のようにしてConstrainedLLMを実行速度を速くしながら作成しました。

おまけで`logits`のソートはbuiltinの`sorted`ではなく、numpyの`argsort`を使うことにより少しだけ高速化しています。

まだいくらでも速くしようはあります。
例えば、そもそも`decode`自体が遅いので、一度も使わないようにする方法です。

`get_path_to_vocab_file`でトークンテキストとトークンIDの対応表のパスをゲットし、それを持ってきてデコードの代わりにその辞書を用いる方法です。

この方法では、この辞書は例えばスペース(" ")がĠとなっていたり、改行("\n)がĊになっていたりするトークン化けと呼ばれる非表示文字を強制的に表示させる方式が取られています。checkerでJSONのチェックをする際にこの非表示文字のせいでうまくいかなくなるのでこれに対応してあげればさらに速くなります。

ただ今回はLLMの入門なのでこのくらいに留めておきます。

あとタブのように以降の文が1意に定まればLLMを介さずに確定させる仕組みで速度を３倍以上早くしました。
