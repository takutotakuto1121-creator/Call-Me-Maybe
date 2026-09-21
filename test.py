from llm_sdk import Small_LLM_Model
import json

def main():
    print("=== Instanciate LLM ===")
    llm = Small_LLM_Model()
    print()
    print("== Encoding test ==")
    original_str = "what is the sum of 42 and 2"
    token_ID = llm.encode(original_str).tolist()[0]
    print(token_ID)
    print()
    print("== Decoding test ==")
    decoding_str = llm.decode(token_ID)
    print(decoding_str)
    print()
    print("== getting logits test ==")
    logits = llm.get_logits_from_input_ids(token_ID)
    print(f"max: {max(logits)}")
    print(f"min: {min(logits)}")
    print(f"average: {sum(logits)/len(logits)}")
    print()
    print("== vocab test ==")
    vocab_path = llm.get_path_to_vocab_file()
    print(vocab_path)
    with open(vocab_path, "r") as f:
        vocab = json.load(f)
    print(f"total vocabulary: {len(vocab)}")
    target = "{"
    for item in vocab:
        if target == vocab.keys():
            print(f"{item}'s token ID is {vocab[item]}")
    


if __name__ == "__main__":
    main()
