*This project has been created as part
of the 42 curriculum by tsugimot*
# Call Me Maybe
## Description
**Call Me Maybe** is a solo project in Milestone 3 of the 42 cursus.
The goal is to write a program that uses *Constrained Decoding* to force an LLM to output JSON in a specified format. See the [subject requirements](docs/subject.md) for details.

## Instruction
Run the program with the following command:
```bash
make run
```

To print only the output for the first prompt in the input file to standard output, run:
```bash
make test
```

To run while printing the token generation process to standard output, run:
```bash
make animation
```

To specify the input and output files, run it as follows:
```bash
uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]
```

## Algorithm explanation
### Parsing
Parsing is nothing new, so it is omitted here; the code speaks for itself. Validation is done with `pydantic` and `json`.

### Implementation using the LLM
First, consider how to make Small_LLM_Model generate text in the usual way. See [here](docs/simple_llm.md).

### Constrained Decoding
Next, consider how to modify the SimpleLLM built above so that it follows a specified JSON format. See [here](docs/constrained.md).

Then build a checker that verifies whether a string conforms to the JSON format specified in the subject requirements. See [here](docs/json_checker.md).

## Resources
### AI Usage
The code is written by hand.
AI was used to resolve flake8 and mypy errors.

### Resources
To be written later.

## Others
For additional bonus information, see [here](docs/others.md).
