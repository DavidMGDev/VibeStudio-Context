#!/usr/bin/env python3
"""
CodeTextify.py - Universal Code File Processor
Processes code files with specified extensions into consolidated text files.
Designed to work with any codebase (web projects, game engines, etc.)
Place this file in VibeStudio/CodeTextify.py
"""

import os
import shutil
import re
import subprocess
import sys
import time
import json

# === CONFIGURATION SECTION ===
# Paths are relative to project root (where the batch file is located)
# This script should be placed in VibeStudio/CodeTextify.py
CONFIG = {
    'source_folder': '.',  # Current directory by default
    'txts_folder': 'VibeStudio/TXTs',
    'merged_folder': 'VibeStudio/Merged',
    'max_chars_per_file': 75000,
    'output_filename_prefix': 'MergedFile',
    'file_extensions': [],  # Will be set via command line
    'DEBUG': False  # Set to True for verbose dir-walking logs (e.g., to debug skips)
}

# Define ignored items as lists (to avoid syntax issues), then convert to lowercase sets
IGNORED_FOLDERS_LIST = [
    '.git', 'node_modules', '.godot', '__pycache__', 'build', 'dist', 'out', 'bin',
    'target', '.gradle', '.idea', '.vscode', 'venv', 'env', '.pytest_cache', 'coverage',
    '.next', 'public', 'npm_modules', '.cache', 'vibestudio'  # Enhanced + vibestudio for pruning
]
CONFIG['ignored_folders'] = {k.lower() for k in IGNORED_FOLDERS_LIST}

IGNORED_FILES_LIST = [
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock', 'composer.lock', 'Gemfile.lock',
    '.env', '.env.local', 'LICENSE', 'CHANGELOG.md',
    '.gitignore', '.gitattributes', 'tsconfig.json', 'webpack.config.js',
    'next-env.d.ts', '.eslintrc.json'  # Enhanced for Next.js configs
]
CONFIG['ignored_files'] = {k.lower() for k in IGNORED_FILES_LIST}


def print_header():
    """Print application header."""
    print("=" * 60)
    print("           CODE TEXTIFY v2.4")
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

# FIXED: Pruned traversal - modify dirs[:] to skip entire subtrees (no entering node_modules/type-is etc.)
def walk_code_files(folder_path, extensions):
    """Generator: Yield (root, filename) for files matching extensions, skipping ignores."""
    ignored_folders_lower = CONFIG['ignored_folders']
    ignored_files_lower = CONFIG['ignored_files']
    
    for root, dirs, files in os.walk(folder_path):
        root_basename_lower = os.path.basename(root).lower()
        root_basename_orig = os.path.basename(root)

        # Debug: Log entering dirs (optional)
        if CONFIG['DEBUG']:
            print(f"  DEBUG: Entering dir: {root}")

        # FIXED: Prune subdirs - remove ignored ones from dirs list to skip their traversal
        pruned_dirs = []
        for d in dirs:
            d_lower = d.lower()
            if d_lower not in ignored_folders_lower and d_lower != 'vibestudio':
                pruned_dirs.append(d)
            else:
                if CONFIG['DEBUG']:
                    print(f"  DEBUG: Pruned subdir: {d} under {root_basename_orig} (ignored)")
        dirs[:] = pruned_dirs

        # FIXED: Additional skip for current root if it's ignored (rare, but covers root-level)
        if root_basename_lower in ignored_folders_lower or root_basename_lower == 'vibestudio':
            if CONFIG['DEBUG']:
                print(f"  DEBUG: Skipped entire root dir: {root_basename_orig} (ignored)")
            continue  # No file processing for this root

        # Process files in this dir
        for filename in files:
            filename_lower = filename.lower()
            if filename_lower in ignored_files_lower:
                print(f"  -> Skipped file: {os.path.join(root_basename_orig, filename)} (ignored file)")
                continue
            if any(filename.endswith(ext) for ext in extensions):
                yield root, filename

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
    print(f"  Ignored folders: {len(CONFIG['ignored_folders'])} (e.g., node_modules, .next, .godot)")
    print(f"  Ignored files:   {len(CONFIG['ignored_files'])} (e.g., package-lock.json)")
    if CONFIG['DEBUG']:
        print("  DEBUG mode: Enabled (verbose dir logs)")
    print()

    if not os.path.exists(source_path):
        print(f"ERROR: Source folder not found: {source_path}")
        print("Please check the 'source_folder' setting in the configuration.")
        return False, None, None, None

    if not CONFIG['file_extensions']:
        print("ERROR: No file extensions specified!")
        print("Please provide file extensions as command line arguments.")
        return False, None, None, None

    file_count = sum(1 for _ in walk_code_files(source_path, CONFIG['file_extensions']))
    print(f"[OK] Source folder found with {file_count} matching files (after ignores)")

    if file_count == 0:
        print("WARNING: No files found with the specified extensions!")
        print("Make sure you're in the correct directory and the extensions are correct.")

    return True, source_path, txts_path, merged_path

def count_code_files(folder_path, extensions):
    """Count the number of files with specified extensions in a folder."""
    return sum(1 for _ in walk_code_files(folder_path, extensions))

