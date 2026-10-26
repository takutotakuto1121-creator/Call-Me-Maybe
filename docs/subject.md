# Subject Requirement
## Summary
Build a tool that uses an LLM to convert natural-language prompts into structured function calls.

For example, given the prompt *What is the sum of 40 and 2?*, it returns the following:

- Function name: fn_add_numbers
- Arguments: {"a": 40.0, "b": 2.0}

The output must be 100% valid JSON, achieved using **Constrained Decoding**.
## LLM Model
**Qwen/Qwen3-0.6B** is used.
Using `torch`, `transformers`, `huggingface_hub`, etc. directly is forbidden; the Small_LLM_Model class in llm_sdk is used as a wrapper.
Small_LLM_Model provides the following methods:
1. def encode(self, text: str) -> torch.Tensor:  
Encodes a string.
2. def decode(self, ids: torch.Tensor | list[int]) -> str:  
Decodes a list of token IDs.
3. def get_logits_from_input_ids(self, input_ids: list[int]) -> list[float]:  
Takes a list of token IDs and returns the list of probabilities for the next token based on it.
4. def get_path_to_vocab_file(self) -> str:  
Returns the path to the mapping (dictionary) between token IDs and tokens.

## Constrained Decoding
When given text, an LLM splits it into minimal units such as words (tokens) and assigns a numeric ID to each unit (encoding). It then takes that list of token IDs and predicts the next token. This is repeated many times: the model keeps predicting the next token, and finally converts the IDs back into text (decoding) and outputs it.

**Constrained Decoding** intervenes in the step that predicts the next token so that the output follows a specified format.

In this project, Constrained Decoding is used to guarantee 100% valid JSON output.

## Performance and Reliability
The output must satisfy the following conditions:
- Function selection and argument selection must be more than 90% accurate.
- JSON output must be 100% valid.
- It must run within 5 minutes on standard hardware.
- Error handling must be flawless.

## Input Files
The program receives a JSON file containing prompts in the following format:
```json
[
  {
    "prompt": "What is the sum of 2 and 3?"
  },
  {
    "prompt": "What is the sum of 265 and 345?"
  },
  {
    "prompt": "Greet shrek"
  },
  {
    "prompt": "Greet john"
  },
  {
    "prompt": "Reverse the string'hello'"
  }
  ...
]
```

It also receives a JSON file describing the available functions:
```json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {
        "type": "number"
      },
      "b": {
        "type": "number"
      }
    },
    "returns": {
      "type": "number"
    }
  },
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  {
    "name": "fn_reverse_string",
    "description": "Reverse a string and return the reversed result.",
    "parameters": {
      "s": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  ...
]
```

## Output Files
The program outputs a JSON file in the following format. It must be 100% valid JSON, and its fields must also be produced by **Qwen/Qwen3-0.6B** with more than 90% accuracy.
```json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {
        "type": "number"
      },
      "b": {
        "type": "number"
      }
    },
    "returns": {
      "type": "number"
    }
  },
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
  {
    "name": "fn_reverse_string",
    "description": "Reverse a string and return the reversed result.",
    "parameters": {
      "s": {
        "type": "string"
      }
    },
    "returns": {
      "type": "string"
    }
  },
...
]
```
