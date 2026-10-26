# Constrained LLM
So where should we intervene to force the output into the format we want? The answer is the process that produces `logits`, the list of probabilities for the next token. By intervening in this process and manually setting the probability of any unsuitable next token to **-inf**, creating a new `masked logits`, that token can never be chosen as the next token. As a result, token selection picks the highest-probability token among the suitable ones. We improve SimpleLLM to build the following ConstrainedLLM.

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
        # Encode
        token_ids: list[int] = self.model.encode(prompt).tolist()[0]

        for _ in range(max_new_tokens):
            # Get the probabilities of the next token as logits
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)

            # ---- Perform some kind of check here ----
            masked_logits = ...
            # ------------

            # Take the token with the highest probability as next_token_id (logits replaced with masked_logits)
            next_token_id = max(range(len(masked_logits)), key=lambda i: masked_logits[i])
            # Fix the token and loop again to predict the next one
            token_ids.append(next_token_id)

        # Decode
        result = self.model.decode(token_ids)
        return result
```

All we need to do is perform some kind of check at the location above and turn `logits` into `masked_logits`.

The check is done by some checker (`self.checker`), but let's set that aside for now.

For example, the following approach is possible:

```python
masked_logits = []

for index, logit in enumerate(logits):
    if not self.check_json(token_ids, index):
        logit = -math.inf
        masked_logits.append(logit)
```

Since `index` runs from 0 through the number of logits in order, it represents a **token_id**. We check **every** token_id, and if it does not fit the JSON format, its entry in `masked_logits` is set to -inf. As a result, only suitable token IDs can be selected. We should handle the case where everything becomes -inf, but we skip that for simplicity.

However, with this implementation, every time a single token is selected, all token IDs are iterated over and checked, which takes a very long time.

So let's slightly change the order, as follows:

```python
masked_logits = [-math.inf] * len(logits)
sorted_indices = sorted(
    range(len(logits)),
    key=lambda i: logits[i],
    reverse=True
    )

for index in sorted_indices:
    if self.check_json(token_ids, index):
        masked_logits[index] = logits[index]
        break
```

First, we create `sorted_indices`, the indices sorted in descending order of logit. We take indices in this order and check each one, breaking out of the loop as soon as one that fits the JSON format appears.

Checking every index, setting the logits of unsuitable indices to -inf, and taking the index of the maximum remaining logit as the next token ID gives the same index as sorting indices by logit first and taking the first suitable one in order.

So both produce the same result, but the former performs a check on every token each time, requiring an enormous number of checks, while the latter exits the check loop as soon as a suitable token is found, reducing the number of checks by orders of magnitude. This implementation is therefore overwhelmingly faster, and speed improved dramatically.

The subject states *You set logits for invalid tokens (those breaking the schema or structure) to negative infinity.*, so we need to build `masked_logits`, which makes the code a bit awkward.

There is one more spot that severely hurts speed:

```python
    def check_json(self, next_token_id: int) -> bool:
        next_token_text = self.model.decode(next_token_id)
        return self.checker.check(next_token_text)
```

It calls `decode` on `next_token_id` every time. `decode` is slow, so calling it every time makes processing very slow. We therefore want to call `decode` as few times as possible.

So we call it only once at the beginning and once at the end. At the beginning, we call `decode` and store the results in a dictionary, and `check_json` uses that dictionary to convert token IDs into token text. This is how ConstrainedLLM was built while keeping it fast.

As a small extra, sorting `logits` uses numpy's `argsort` instead of the builtin `sorted`, which makes it slightly faster.

There are still many ways to make it faster.
For example, since `decode` itself is slow, one approach is to never use it at all.

`get_path_to_vocab_file` gives the path to the mapping between token text and token IDs, and that dictionary can be used instead of decoding.

In this dictionary, invisible characters are forcibly rendered visible, e.g. a space (" ") becomes Ġ and a newline ("\n") becomes Ċ (so-called token mojibake). These invisible-character representations break the JSON check in the checker, so handling them would make it even faster.

However, since this is an introduction to LLMs, we stop here.

Also, a mechanism that fixes the following text without going through the LLM whenever it is uniquely determined (like tab completion) made it more than 3 times faster.
