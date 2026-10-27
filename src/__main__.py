from .parse_json import Parse, FunctionItem
from .constrained_llm import ConstrainedLLM
from .check_json import JsonChecker
from llm_sdk import Small_LLM_Model
from typing import Any
from pydantic import BaseModel, ValidationError
import pathlib


class FunctionCallResult(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, Any]


def build_system_prompt(functions: list[FunctionItem]) -> str:
    function_list = ""
    for func in functions:
        params = ", ".join(
            f"{key}: {item.type}" for key, item in func.parameters.items()
        )
        function_list += f"{func.name}({params}): {func.description}\n"

    return (
        "Output JSON: the user's prompt, the name of the function to call, "
        "and its parameters.\n"
        'Example: {"prompt": "What is the sum of 2 and 3?", '
        '"name": "fn_add_numbers", "parameters": {"a": 2.0, "b": 3.0}}\n'
        "Functions:\n"
        f"{function_list}"
    )


def build_param_types(
    functions: list[FunctionItem]
) -> dict[str, dict[str, str]]:
    return {
        func.name: {k: v.type for k, v in func.parameters.items()}
        for func in functions
    }


def make_json_output(system_prompt: str) -> None:
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
    functions = parse.load_functions()
    param_types = build_param_types(functions)
    json_checker = JsonChecker(param_types)
    llm = ConstrainedLLM(small_llm, json_checker, animation, functions)

    prompts = parse.load_prompts()

    if test:
        prompt = prompts[0]
        llm.checker = JsonChecker(param_types)
        result = ""
        # print(results)
        # for prompt in prompts:
        real_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt.prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        result += llm.constrained_generate(real_prompt)

    else:
        results = "[\n"
        for prompt in prompts:
            llm.checker = JsonChecker(param_types)
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

        path = pathlib.Path(parse.options.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(parse.options.output_path, mode="w") as f:
            f.write(results)
        try:
            content = parse.load_json(
                parse.options.output_path
            )
            [FunctionCallResult(**item) for item in content]
        except RuntimeError as e:
            system_prompt += f"DON'T make this error {e}"
            make_json_output(system_prompt)
        except ValidationError as e:
            system_prompt += f"DON'T make this error {e}"
            make_json_output(system_prompt)


def main() -> None:
    parse = Parse()
    functions = parse.load_functions()
    system_prompt = build_system_prompt(functions)
    make_json_output(system_prompt)


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        print(f"[Error]{e}")
