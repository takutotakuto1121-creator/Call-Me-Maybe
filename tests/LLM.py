from llm_sdk import Small_LLM_Model


class SimpleLLM:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model

    def generate(
            self, prompt: str, max_new_tokens: int = 50
            ) -> str:
        token_ids: list[int] = self.model.encode(prompt).tolist()[0]
        eos_token_id = self.model._tokenizer.eos_token_id
        for _ in range(max_new_tokens):
            logits: list[float] = self.model.get_logits_from_input_ids(token_ids)
            next_token_id = max(range(len(logits)), key=lambda i: logits[i])
            if next_token_id == eos_token_id:
                break
            token_ids.append(next_token_id)
        result = self.model.decode(token_ids)
        return result


def main():
    print("=== Instanciate SLM ===")
    llm = Small_LLM_Model()
    llm_simple = SimpleLLM(llm)
    print()

    # print("== first test ==")
    # prompt = "What is the sum of 40 and 2"
    # print("prompt: ")
    # print(prompt)
    # print()
    # result = llm_simple.generate(prompt)
    # print("result: ")
    # print(result)
    # print()

    print("== second test ==")
    system_prompt = "You are a helpful assistant that answers in JSON"
    user_prompt = "Give me information about Harry Potter and the Order of Phoenix pleas ansewer in JSON"
    prompt2 = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    result = llm_simple.generate(prompt2, max_new_tokens=200)
    print("result: ")
    print(result)
    print()

if __name__ == "__main__":
    main()
