# Script fpr loading results data
import os
import json

def read_json_files(folder_path):
    # List all files in the given folder
    files = os.listdir(folder_path)
    
    # Filter out JSON files
    json_files = [file for file in files if file.endswith('.json')]
    
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        
        # Open and read the JSON file
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                print(f"Contents of {json_file}:")
                print(json.dumps(data, indent=4))  # Pretty print the JSON
            except json.JSONDecodeError as e:
                print(f"Error reading {json_file}: {e}")

# Example usage
folder_path = '/path/to/your/folder'
read_json_files(folder_path)
