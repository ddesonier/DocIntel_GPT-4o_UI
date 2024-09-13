import json
import os
import argparse

def generate_schema_from_json(data, key=None):
    """
    Recursively generate a JSON schema from the given JSON data.
    """
    if isinstance(data, dict):
        properties = {k: generate_schema_from_json(v, k) for k, v in data.items()}
        return {"type": "object", "properties": properties}
    elif isinstance(data, list):
        if data:  # Non-empty list
            return {"type": "array", "items": generate_schema_from_json(data[0])}
        else:  # Empty list
            return {"type": "array"}
    elif isinstance(data, str):
        # Special handling for date-like strings, adjust the pattern as needed
        if key and key.lower().replace(" ", "_") == "date_quoted":
            return {"type": "string", "pattern": "^[A-Z]{3} [0-9]{2}, [0-9]{4}$"}
        return {"type": "string"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    else:
        return {}

def main():
    parser = argparse.ArgumentParser(description="Generate JSON schema from a JSON file.")
    parser.add_argument("input_file", help="Path to the input JSON file")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = os.path.splitext(input_file)[0] + "_schema.json"

    # Read the JSON data from the input file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Generate the JSON schema
    schema = generate_schema_from_json(data)

    # Write the generated schema to the output file
    with open(output_file, 'w') as file:
        json.dump(schema, file, indent=4)

    print(f"Schema generated and saved to {output_file}")

if __name__ == "__main__":
    main()