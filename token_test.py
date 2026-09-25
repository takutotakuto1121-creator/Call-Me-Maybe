from llm_sdk import Small_LLM_Model
import json


def main():
    llm = Small_LLM_Model()
    vocab_path = llm.get_path_to_vocab_file()

    with open(vocab_path) as f:
        vocab = json.load(f)

    vocab_rev = {v: k for k, v in vocab.items()}

    print("=== test1: contains \\n ===")
    newline_containing = [
        (tid, text) for tid, text in vocab_rev.items()
        if "\n" in text or "Ċ" in text
    ]
    print(f"count: {len(newline_containing)}")
    for tid, text in newline_containing[:20]:
        print(tid, repr(text))

    print()
    print("=== test2: exactly '\\n' ===")
    exact_newline = [
        (tid, text) for tid, text in vocab_rev.items()
        if text == "\n" or text == "Ċ"
    ]
    print(f"count: {len(exact_newline)}")
    for tid, text in exact_newline:
        print(tid, repr(text))

    print()
    print("=== test3: contains space ===")
    space_containing = [
        (tid, text) for tid, text in vocab_rev.items()
        if " " in text or "Ġ" in text
    ]
    print(f"count: {len(space_containing)}")
    for tid, text in space_containing[:20]:
        print(tid, repr(text))

    print()
    print("=== test4: exactly ' ' (single space) ===")
    exact_space = [
        (tid, text) for tid, text in vocab_rev.items()
        if text == " " or text == "Ġ"
    ]
    print(f"count: {len(exact_space)}")
    for tid, text in exact_space:
        print(tid, repr(text))


if __name__ == "__main__":
    main()
