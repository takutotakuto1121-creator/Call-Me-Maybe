import json
import argparse
from pydantic import BaseModel, Field, ValidationError

class Options(BaseModel):
    input_prompt: str = Field(default="data/input/function_calling_tests.json")
    input_functions: str = Field(default="data/input/functions_definition.json")
    output_path: str = Field(default="data/output/function_calls.json")

class PromptItem(BaseModel):
    prompt: str

class FunctionCentre(BaseModel):
    type: str

class FunctionItem(BaseModel):
    name: str
    description: str
    parameters: dict[str, FunctionCentre]
    returns: FunctionCentre

class Parse:
    def __init__(self):
        self.options = self.get_options()

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--functions_definition", type=str, default=None)
        parser.add_argument("--input", type=str, default=None)
        parser.add_argument("--output", type=str, default=None)
        return parser.parse_args()

    def get_options(self) -> Options:
        args = self.parse_args()
        key_args = {}
        if args.input is not None:
            key_args["input_prompt"] = args.input
        if args.functions_definition is not None:
            key_args["input_functions"] = args.functions_definition
        if args.output is not None:
            key_args["output_path"] = args.output
        try:
            return Options(**key_args)
        except ValidationError as e:
            raise RuntimeError(f"INvalid Option: {e}")


    def load_json(self, path:str) -> list[dict]:
        # 構文的に正しいJSONか、そもそもfileがあるのかをチェック
        try:
            with open(path) as f:
                json_content = json.load(f)
        except FileNotFoundError as e:
            raise RuntimeError(f"Input file {self.options.input_prompt} not found: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON syntax in {self.options.input_prompt}: {e}")
        # JSONが、[{"prompt": "aaa"}, {"prompt": "bbb"}]
        # この形式のJSONであるかをチェック. topがリスト
        if not isinstance(json_content, list):
            raise RuntimeError(f"Invalid JSON. JSON's top should be list")
        return json_content

    def load_prompts(self) -> list[PromptItem]:
        '''promptsが要件のJSON形式に則っていればloadする。'''
        json_content = self.load_json(self.options.input_prompt)
        # 各要素が適しているかをチェック
        try:
            prompt_items = [PromptItem(**item) for item in json_content]
            return prompt_items
        except ValidationError:
            raise RuntimeError(f'Invalid JSON key: value should be like "prompt": "aaa')

    def load_functions(self) -> list[FunctionItem]:
        '''function_definitionが要件のJSON形式に則っていればloadする。'''
        json_content = self.load_json(self.options.input_functions)
        # 各要素が適しているかどうかをチェック
        try:
            functions_item = [FunctionItem(**item) for item in json_content]
            return functions_item
        except ValidationError:
            raise RuntimeError(f"Invalid JSON ")
