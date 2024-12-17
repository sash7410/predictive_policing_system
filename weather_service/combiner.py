import os
from pathlib import Path

# Define directories to ignore
IGNORE_DIRS = {
    '.venv',
    'venv',
    'env',
    'build',
    'dist',
    '__pycache__',
    'node_modules',
    '.git',
    '.idea',
    '.vscode',
    'weather_service_v1.egg-info',
    '.pytest_cache',
    'scripts'
}


def combine_files(directory_path, output_file='combined_output.txt'):
    """
    Recursively combines all files in the specified directory and its subdirectories into a single output file,
    completely skipping ignored directories.

    Args:
        directory_path (str): Path to the directory containing files to combine
        output_file (str): Name of the output file (default: 'combined_output.txt')
    """
    try:
        # Convert to Path object for better path handling
        directory = Path(directory_path)

        # Check if directory exists
        if not directory.is_dir():
            raise NotADirectoryError(f"'{directory_path}' is not a valid directory")

        # Track processed files count
        processed_files = 0
        skipped_dirs = set()

        # Create or overwrite the output file
        with open(directory / output_file, 'w', encoding='utf-8') as outfile:
            # Walk through directory structure manually to have better control
            for root_path in directory.iterdir():
                # Skip completely if it's in ignored directories
                if root_path.is_dir():
                    if root_path.name in IGNORE_DIRS or any(parent.name in IGNORE_DIRS for parent in root_path.parents):
                        skipped_dirs.add(root_path.name)
                        continue

                    # Process files in non-ignored directories
                    for file_path in root_path.rglob('*'):
                        if not file_path.is_file() or file_path.name == output_file:
                            continue

                        # Skip if any parent directory is in ignore list
                        if any(parent.name in IGNORE_DIRS for parent in file_path.parents):
                            continue

                        # Process the file
                        relative_path = file_path.relative_to(directory)

                        # Write filename and path as a header
                        outfile.write(f"\n{'=' * 50}\n")
                        outfile.write(f"Content from: {relative_path}\n")
                        outfile.write(f"{'=' * 50}\n\n")

                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                outfile.write(infile.read())
                                outfile.write('\n')
                            processed_files += 1
                        except Exception as e:
                            outfile.write(f"Error reading file {relative_path}: {str(e)}\n")

                # Process files in root directory
                elif root_path.is_file() and root_path.name != output_file:
                    relative_path = root_path.relative_to(directory)

                    # Write filename and path as a header
                    outfile.write(f"\n{'=' * 50}\n")
                    outfile.write(f"Content from: {relative_path}\n")
                    outfile.write(f"{'=' * 50}\n\n")

                    try:
                        with open(root_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                            outfile.write('\n')
                        processed_files += 1
                    except Exception as e:
                        outfile.write(f"Error reading file {relative_path}: {str(e)}\n")

        print(f"Successfully combined {processed_files} files into {output_file}")
        print("Completely skipped directories:", ", ".join(sorted(skipped_dirs)))

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Get directory path from user
    dir_path = "/Users/sashank/Downloads/docs/courseFall24/BigData/project/predictive_policing_system/weather_service"
    combine_files(dir_path)