from llm_sdk import Small_LLM_Model
from .check_json import JsonChecker, Mode
from .parse_json import FunctionItem
import json
import math
import numpy as np


class ConstrainedLLM:
    def __init__(
        self, model: Small_LLM_Model,
        checker: JsonChecker, animation: bool,
        functions: list[FunctionItem]
    ) -> None:
        self.model = model
        self.functions = {func.name: func for func in functions}
        self.gen_text = ""
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

    def unique_candidate(self, partial: str, words: list[str]) -> str:
        # 候補が1つに絞れるなら、残りの文字列 + 閉じクォートを返す
        matched = [w for w in words if w.startswith(partial)]
        if len(matched) != 1:
            return ""
        return matched[0][len(partial):] + '"'

    def forced_text(self) -> str:
        """今の状態から、次に来る文字列が一意に決まるならそれを返す。"""
        c = self.checker
        s = c.state
        if s.in_escape or s.in_hex or s.in_number or s.tfn_target:
            return ""
        indent = " " * 4
        closing = {c.PROMPT: '"', c.NAME: '"', c.PARAMETER: ""}

        if s.literal_target:
            rest = s.literal_target[s.literal_num:]
            return rest + closing[s.literal_target]

        if s.in_string:
            if s.mode == Mode.NAME_COMMA:
                partial = self.gen_text.rsplit(c.NAME, 1)[-1][1:]
                return self.unique_candidate(partial, list(self.functions))
            if s.mode == Mode.PARAMETER_VALUE_KEY:
                match = self.gen_text.rsplit(c.NAME, 1)[-1].split('"')[1]
                func = self.functions.get(match)
                if func is None:
                    return ""
                params = '"' + self.gen_text.rsplit(c.PARAMETER, 1)[-1]
                partial = params.rsplit('"', 1)[-1]
                unused = [
                    k for k in func.parameters
                    if f'"{k}": ' not in params
                ]
                return self.unique_candidate(partial, unused)
            return ""

        mode = s.mode
        if mode == Mode.START_SPACE:
            return " " * (2 - s.space_num) + "{\n" + indent + c.PROMPT + '"'
        if mode == Mode.START:
            return "{\n" + indent + c.PROMPT + '"'
        if mode == Mode.PROMPT_LINE_BREAK:
            return "\n" + indent + c.PROMPT + '"'
        if mode == Mode.PROMPT_SPACE:
            return " " * (4 - s.space_num) + c.PROMPT + '"'
        if mode in (Mode.PROMPT_VALUE, Mode.NAME_VALUE):
            return '"'
        if mode == Mode.PROMPT_COMMA:
            return ",\n" + indent + c.NAME + '"'
        if mode == Mode.NAME_LINE_BREAK:
            return "\n" + indent + c.NAME + '"'
        if mode == Mode.NAME_SPACE:
            return " " * (4 - s.space_num) + c.NAME + '"'
        if mode == Mode.NAME_COMMA:
            return ",\n" + indent + c.PARAMETER
        if mode == Mode.PARAMETER_LINE_BREAK:
            return "\n" + indent + c.PARAMETER
        if mode == Mode.PARAMETER_SPACE:
            return " " * (4 - s.space_num) + c.PARAMETER
        if mode == Mode.PARAMETER_VALUE_COLON_SPACE:
            return " " if s.exist_colon else ": "
        if mode == Mode.END_LINE_BREAK:
            return "\n  },\n"
        if mode == Mode.END_SPACE:
            return " " * (2 - s.space_num) + "},\n"
        if mode == Mode.END:
            if not s.exist_brace:
                return "},\n"
            return "\n" if s.exist_comma else ",\n"
        return ""

    def force_tokens(self, token_ids: list[int]) -> None:
        """モデルを呼ばずに確定できる部分を token_ids に追加する。"""
        while not self.checker.is_completed():
            text = self.forced_text()
            if not text:
                return
            saved_state = self.checker.snapshot()
            if not self.checker.check(text):
                self.checker.restore(saved_state)
                return
            token_ids.extend(self.model.encode(text).tolist()[0])
            self.gen_text += text
            if self.animation:
                print(text, end="")

    def constrained_generate(self, prompt: str) -> str:
        token_ids = self.model.encode(prompt).tolist()[0]
        self.gen_text = ""

        for _ in range(100):
            self.force_tokens(token_ids)
            if self.checker.is_completed():
                break
            saved_state = self.checker.snapshot()
            logits: list[float] = (
                self.model.get_logits_from_input_ids(token_ids)
            )

            logits_arr = np.array(logits)
            sorted_indices = np.argsort(-logits_arr)
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
                raise RuntimeError(
                    "No valid JSON token found. "
                    "Stopped generating\n"
                )

            next_token_id = max(
                range(len(masked_logits)),
                key=lambda i: masked_logits[i]
            )

            # ---debug---
            # valid_candidates = [
            #     (i, new_logits[i])
            #     for i in range(len(new_logits))
            #     if new_logits[i] != -math.inf
            # ]
            # valid_candidates.sort(key=lambda x: -x[1])
            # top5 = valid_candidates[:5]
            # print(
            #     "TOP5 valid tokens:",
            #     [(self.vocab_rev.get(i), score)
            #      for i, score in top5]
            # )
            # ---debug---

            #  chosen_text = self.vocab_rev.get(next_token_id)
            chosen_text = self.decoded_tokens.get(next_token_id)
            if chosen_text is not None:
                self.checker.check(chosen_text)
                self.gen_text += chosen_text

            if self.animation:
                print(chosen_text, end="")

            token_ids.append(next_token_id)
            if self.checker.is_completed():
                break

        return self.gen_text
