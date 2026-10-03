from llm_sdk import Small_LLM_Model
from .check_json import JsonChecker
import json
import math
import sys

class ConstrainedLLM:
    def __init__(self, model: Small_LLM_Model, checker: JsonChecker, animation: bool):
        self.model = model
        self.vocab_path = self.model.get_path_to_vocab_file()
        with open(self.vocab_path) as f:
            self.vocab = json.load(f)
        self.vocab_rev = {v: k for k, v in self.vocab.items()}
        self.checker = checker
        self.animation = animation
        self.decoded_tokens = {
            token: self.model.decode(token)
            for token in self.vocab.values()
            }

    def check_json(self, next_token_id: int) -> bool:
        # next_token_text = self.vocab_rev.get(next_token_id)
        next_token_text = self.decoded_tokens.get(next_token_id)
        if next_token_text is None:
            return False
        return self.checker.check(next_token_text)

    def constrained_generate(self, prompt: str) -> str:
        token_ids = self.model.encode(prompt).tolist()[0]
        prompt_token_length = len(token_ids)

        for _ in range(100):
            saved_state = self.checker.snapshot()
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)
            sorted_indices = sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)
            masked_logits = [-math.inf] * len(logits)
            valid_token_found = False

            for token_id in sorted_indices:
                if self.check_json(token_id):
                    masked_logits[token_id] = logits[token_id]
                    self.checker.restore(saved_state)
                    valid_token_found = True
                    break
            
            else:
                self.checker.restore(saved_state)
            
            if not valid_token_found:
                raise RuntimeError("No valid JSON token found. Stopped generating\n")

            next_token_id = max(range(len(masked_logits)), key=lambda i: masked_logits[i])

            # ---debug---
            # valid_candidates = [(i, new_logits[i]) for i in range(len(new_logits)) if new_logits[i] != -math.inf]
            # valid_candidates.sort(key=lambda x: -x[1])
            # top5 = valid_candidates[:5]
            # print("TOP5 valid tokens:", [(self.vocab_rev.get(i), score) for i, score in top5])
            # ---debug---

            # chosen_text = self.vocab_rev.get(next_token_id)
            chosen_text = self.decoded_tokens.get(next_token_id)
            if chosen_text is not None:
                self.checker.check(chosen_text)

            if self.animation:
                print(chosen_text, end = "")
                sys.stdout.flush()
            
            token_ids.append(next_token_id)
            if self.checker.is_completed():
                break

        generated_ids = token_ids[prompt_token_length:]
        result = ""
        for id in generated_ids:
            result += self.decoded_tokens.get(id)
        return result
