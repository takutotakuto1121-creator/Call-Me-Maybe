# Others
## Design decisions
- `pydantic` and `json` are used for validation, because I am used to them.
- ConstrainedLLM calls `decode` only once at the beginning and once at the end, because it is faster.
- JsonChecker does not use a stack. The JSON format was specified in detail, so there was no need to handle nesting.

## Performance analysis
- Accuracy: Quite accurate. More than 90% of the outputs are correct.
- Speed: Meets the subject's requirement of finishing within 5 minutes, though there is still plenty of room for improvement.
- Reliability: Parsing is done thoroughly, so it does not crash. Error handling is also strict.

## Challenges faced
- When building [ConstrainedLLM](constrained.md), I faced the problem of extremely slow execution. The main causes were calling `decode` many times and checking every token in `check_json`. I sped it up by calling `decode` only at the beginning and the end, and by checking tokens in descending order of probability.
- When building [JsonChecker](json_checker.md), I initially tried to first guarantee 100% valid JSON output and then check that it matched the specified format. I even wanted to let the format be specified freely. However, that implementation was too difficult for my current skill level, so I simplified it and solved the problem by implementing only what the subject requires. I would like to take on that implementation once I have improved my skills.

## Testing strategy
You can test by editing the first prompt in `input/function_calling_tests.json` and `input/function_definition.json` however you like, running the following command, and checking the output.

```bash
make test
```

## Example Usage
Leave the files in the input directory as their defaults and run the following command:
```bash
make run
```

## Bonus Part
The following bonuses are supported:
- Advanced error recovery mechanism: after creating the JSON file and writing the output to it, `json.load()` is used to verify that it satisfies the JSON format. If an error occurs, a note asking the model to regenerate without producing that error is appended to the system prompt, and the output is regenerated.
- Test creation: `make test` prints only the output for the first prompt to standard output, making testing easy.
- Visualization of the generation process: when running with `make test` or `make animation`, each token is printed to standard output as it is generated, so the generation process can be seen as an animation.
