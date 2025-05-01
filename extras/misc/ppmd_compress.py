import os
import subprocess

# this script compresses a given file (in same directory as script) using 7z CLI with PPMd compression
# PPMd is good for text/json

file_name = "tags.json"

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, file_name)

# output file path
output_7z_path = os.path.join(script_dir, "compressed_files", f"{file_name}_ppmd.7z")

# Command to compress the file with PPMd at max quality using 7z
command = [
    "7z",
    "a",
    output_7z_path,
    json_path,
    "-mx=9",  # Set compression level to maximum
    "-m0=PPMd",  # Set PPMd compression method
]

subprocess.run(command, check=True)

print(f"File compressed to {output_7z_path} with PPMd max quality.")
