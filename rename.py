#!/usr/bin/env python3

import argparse
import re
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


def batch_rename(target_dir_path: Path, is_dry_run: bool = False):
    """
    Traverses the immediate contents of a directory and renames them.
    If is_dry_run is True, it only prints the propose changes.
    """

    target_path = target_dir_path.resolve()

    if not target_path.is_dir():
        print(f"Error: Directory '{target_path}' not found.")
        return

    # iterdir() ONLY gets the immediate children (no recursion)
    all_paths = list(target_path.iterdir())

    for current_path in all_paths:

        # make sure that hidden files aren't touched -> .git .env
        if current_path.name.startswith("."):
            continue

        # get the new name
        new_name = standardize_name(current_path.name)

        if current_path.name != new_name:
            # construct the new path
            new_path = current_path.parent / new_name

            try:
                # collision handling
                if new_path.exists():
                    original_stem = new_path.stem
                    original_suffix = new_path.suffix
                    counter = 2

                    while new_path.exists():
                        # stitch together: stem + -counter + suffix (e.g. my-file-2.txt)
                        incremented_name = f"{original_stem}-{counter}{original_suffix}"
                        new_path = current_path.parent / incremented_name
                        counter += 1

                type_label = "Folder" if current_path.is_dir() else "File"

                if is_dry_run:
                    print(
                        f"[DRY RUN] Would rename {type_label}:\n  {current_path.name} \n  -> {new_path.name}\n"
                    )
                else:
                    # (new_path is now guaranteed to be unique)
                    current_path.rename(new_path)
                    print(f"Renamed {type_label}:\n  {current_path.name} \n  -> {new_path.name}\n")

            except Exception as e:
                print(f"Failed to rename {current_path}: {e}")


if __name__ == "__main__":

    # 1. Initialize Argument Parser
    parser = argparse.ArgumentParser(
        description="Rename immediate files and folders to kebab-case."
    )

    # 2. Define expected arguments
    parser.add_argument(
        "target_directory", type=str, help="The directory to target (e.g., . for current)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print proposed changes without mutating the disk"
    )

    # 3. Parse the user's temrinal input
    args = parser.parse_args()
    target_directory = Path(args.target_directory)

    # 4. Execute based on the presenf of the flag
    if args.dry_run:
        print("--- DRY RUN MODE ACTIVATED: No files will be modified ---\n")
        print(f"Targeting: {target_directory.resolve()}\n")
        batch_rename(target_directory, is_dry_run=True)
    else:
        print("WARNING: This script will modify immediate file and folder names.")
        print(f"Targeting: {target_directory.resolve()}")

        confirm = input(f"Are you sure you want to rename contents here? (y/n): ")

        if confirm.lower() == "y":
            batch_rename(target_directory, is_dry_run=False)
            print("Renaming process complete.")
        else:
            print("Operation cancelled.")
