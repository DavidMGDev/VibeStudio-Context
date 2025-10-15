#!/usr/bin/env python3
"""
CodeTextify.py - Universal Code File Processor
Processes code files with specified extensions into consolidated text files.
Designed to work with any codebase (web projects, game engines, etc.)
Place this file in VSC-PLUS/CodeTextify.py
"""

import os
import shutil
import re
import subprocess
import sys
import time

# === CONFIGURATION SECTION ===
# Paths are relative to project root (where the batch file is located)
# This script should be placed in VSC-PLUS/CodeTextify.py
CONFIG = {
    'source_folder': '.',  # Current directory by default
    'txts_folder': 'VSC-PLUS/TXTs',
    'merged_folder': 'VSC-PLUS/Merged',
    'max_chars_per_file': 75000,
    'output_filename_prefix': 'MergedFile',
    'file_extensions': []  # Will be set via command line
}

def print_header():
    """Print application header."""
    print("=" * 60)
    print("           CODE TEXTIFY v2.0")
    print("      Universal Code File to Text Converter")
    print("=" * 60)
    print()

def print_step(step_number, description):
    """Print a formatted step header."""
    print(f"\n[STEP {step_number}] {description}")
    print("-" * (len(description) + 10))

def wait_for_user(message="Press Enter to continue...", timeout=None):
    """Wait for user input with optional timeout."""
    try:
        if timeout:
            print(f"{message} (continuing automatically in {timeout} seconds)")
            time.sleep(timeout)
        else:
            input(message)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

def validate_paths():
    """Validate and display the configured paths."""
    print("Configuration:")
    source_path = os.path.abspath(CONFIG['source_folder'])
    txts_path = os.path.abspath(CONFIG['txts_folder'])
    merged_path = os.path.abspath(CONFIG['merged_folder'])

    print(f"  Source folder:  {source_path}")
    print(f"  TXTs folder:    {txts_path}")
    print(f"  Output folder:  {merged_path}")
    print(f"  File extensions: {', '.join(CONFIG['file_extensions'])}")
    print()

    if not os.path.exists(source_path):
        print(f"ERROR: Source folder not found: {source_path}")
        print("Please check the 'source_folder' setting in the configuration.")
        return False, None, None, None

    if not CONFIG['file_extensions']:
        print("ERROR: No file extensions specified!")
        print("Please provide file extensions as command line arguments.")
        return False, None, None, None

    file_count = count_code_files(source_path, CONFIG['file_extensions'])
    print(f"✓ Source folder found with {file_count} matching files")

    if file_count == 0:
        print("WARNING: No files found with the specified extensions!")
        print("Make sure you're in the correct directory and the extensions are correct.")

    return True, source_path, txts_path, merged_path

def count_code_files(folder_path, extensions):
    """Count the number of files with specified extensions in a folder."""
    count = 0
    try:
        for root, _, files in os.walk(folder_path):
            # Skip the VSC-PLUS folder itself
            if 'VSC-PLUS' in root or 'VSC' in root:
                continue
            count += len([f for f in files if any(f.endswith(ext) for ext in extensions)])
    except:
        pass
    return count

def safe_remove_folder(folder_path):
    """Safely remove a folder and its contents."""
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"  ✓ Cleared: {folder_path}")
        else:
            print(f"  ✓ Folder doesn't exist (no need to clear): {folder_path}")
        return True
    except Exception as e:
        print(f"  ✗ Error clearing {folder_path}: {e}")
        return False

def create_folder(folder_path):
    """Create a folder if it doesn't exist."""
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"  ✓ Created: {folder_path}")
        return True
    except Exception as e:
        print(f"  ✗ Error creating {folder_path}: {e}")
        return False

def copy_code_files(source_folder, destination_folder, extensions):
    """Copy and rename code files to .txt format."""
    copied_count = 0
    error_count = 0

    print(f"  Scanning {source_folder} for files with extensions: {', '.join(extensions)}")

    for root, _, files in os.walk(source_folder):
        # Skip the VSC-PLUS and VSC folders themselves
        if 'VSC-PLUS' in root or 'VSC' in root:
            continue

        for filename in files:
            if any(filename.endswith(ext) for ext in extensions):
                source_file = os.path.join(root, filename)
                dest_file = os.path.join(destination_folder, filename + '.txt')

                try:
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                    if copied_count % 10 == 0:  # Progress indicator
                        print(f"    Copied {copied_count} files...")
                except Exception as e:
                    print(f"    ✗ Error copying {filename}: {e}")
                    error_count += 1

    print(f"  ✓ Successfully copied {copied_count} files")
    if error_count > 0:
        print(f"  ⚠ {error_count} files had errors")

    return copied_count > 0

