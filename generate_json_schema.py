import json
import os
import sys
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

def generate_schema(data):
    """
    Recursively generate a JSON schema from the given JSON data.

    Args:
        data (dict): The JSON data to generate the schema from.

    Returns:
        dict: The generated JSON schema.
    """
    if isinstance(data, dict):
        properties = {k: generate_schema(v) for k, v in data.items()}
        return {"type": "object", "properties": properties, "required": list(data.keys())}
    elif isinstance(data, list):
        if data:  # Non-empty list
            return {"type": "array", "items": generate_schema(data[0])}
        else:  # Empty list
            return {"type": "array"}
    elif isinstance(data, str):
        return {"type": "string"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    else:
        return {}

def validate_json(data, schema):
    """
    Validate JSON data against a schema.

    Args:
        data (dict): The JSON data to validate.
        schema (dict): The JSON schema to validate against.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    for error in errors:
        print(f"Validation error: {error.message}")
    return not errors

def main():
    # Check if the file path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python generate_json_schema.py <path_to_json_file>")
        sys.exit(1)

    # Path to the JSON file
    json_file_path = sys.argv[1]

    # Read the JSON file
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Generate the JSON schema
    json_schema = generate_schema(json_data)

    # Validate the JSON data against the generated schema
    is_valid = validate_json(json_data, json_schema)
    if is_valid:
        print("The JSON data is valid against the generated schema.")
    else:
        print("The JSON data is not valid against the generated schema.")

    # Save the generated schema to a file
    schema_file_path = os.path.splitext(json_file_path)[0] + "_schema.json"
    with open(schema_file_path, "w", encoding="utf-8") as schema_file:
        json.dump(json_schema, schema_file, ensure_ascii=False, indent=4)

    print(f"JSON schema has been saved to {schema_file_path}")

if __name__ == "__main__":
    main()