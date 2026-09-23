from llm_sdk import Small_LLM_Model
from .check_json import JsonChecker
import json
import math

class ConstrainedLLM:
    def __init__(self, model: Small_LLM_Model, checker: JsonChecker):
        self.model = model
        self.eos_token_id = self.model._tokenizer.eos_token_id
        self.vocab_path = self.model.get_path_to_vocab_file()
        with open(self.vocab_path) as f:
            self.vocab = json.load(f)
        self.vocab_rev = {v: k for k, v in self.vocab.items()}
        self.checker = checker

    def check_json(self, next_token_id: int) -> bool:
        next_token_text = self.vocab_rev.get(next_token_id)
        if next_token_text is None:
            return False
        return self.checker.check(next_token_text)

    def constrained_generate(self, prompt: str) -> str:
        token_ids = self.model.encode(prompt).tolist()[0]
        prompt_token_length = len(token_ids)

        for _ in range(200):
            saved_state = self.checker.snapshot()
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)
            new_logits = []
            for next_token_id, logit in enumerate(logits):
                if not self.check_json(next_token_id):
                    logit = -math.inf
                self.checker.restore(saved_state)
                new_logits.append(logit)
            next_token_id = max(range(len(new_logits)), key=lambda i: new_logits[i])
            # ---debug---
            valid_candidates = [(i, new_logits[i]) for i in range(len(new_logits)) if new_logits[i] != -math.inf]
            valid_candidates.sort(key=lambda x: -x[1])
            top5 = valid_candidates[:5]
            # ---debug---
            print("TOP5 valid tokens:", [(self.vocab_rev.get(i), score) for i, score in top5])  
            if next_token_id == self.eos_token_id or self.checker.is_completed():
                break
            chosen_text = self.vocab_rev.get(next_token_id)
            if chosen_text is not None:
                self.checker.check(chosen_text)
            # print(chosen_text, end = "")                
            token_ids.append(next_token_id)

        generated_ids = token_ids[prompt_token_length:]
        result = self.model.decode(generated_ids)
        return result
