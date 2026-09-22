from .parse_json import Options, Parse, FunctionItem
from .constrained_llm import ConstrainedLLM


def build_system_prompt(functions: list[FunctionItem]) -> list[str]:
    function_list = []
    for func in functions:
        func_description = (
            f"{func.name}: {func.description}"
            f"parameters are {func.parameters}"
            f"returns are {func.returns}"
        )
        function_list.append(func_description)

    return (
        "you are a helpful assistant that generate JSON data. "
        "user asks you some questions and you will generate only JSON data. "
        "JSON data should include dictionaries like this.\n"
        "{\n"
        '   "prompt": "What is the sum of 2 and 3?",\n'
        '   "name": "fn_add_numbers",\n'
        '   "parameters": {"a": 2.0, "b": 3.0}\n'
        "}\n"
        "prompt is user's prompt."
        "name is function name you call in order to solve user's question."
        "parameters are parameters of functions you call."
        "this is the list of functions and their features you can choose.\n"
        f"{function_lst}"
    )


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
    print(results)

if __name__ == "__main__":
    main()