def safe_remove_folder(folder_path):
    """Safely remove a folder and its contents."""
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"  [OK] Cleared: {folder_path}")
        else:
            print(f"  [OK] Folder doesn't exist (no need to clear): {folder_path}")
        return True
    except Exception as e:
        print(f"  [ERROR] Error clearing {folder_path}: {e}")
        return False

def create_folder(folder_path):
    """Create a folder if it doesn't exist."""
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"  [OK] Created: {folder_path}")
        return True
    except Exception as e:
        print(f"  [ERROR] Error creating {folder_path}: {e}")
        return False

def copy_code_files(source_folder, destination_folder, extensions):
    """Copy and rename code files to unique .txt format using paths."""
    copied_count = 0
    error_count = 0
    file_map = {}

    print(f"  Scanning {source_folder} for files with extensions: {', '.join(extensions)}")

    def sanitize_rel_path(rel_path):
        safe = re.sub(r'[\\/:*?"<>| ]+', '_', rel_path)
        if len(safe) > 200:
            safe = safe[:200] + '_truncated'
        return safe

    for root, filename in walk_code_files(source_folder, extensions):
        source_file = os.path.join(root, filename)
        rel_path = os.path.relpath(source_file, source_folder)
        safe_rel = sanitize_rel_path(rel_path)
        unique_key = safe_rel
        dest_file = os.path.join(destination_folder, unique_key + '.txt')

        # FIXED: No longer needed, but keep as safety (won't trigger)
        if 'node_modules' in rel_path.lower():
            print(f"    [WARN] EMERGENCY: Copied from node_modules! Path: {rel_path} (skip failed?)")

        try:
            shutil.copy2(source_file, dest_file)
            copied_count += 1
            file_map[unique_key] = {
                'original_filename': filename,
                'rel_path': rel_path.replace('\\', '/')
            }
            if copied_count % 10 == 0:
                print(f"    Copied {copied_count} files...")
        except Exception as e:
            print(f"    [ERROR] Error copying {filename}: {e}")
            error_count += 1

    if file_map:
        map_path = os.path.join(destination_folder, 'file_map.json')
        try:
            with open(map_path, 'w', encoding='utf-8') as f:
                json.dump(file_map, f, indent=2)
            print(f"    [OK] Created file_map.json ({len(file_map)} entries)")
        except Exception as e:
            print(f"    [ERROR] Error saving map: {e}")

    print(f"  [OK] Successfully copied {copied_count} unique files")
    if error_count > 0:
        print(f"  [WARN] {error_count} files had errors")

    return copied_count > 0

