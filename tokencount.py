import tiktoken
import json
import sys
import argparse

def open_json_file(file_path, model):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None

def count_tokens(text, model):
    tokenizer =  tiktoken.encoding_for_model(model)
    text = json.dumps(text)
    # Tokenize the text
    tokens = tokenizer.encode(text)

    # Return the number of tokens
    return len(tokens)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count tokens in a JSON file.")
    parser.add_argument('--file_path', type=str)
    parser.add_argument('--model', type=str, default='gpt-4')
    
    args = parser.parse_args()

    if args.file_path:
        data = open_json_file(args.file_path,args.model)
        if data is not None:
            print(f"Number of tokens: {count_tokens(data, model=args.model)}")
    else:
        print("Missing path to a JSON file as an argument.")

# Example Run
# python tokencount.py --file_path "path/to/file.json" --model "gpt-4"