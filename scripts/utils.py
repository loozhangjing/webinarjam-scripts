import os
import sys
import pathlib
import logging

logging.basicConfig(level=logging.INFO)

def confirm_if_overwriting_file(output_file_path: pathlib.Path, exit_if_no_overwrite=True):
    if os.path.isfile(output_file_path) is True:
        print()
        overwrite = input(f"{output_file_path} already exists, overwrite? [y/n] ")
        print()

        overwrite = overwrite.lower().strip()

        if overwrite != "y" and overwrite != "yes":
            logging.info(f"{output_file_path} remains unchanged")
            if exit_if_no_overwrite is True:
                sys.exit()

        if exit_if_no_overwrite is True:
            logging.info(f"overwriting {output_file_path}")