def get_original_filename(filename_with_txt):
    """Extract original filename before .txt was added."""
    base_name = os.path.basename(filename_with_txt)
    return base_name[:-4] if base_name.endswith('.txt') else base_name

def get_file_path(original_name, root_source_folder, all_files_map):
    """Find the relative path of an original file from the pre-built map."""
    return all_files_map.get(original_name, original_name)

def merge_text_files(input_folder, output_folder, source_root, extensions):
    """Merge text files into larger consolidated files, with indexes and smart splitting."""

    # Build file map, excluding VSC and VSC-PLUS folders
    all_source_files_map = {}
    for root, _, files in os.walk(source_root):
        if 'VSC-PLUS' in root or 'VSC' in root:
            continue
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                all_source_files_map[f] = os.path.relpath(os.path.join(root, f), os.getcwd())

    source_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.txt')])

    if not source_files:
        print("  ✗ No .txt files found to merge")
        return False

    print(f"  Found {len(source_files)} files to merge...")

    file_index = 1
    merged_count = 0
    buffer_files = []
    buffer_content_size = 0

    max_chars = CONFIG['max_chars_per_file']
    prefix = CONFIG['output_filename_prefix']

    def write_buffer(folder, name_prefix, is_single_file_split=False):
        nonlocal buffer_files, buffer_content_size, merged_count, file_index
        if not buffer_files:
            return

        index_header = f"--- INDEX OF FILES IN THIS MERGE ---\n"
        index_body = ""
        full_content = ""

        for i, file_info in enumerate(buffer_files):
            path_display = file_info.get('path', file_info['name'])
            index_body += f"File #{i+1}: {path_display}\n"
            full_content += file_info['content']

        index = index_header + index_body + ('-' * 35) + "\n\n"
        final_output = index + full_content

        # Determine filename
        if is_single_file_split:
            # For splits, the name is already fully formed (e.g., MergedFile-1-1.txt)
            name = name_prefix
        else:
            name = f"{name_prefix}-{file_index}.txt"

        output_file = os.path.join(folder, name)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_output)

            num_files_str = f"{len(buffer_files)} file{'s' if len(buffer_files) != 1 else ''}"
            print(f"    ✓ Created {name} ({num_files_str}, {len(final_output)} chars)")
            merged_count += 1
        except Exception as e:
            print(f"    ✗ Error writing {output_file}: {e}")

        buffer_files = []
        buffer_content_size = 0
        if not is_single_file_split:
            file_index += 1

    for file_path in source_files:
        original_name = get_original_filename(os.path.basename(file_path))
        content = open(file_path, 'r', encoding='utf-8').read()

        # --- Large File Splitting ---
        header_est = len(f"{'=' * 100}\nFile: {original_name} (Part X of Y)\n{'=' * 100}\n\n")
        index_est = 150 # Generous estimate for the index
        if len(content) + header_est + index_est > max_chars:
            if buffer_files: write_buffer(output_folder, prefix)

            print(f"    → Splitting large file: {original_name}...")

            # Determine if we should do smart splitting based on file type
            is_code_file = any(original_name.endswith(ext) for ext in ['.py', '.js', '.ts', '.gd', '.java', '.cpp', '.c', '.cs'])

            # 1. Pre-calculate splits
            splits, temp_offset = [], 0
            while temp_offset < len(content):
                available = max_chars - header_est - index_est
                end = temp_offset + available
                chunk = ""
                if end >= len(content):
                    chunk = content[temp_offset:]
                    temp_offset = len(content)
                elif is_code_file:
                    # Try to split at function boundaries for code files
                    pos = max(
                        content.rfind('\nfunction ', temp_offset, end),
                        content.rfind('\ndef ', temp_offset, end),
                        content.rfind('\nfunc ', temp_offset, end),
                        content.rfind('\nclass ', temp_offset, end)
                    )
                    if pos > temp_offset:
                        chunk = content[temp_offset:pos]
                        temp_offset = pos
                    else:
                        chunk = content[temp_offset:end]
                        temp_offset = end
                else:
                    chunk = content[temp_offset:end]
                    temp_offset = end
                if chunk.strip(): splits.append(chunk)

            total_parts = len(splits)
            print(f"      File will be split into {total_parts} parts.")

            # 2. Write splits
            for i, chunk in enumerate(splits):
                part_num = i + 1
                part_header = f"{'=' * 100}\nFile: {original_name} (Part {part_num} of {total_parts})\n{'=' * 100}\n\n"
                rel_path = get_file_path(original_name, source_root, all_source_files_map)
                path_disp = f"{rel_path} (Part {part_num}/{total_parts})"

                buffer_files.append({'name': original_name, 'path': path_disp, 'content': part_header + chunk + "\n\n"})
                write_buffer(output_folder, f"{prefix}-{file_index}-{part_num}.txt", is_single_file_split=True)

            file_index += 1
            continue

        # --- Regular Buffering ---
        rel_path = get_file_path(original_name, source_root, all_source_files_map)
        file_header = f"{'=' * 100}\nFile: {original_name}\n{'=' * 100}\n\n"
        entry_content = file_header + content + "\n\n"

        # Estimate future index size
        future_index = "".join([f['path'] for f in buffer_files] + [rel_path])
        if buffer_files and buffer_content_size + len(entry_content) + len(future_index) + 100 > max_chars:
            write_buffer(output_folder, prefix)

        buffer_files.append({'name': original_name, 'path': rel_path, 'content': entry_content})
        buffer_content_size += len(entry_content)

    if buffer_files: write_buffer(output_folder, prefix)

    print(f"  ✓ Created {merged_count} merged files")
    return merged_count > 0

