# VibeStudio Context

🚀 **Extract your entire project codebase into AI-ready text files** – Merge code across files into concise, indexed documents without token limits. Perfect for feeding full projects to AI assistants like Grok, Claude, or ChatGPT for analysis, debugging, or refactoring.

## Why Use It?
- **Practicality**: Large projects often exceed AI context windows. This tool copies, renames (.txt), and merges files with indexes and smart splitting (e.g., at function boundaries for code), creating portable text files you can paste into any AI chat.
- **Speed**: Processes hundreds of files in seconds, skips irrelevant folders (like `node_modules`), and limits files to ~75K chars each.
- **Versatile**: Supports web, Godot, or custom project types out of the box.

## Installation (30 seconds)
1. Download and run **`VibeStudio-Context (Installer).bat`** from the [Releases page](https://github.com/DavidMGDDev/VibeStudio-Context/releases) in your **project root directory**.
2. Select your project type: **Web** (HTML/JS/CSS/etc.), **Godot** (GD/TSCN), or **Other** (custom extensions like `.py .cpp`).
3. For "Other", enter extensions one by one (e.g., `.rs done` for Rust).
4. The installer clones this repo, configures, and self-cleans – leaving only `Z - Extract Context.bat` and a `VibeStudio` folder with the processor.

**Requirements**: Windows, Git, Python 3 (auto-checked).

## Usage
- Place `Z - Extract Context.bat` in your project root.
- Double-click it to run.
- Output: `VibeStudio/Merged/*.txt` files with indexes (e.g., `--- INDEX OF FILES IN THIS MERGE ---` + contents).
- Large files auto-split; Explorer opens the folder on completion.

### Example Output Snippet
```
--- INDEX OF FILES IN THIS MERGE ---
File #1: src/main.py
File #2: assets/config.json
-------------------------------------
====================================================================================================
File: main.py
====================================================================================================

def hello_world():
    print("Hello from VibeStudio!")
```

## Supported Project Types
- **Web**: `.html .htm .css .scss .sass .less .js .jsx .mjs .ts .tsx .vue .php .json`
- **Godot**: `.gd .tscn`
- **Other**: Any extensions you specify.

## Troubleshooting
- No files found? Check extensions match your project.
- Errors? Ensure Python/Git in PATH; run as admin if needed.
- Customize: Edit `VibeStudio/CodeTextify.py` for advanced tweaks.

## License
MIT – Free to use/modify. Questions? Open an issue or email davidmgdev@gmail.com.

⭐ Star if helpful!