import json
import sys

def open_json_file(file_path):
    """
    Opens a JSON file and returns its content.

    Parameters:
    file_path (str): The path to the JSON file to be opened.
    """
    try:
        with open(file_path, 'r') as file:
            #json_object = json.dumps(file, indent = 4) 
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(file_path)
        data = open_json_file(file_path)
        if data is not None:
            print(json.dumps(data, indent=4))
    else:
        print("Please provide the path to a JSON file as an argument.")