def open_output_folder(folder_path):
    """Open the output folder in Windows Explorer."""
    try:
        abs_path = os.path.abspath(folder_path)
        if os.path.exists(abs_path):
            subprocess.run(['explorer', abs_path])
            print(f"  ✓ Opened output folder: {abs_path}")
        else:
            print(f"  ⚠ Output folder not found: {abs_path}")
    except Exception as e:
        print(f"  ⚠ Could not open folder: {e}")

def parse_arguments():
    """Parse command line arguments for file extensions."""
    if len(sys.argv) < 2:
        print("ERROR: No file extensions provided!")
        print("Usage: python CodeTextify.py .ext1 .ext2 .ext3")
        print("Example: python CodeTextify.py .py .js .html .css")
        return []

    # Get extensions from command line arguments
    extensions = []
    for arg in sys.argv[1:]:
        # Ensure extension starts with a dot
        if not arg.startswith('.'):
            arg = '.' + arg
        extensions.append(arg)

    return extensions

def main():
    """Main execution function."""
    print_header()

    # Parse command line arguments
    CONFIG['file_extensions'] = parse_arguments()
    if not CONFIG['file_extensions']:
        wait_for_user("Press Enter to exit...")
        return False

    # Validate configuration
    valid, source_path, txts_path, merged_path = validate_paths()
    if not valid:
        wait_for_user("Press Enter to exit...")
        return False

    wait_for_user("Press Enter to start processing...")

    # Step 1: Clear existing folders
    print_step(1, "Clearing existing output folders")
    if not safe_remove_folder(txts_path) or not safe_remove_folder(merged_path):
        print("Failed to clear folders. Please check permissions.")
        wait_for_user("Press Enter to exit...")
        return False

    # Step 2: Create fresh folders
    print_step(2, "Creating fresh output folders")
    if not create_folder(txts_path) or not create_folder(merged_path):
        print("Failed to create folders. Please check permissions.")
        wait_for_user("Press Enter to exit...")
        return False

    # Step 3: Copy code files
    print_step(3, "Copying and converting code files")
    if not copy_code_files(source_path, txts_path, CONFIG['file_extensions']):
        print("No files were copied. Check your extensions and source folder.")
        wait_for_user("Press Enter to exit...")
        return False

    # Step 4: Merge files
    print_step(4, "Merging files into consolidated text files")
    if not merge_text_files(txts_path, merged_path, source_path, CONFIG['file_extensions']):
        print("Failed to merge files.")
        wait_for_user("Press Enter to exit...")
        return False

    # Step 5: Open output
    print_step(5, "Opening output folder")
    open_output_folder(merged_path)

    # Success message
    print("\n" + "=" * 60)
    print("           ✓ PROCESSING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nYour merged files are ready in: {os.path.abspath(merged_path)}")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            wait_for_user("\nPress Enter to exit...", timeout=10)
        else:
            wait_for_user("\nProcessing failed. Press Enter to exit...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error occurred: {e}")
        print("\nPlease check your configuration and try again.")
        wait_for_user("Press Enter to exit...")
        sys.exit(1)
