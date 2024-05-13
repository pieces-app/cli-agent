import json
import os
import re

from pieces.settings import Settings

# Used to create a valid file name when opening to "Opened Snippets"
def sanitize_filename(name):
    """ Sanitize the filename by removing or replacing invalid characters. """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name

def export_code_to_file(code, name, language):
    # Sanitize the name to ensure it's a valid filename
    filename = sanitize_filename(name)
    file_extension = get_file_extension(language)

    # Ensure the directory exists, create it if not
    if not os.path.exists(Settings.open_snippet_dir):
        os.makedirs(Settings.open_snippet_dir)

    # Path to save the extracted code
    file_path = os.path.join(Settings.open_snippet_dir, f'{filename}{file_extension}')

    # Writing the extracted code to a new file
    if isinstance(code, str): # Code string raw
        with open(file_path, 'w') as file:
            file.write(code)
    else: # Image bytes data
        with open(file_path, 'wb') as file:
            file.write(bytes(code))

    return file_path

def get_file_extension(language):
    with open(Settings.extensions_dir) as f:
        extension_mapping = json.load(f)

    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extension_mapping.get(language, '.txt')