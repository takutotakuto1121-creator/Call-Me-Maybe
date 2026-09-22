from llm_sdk import Small_LLM_Model
import json
import math

class ConstrainedLLM:
    def __init__(self, model: Small_LLM_Model):
        self.model = model
        self.eos_token_id = self.model._tokenizer.eos_token_id
        self.vocab_path = self.model.get_path_to_vocab_file()
        with open(self.vocab_path) as f:
            self.vocab = json.load(f)
        self.vocab_rev = {v: k for k, v in self.vocab.items()}

    def check_json(self, token_ids: list[int], index: int) -> bool:
        new_ids = token_ids.append(index)
        new_str = self.model.decode(new_ids)
        # ここでJSONの形式かをチェック
        return True

    def constrained_generate(self, prompt: str) -> str:
        token_ids = self.model.encode(prompt).tolist()[0]
        prompt_length = len(prompt)

        for _ in range(200):
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)
            new_logits = []
            for index, logit in enumerate(logits):
                if not self.check_json(token_ids, index):
                    logit = -math.inf
                new_logits.append(logit)
            next_token_id = max(range(len(new_logits)), key=lambda i: new_logits[i])
            if next_token_id == self.eos_token_id:
                break
            token_ids.append(next_token_id)

        generated_ids = token_ids[prompt_length:]
        result = self.model.decode(generated_ids)
        return result


if __name__ == "__main__":

            


            