def merge_text_files(input_folder, output_folder, source_root, extensions):
    """Merge text files into larger consolidated files, with indexes and smart splitting."""

    map_path = os.path.join(input_folder, 'file_map.json')
    file_map = {}
    fallback_mode = False
    if os.path.exists(map_path):
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                file_map = json.load(f)
            print(f"  [OK] Loaded file_map with {len(file_map)} entries")
        except Exception as e:
            print(f"  [WARN] Error loading file_map ({e}), using fallback mode")
            fallback_mode = True
    else:
        fallback_mode = True
        print("  [WARN] No file_map found, using fallback (may have path issues)")

    all_txt_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
    source_files = sorted([os.path.join(input_folder, f) for f in all_txt_files])

    if not source_files:
        print("  [ERROR] No .txt files found to merge")
        return False

    print(f"  Found {len(source_files)} unique files to merge...")

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

        if is_single_file_split:
            name = name_prefix
        else:
            name = f"{name_prefix}-{file_index}.txt"

        output_file = os.path.join(folder, name)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_output)

            num_files_str = f"{len(buffer_files)} file{'s' if len(buffer_files) != 1 else ''}"
            print(f"    [OK] Created {name} ({num_files_str}, {len(final_output)} chars)")
            merged_count += 1
        except Exception as e:
            print(f"    [ERROR] Error writing {output_file}: {e}")

        buffer_files = []
        buffer_content_size = 0
        if not is_single_file_split:
            file_index += 1

    for file_path in source_files:
        txt_filename = os.path.basename(file_path)
        unique_key = txt_filename[:-4]

        if fallback_mode or unique_key not in file_map:
            original_name = unique_key
            rel_path = unique_key
            print(f"    [WARN] Fallback for {txt_filename}")
        else:
            info = file_map[unique_key]
            original_name = info['original_filename']
            rel_path = info['rel_path']

        # FIXED: Safety net (won't trigger with pruning)
        if 'node_modules' in rel_path.lower():
            print(f"    [WARN] EMERGENCY: Merging node_modules file! Path: {rel_path} (skip failed?)")

        # Try to read file content with multiple encodings
        content = ""
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"    [ERROR] Error reading {txt_filename} with {encoding}: {e}")
                content = f"[ERROR: Could not read file content - {e}]\n"
                break
        else:
            # All encodings failed, try to detect if it's binary
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(1024)
                    if b'\x00' in sample:  # Likely binary file
                        print(f"    [WARN] Skipped binary file: {txt_filename}")
                        continue  # Skip this file entirely
                    else:
                        content = sample.decode('latin-1', errors='replace')
                        print(f"    [WARN] Used fallback encoding for {txt_filename}")
            except Exception as e:
                print(f"    [ERROR] Error reading {txt_filename} as binary: {e}")
                continue  # Skip this file

        header_est = len(f"{'=' * 100}\nFile: {original_name} (Part X of Y)\n{'=' * 100}\n\n")
        index_est = 150
        if len(content) + header_est + index_est > max_chars:
            if buffer_files: write_buffer(output_folder, prefix)

            print(f"    -> Splitting large file: {original_name}...")

            is_code_file = any(original_name.endswith(ext) for ext in ['.py', '.js', '.ts', '.gd', '.java', '.cpp', '.c', '.cs', '.tsx', '.jsx'])

            splits, temp_offset = [], 0
            while temp_offset < len(content):
                available = max_chars - header_est - index_est
                end = temp_offset + available
                chunk = ""
                if end >= len(content):
                    chunk = content[temp_offset:]
                    temp_offset = len(content)
                elif is_code_file:
                    pos = max(
                        content.rfind('\nfunction ', temp_offset, end),
                        content.rfind('\ndef ', temp_offset, end),
                        content.rfind('\nfunc ', temp_offset, end),
                        content.rfind('\nclass ', temp_offset, end),
                        content.rfind('\nexport ', temp_offset, end),
                        content.rfind('\nimport ', temp_offset, end)
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

            for i, chunk in enumerate(splits):
                part_num = i + 1
                part_header = f"{'=' * 100}\nFile: {original_name} (Part {part_num} of {total_parts})\n{'=' * 100}\n\n"
                path_disp = f"{rel_path} (Part {part_num}/{total_parts})"

                buffer_files.append({'name': original_name, 'path': path_disp, 'content': part_header + chunk + "\n\n"})
                write_buffer(output_folder, f"{prefix}-{file_index}-{part_num}.txt", is_single_file_split=True)

            file_index += 1
            continue

        file_header = f"{'=' * 100}\nFile: {original_name}\n{'=' * 100}\n\n"
        entry_content = file_header + content + "\n\n"

        future_index = "".join([f['path'] for f in buffer_files] + [rel_path])
        if buffer_files and buffer_content_size + len(entry_content) + len(future_index) + 100 > max_chars:
            write_buffer(output_folder, prefix)

        buffer_files.append({'name': original_name, 'path': rel_path, 'content': entry_content})
        buffer_content_size += len(entry_content)

    if buffer_files: write_buffer(output_folder, prefix)

    print(f"  [OK] Created {merged_count} merged files")
    return merged_count > 0

def open_output_folder(folder_path):
    """Open the output folder in Windows Explorer."""
    try:
        abs_path = os.path.abspath(folder_path)
        if os.path.exists(abs_path):
            subprocess.run(['explorer', abs_path])
            print(f"  [OK] Opened output folder: {abs_path}")
        else:
            print(f"  [WARN] Output folder not found: {abs_path}")
    except Exception as e:
        print(f"  [WARN] Could not open folder: {e}")

def parse_arguments():
    """Parse command line arguments for file extensions."""
    if len(sys.argv) < 2:
        print("ERROR: No file extensions provided!")
        print("Usage: python CodeTextify.py .ext1 .ext2 .ext3")
        print("Example: python CodeTextify.py .py .js .html .css")
        return []

    extensions = []
    for arg in sys.argv[1:]:
        if not arg.startswith('.'):
            arg = '.' + arg
        extensions.append(arg)

    return extensions

def main():
    """Main execution function."""
    print_header()

    CONFIG['file_extensions'] = parse_arguments()
    if not CONFIG['file_extensions']:
        wait_for_user("Press Enter to exit...")
        return False

    valid, source_path, txts_path, merged_path = validate_paths()
    if not valid:
        wait_for_user("Press Enter to exit...")
        return False

    wait_for_user("Press Enter to start processing...")

    print_step(1, "Clearing existing output folders")
    if not safe_remove_folder(txts_path) or not safe_remove_folder(merged_path):
        print("Failed to clear folders. Please check permissions.")
        wait_for_user("Press Enter to exit...")
        return False

    print_step(2, "Creating fresh output folders")
    if not create_folder(txts_path) or not create_folder(merged_path):
        print("Failed to create folders. Please check permissions.")
        wait_for_user("Press Enter to exit...")
        return False

    print_step(3, "Copying and converting code files (unique names)")
    if not copy_code_files(source_path, txts_path, CONFIG['file_extensions']):
        print("No files were copied. Check your extensions and source folder.")
        wait_for_user("Press Enter to exit...")
        return False

    print_step(4, "Merging files into consolidated text files")
    if not merge_text_files(txts_path, merged_path, source_path, CONFIG['file_extensions']):
        print("Failed to merge files.")
        wait_for_user("Press Enter to exit...")
        return False

    print_step(5, "Opening output folder")
    open_output_folder(merged_path)

    print("\n" + "=" * 60)
    print("           [SUCCESS] PROCESSING COMPLETED SUCCESSFULLY!")
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