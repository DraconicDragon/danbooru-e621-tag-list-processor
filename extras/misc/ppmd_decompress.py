import os
import subprocess

# this script decompresses a given file compressed with PPMd (in same directory as script) using 7z CLI

file_name = "tag_aliases_compressed.7z"

script_dir = os.path.dirname(os.path.abspath(__file__))
compressed_path = os.path.join(script_dir, file_name)

output_dir = os.path.join(script_dir, "decompressed_files")

os.makedirs(output_dir, exist_ok=True)

# Command to decompress the file using 7z
command = [
    "7z",
    "x",
    compressed_path,  # 'x' extracts with full paths
    f"-o{output_dir}",  # Output directory
    "-y",  # Assume Yes on all queries (overwrite without prompt)
]

subprocess.run(command, check=True)

print(f"File decompressed to {output_dir}")
