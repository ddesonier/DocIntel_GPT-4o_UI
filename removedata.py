import shutil
import os
import sys


def delete_folder_contents(folder_path):
    """
    Deletes all the contents of a specified folder, including files and subfolders.

    Parameters:
    folder_path (str): The path to the folder whose contents are to be deleted.
    """
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate over all the items in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                # If it's a file, delete it
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # If it's a directory, delete its contents and the directory itself
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f"The folder {folder_path} does not exist.")

def delete_folder_files(folder_path):
    """
    Deletes all files within a specified folder and its subfolders, but leaves the folders intact.

    Parameters:
    folder_path (str): The path to the folder whose file contents are to be deleted.
    """
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Walk through the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Delete the file
                    os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f"The folder {folder_path} does not exist.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        delete_folder_files(folder_path)
    else:
        print("Please provide a folder path as an argument.")