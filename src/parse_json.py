import json
import sys
import args
from pydantic import BaseModel, Field

class Options(BaseModel):
    input_prompt: str = Field(default="data/input/function_calling_tests.json")
    input_functions: str = Field(default="data/input/functions_defin")
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
        self.options = get_options()

    def get_options(self) -> Options:
        arg = args.parse_args()
        try:
            options = Options(
                input_prompt=arg.input
                input_functions=arg.function_definition
                output_path=arg.output
            )
            return options
        except ValidationError as e:
            raise RuntimeError("Invalid option: {e}")

    def load_json(self) -> list[dict]:
        # 構文的に正しいJSONか、そもそもfileがあるのかをチェック
        try:
            with open(self.options.input_prompt) as f:
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
        json_content = self.load_json()
        # 各要素が適しているかをチェック
        try:
            prompt_items = [PromptItem(**item) for item in json_content]
            return prompt_items
        except ValidationError:
            raise RuntimeError(f'Invalid JSON key: value should be like "prompt": "aaa')

    def load_functions(self) -> list[FunctionItem]:
        '''function_definitionが要件のJSON形式に則っていればloadする。'''
        json_content = self.load_json()
        # 各要素が適しているかどうかをチェック
        try:
            functions_item = [FunctionItem(**item) for item in json_content]
            return functions_item
        except ValidationError:
            raise RuntimeError(f"Invalid JSON ")
