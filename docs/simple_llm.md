# Simple LLM
Most people usually interact with LLMs through a GUI, exchanging text in a conversational format. Let's think about how to implement this using only `encode`, `decode`, and `get_logits_from_input_ids`.

When given text, an LLM splits it into minimal units such as words (tokens) and assigns a numeric ID to each unit (encoding). It then takes that list of token IDs and predicts the next token. This is repeated many times: the model keeps predicting the next token, and finally converts the IDs back into text (decoding) and outputs it.

Translated directly into code, this looks like the following:

```python
from llm_sdk import Small_LLM_Model


class SimpleLLM:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model

    def generate(
            self, prompt: str, max_new_tokens: int = 50
            ) -> str:
        # Encode
        token_ids: list[int] = self.model.encode(prompt).tolist()[0]

        for _ in range(max_new_tokens):
            # Get the probabilities of the next token as logits
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)

            # Take the token with the highest probability as next_token_id
            next_token_id = max(range(len(logits)), key=lambda i: logits[i])
            # Fix the token and loop again to predict the next one
            token_ids.append(next_token_id)

        # Decode
        result = self.model.decode(token_ids)
        return result
```

This is how an LLM is used when nothing is constrained.

So where should we intervene to force the output into the format we want? The answer is the process that produces `logits`, the list of probabilities for the next token. By intervening in this process and manually setting the probability of any unsuitable next token to *-inf*, creating a new `masked logits`, we can achieve this.
