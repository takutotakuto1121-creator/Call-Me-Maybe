from parse_json import Options, Parse, FunctionItem
from constrained_llm import ConstrainedLLM


def build_system_prompt(functins: list[FunctionItem]) -> str:
    

def main():
    llm = ConstrainedLLM()
    parse = Parse()
    prompts = parse.load_prompts()
    functions = parse.load_functions()
    system_prompt = build_system_prompt(functions)
    results = []
    for prompt in prompts:
        real_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n<think>\n"
        )
        results.append(llm.constrained_generate(prompt))