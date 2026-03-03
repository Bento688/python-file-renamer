import re
import sys
from pathlib import Path


def standardize_name(filename: str):
    """

    STANDARDIZE A FILE NAME OR A INTO KEBAB-CASE

    """

    # 1. use pathlib to get the stem (name) and suffix (extension)

    path = Path(filename)

    name = path.stem

    ext = path.suffix

    # 2. insert spaces before uppercase letters

    # 'ReactProject' -> ' React Project'

    name_spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)

    # 3. replace non-alphanumeric characters with spaces

    # 'my_cool' -> 'my cool'

    name_clean = re.sub(r"[^a-zA-Z0-9]", " ", name_spaced)

    # make them into an array of words

    words = name_clean.split()

    # join the words in the array with hyphens AND then lowercase them

    standardized_name = "-".join(words).lower()

    # re-attach the extension name

    if ext:

        # keep extensions lowercase, just in case

        standardized_name += ext.lower()

    return standardized_name


def batch_rename(target_dir_path: Path):
    """

    traverses a directory and renames files and folders from the bottom up

    """

    target_path = target_dir_path.resolve()

    if not target_path.is_dir():

        print(f"Error: Directory '{target_path}' not found.")

        return

    # We must rename from the bottom-up (deepest files/folders first).

    # Path.rglob('*') gets EVERYTHING, but we need to sort it so the longest

    # paths (deepest files) come first.

    all_paths = list(target_path.rglob("*"))

    all_paths.sort(key=lambda p: len(p.parts), reverse=True)

    for current_path in all_paths:

        # get the new name

        new_name = standardize_name(current_path.name)

        if current_path.name != new_name:

            # construct the new path

            new_path = current_path.parent / new_name

            try:

                current_path.rename(new_path)

                type_label = "Folder" if current_path.is_dir() else "File"

                print(f"Renamed {type_label}:\n  {current_path.name} \n  -> {new_name}\n")

            except Exception as e:

                print(f"Failed to rename {current_path}: {e}")


if __name__ == "__main__":

    # check if command line argument is provided

    if len(sys.argv) < 2:

        print("Usage: python script.py <target_directory>")

        print("Example: python script.py .")

        sys.exit(1)

    # The second (sys.argv[1]) is the directory path.

    # The first argument (sys.argv[0]) is the script name.

    target_arg = sys.argv[1]

    target_directory = Path(target_arg)

    print("WARNING: This script will recursively modify file and folder names.")

    print("Please ensure you have a backup of your target directory.\n")

    # Print the resolved absolute path so the user knows exactly what they are affecting

    print(f"Targeting: {target_directory.resolve()}")

    confirm = input(f"Are you sure you want to rename contents here? (y/n): ")

    if confirm.lower() == "y":

        batch_rename(target_directory)

        print("Renaming process complete.")

    else:

        print("Operation cancelled.")
