import os
import re


class FileManager:

    DIRECTORY = re.compile(r'[\\/]([^\\/]*)')
    DRIVE_LETTER = re.compile(r'^(\w+):[\\/]')
    ROOT = re.compile(r'^(\w+)[\\/]')

    def __init__(self):
        pass

    @staticmethod
    def create_dir(filepath: str) -> None:
        if os.path.exists(filepath):
            return

        # Get all directories from filepath.
        directories = FileManager.DIRECTORY.findall(filepath)
        # Check if drive letter was included in filepath.
        drive_letter = FileManager.DRIVE_LETTER.search(filepath)
        if drive_letter:
            prefix = f"{drive_letter.group(1)}:/"
        else:
            # Drive letter was not included, so create directory in current
            # directory.
            prefix = os.getcwd()
            # The first directory needs to be added as it doesn't have
            # a '/' or '\' before it, for the regex search.
            directories.insert(0, FileManager.ROOT.search(filepath).group(1))

        index_range = 0
        while True:
            # Iterate through all directories and create the ones that don't exist.
            index_range += 1
            if index_range > len(directories):
                # Break when all directories have been created
                break
            # Form path from directories, and normalize for user OS.
            formed_path = os.path.normpath(
                os.path.join(prefix, *directories[:index_range])
            )

            if os.path.exists(formed_path):
                continue
            else:
                os.mkdir(formed_path)


