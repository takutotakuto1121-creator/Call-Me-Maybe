from .parse_json import Options, Parse, FunctionItem
from .constrained_llm import ConstrainedLLM
from .check_json import JsonChecker
from llm_sdk import Small_LLM_Model


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
        "JSON data should be like this.\n"
        "{\n"
        '  "prompt": "What is the sum of 2 and 3?",\n'
        '  "name": "fn_add_numbers",\n'
        '  "parameters": {"a": 2.0, "b": 3.0}\n'
        "}\n"
        "prompt is user's prompt."
        "name is function name you call in order to solve user's question."
        "parameters are parameters of functions you call."
        "this is the list of functions and their features you can choose.\n"
        f"{function_list}"
    )


def main():
    small_llm = Small_LLM_Model()
    jsonchecker = JsonChecker()
    llm = ConstrainedLLM(small_llm, jsonchecker)
    parse = Parse()
    prompts = parse.load_prompts()
    functions = parse.load_functions()
    system_prompt = build_system_prompt(functions)
    # results = '{\n   "prompt": "'
    results = ""
    # for prompt in prompts:
    prompt = prompts[0]
    real_prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{prompt.prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
        # '{\n   "prompt": "'
    )
    results += llm.constrained_generate(real_prompt)
    print(results)


if __name__ == "__main__":
    main()
