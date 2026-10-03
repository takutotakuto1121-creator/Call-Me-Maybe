from .parse_json import Options, Parse, FunctionItem
from .constrained_llm import ConstrainedLLM
from .check_json import JsonChecker
from llm_sdk import Small_LLM_Model
import sys
from typing import Any
from pydantic import BaseModel, ValidationError


class FunctionCallResult(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, Any]


def build_system_prompt(functions: list[FunctionItem]) -> list[str]:
    function_list = ""
    for func in functions:
        func_description = (
            f"name: {func.name}\n"
            f"description: {func.description}\n"
            f"parameters: {func.parameters}\n"
            f"returns: {func.returns}\n\n"
        )
        function_list += func_description

    return (
        "you are a helpful assistant that generate JSON data. "
        "user asks you some questions and you will generate only JSON data. "
        "JSON data should be like this.\n"
        "  {\n"
        '    "prompt": "What is the sum of 2 and 3?",\n'
        '    "name": "fn_add_numbers",\n'
        '    "parameters": {"a": 2.0, "b": 3.0}\n'
        "  },\n"
        "prompt is user's prompt."
        "name is function name you call in order to solve user's question."
        "parameters are parameters of functions you call."
        "this is the list of functions and their features you can choose.\n"
        f"{function_list}"
    )


def make_json_output(system_prompt: str):
    parse = Parse()
    args = parse.parse_args()
    if args.test is not None:
        test = True
    else:
        test = False
    if args.animation is not None:
        animation = True
    else:
        animation = False

    small_llm = Small_LLM_Model()
    json_checker = JsonChecker()
    llm = ConstrainedLLM(small_llm, json_checker, animation)

    prompts = parse.load_prompts()
    functions = parse.load_functions()

    if test:
        prompt = prompts[0]
        llm.checker = JsonChecker()
        result = ""
        # print(results)
        # for prompt in prompts:
        real_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt.prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        result += llm.constrained_generate(real_prompt)
        print(result)

    else:
        results = "[\n"
        for prompt in prompts:
            llm.checker = JsonChecker()
            result = ""
            # print(results)
            # for prompt in prompts:
            real_prompt = (
                f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                f"<|im_start|>user\n{prompt.prompt}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            result += llm.constrained_generate(real_prompt)
            results += result
        results = results[:-2]
        results += "\n]"
        with open("data/output/function_calling_results.json", mode="w") as f:
            f.write(results)
        try:
            content = parse.load_json("data/output/function_calling_results.json")
            [FunctionCallResult(**item) for item in content]
        except RuntimeError as e:
            system_prompt += f"DON'T make this error {e}"
            make_json_output(system_prompt)
        except ValidationError as e:
            system_prompt += f"DON'T make this error {e}"
            make_json_output(system_prompt)


def main():
    parse = Parse()
    functions = parse.load_functions()
    system_prompt = build_system_prompt(functions)
    make_json_output(system_prompt)


if __name__ == "__main__":
    main()
