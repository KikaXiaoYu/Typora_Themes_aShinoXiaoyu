import os

# Configuration: Output filename
OUTPUT_FILE = "_project-SAC.txt"

# Configuration: Ignored directories (Added hidden folder filtering for Windows)
IGNORE_DIRS = {
    '.git', '__pycache__', '.vscode', '.idea', 'venv', 'env', 
    'node_modules', 'wandb', 'logs', 'checkpoints', 'data',
    '$RECYCLE.BIN', 'System Volume Information', # Windows specific
    '_AI-guidance'
    
}

# Configuration: Ignored file extensions
IGNORE_EXTENSIONS = {
    # Documents/Binary
    '.pdf', '.docx', '.doc', '.xlsx', '.ppt', '.pptx',
    # Deep Learning weights (Prevent reading large binary files/gibberish)
    '.pt', '.pth', '.ckpt', '.safetensors', '.pkl', '.npy', '.npz', '.h5',
    # Images/Media
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.mp4', '.avi',
    # Archives/Executables
    '.zip', '.tar', '.gz', '.rar', '.7z', '.exe', '.dll', '.so', '.o', '.lib', '.obj',
    # System files
    '.DS_Store', 'desktop.ini', 'Thumbs.db'
}

def read_file_content(file_path):
    """
    Attempt to read using UTF-8; if failed, try GBK (common on Windows).
    If both fail, treat as binary and skip.
    """
    encodings = ['utf-8', 'gbk']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                # Attempt to read the first 1024 bytes to quickly verify encoding
                content = f.read()
                return content
        except (UnicodeDecodeError, PermissionError):
            continue
        except Exception as e:
            # Other IO errors
            return None
    
    return None

def get_file_tree(startpath):
    """
    Generate directory tree structure.
    """
    tree_str = "## 1. Project Structure\n\n```text\n"
    for root, dirs, files in os.walk(startpath):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if any(f.lower().endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            if f == OUTPUT_FILE or f == os.path.basename(__file__):
                continue
            tree_str += f"{subindent}{f}\n"
    tree_str += "```\n\n"
    return tree_str

def get_file_contents(startpath):
    """
    Read file contents.
    """
    content_str = "## 2. File Contents\n\n"
    
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # 1. Filter by extension
            if any(filename.lower().endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            
            # 2. Exclude script itself and the output file
            if filename == OUTPUT_FILE or filename == os.path.basename(__file__):
                continue
            
            # 3. Attempt to read content
            content = read_file_content(file_path)
            
            # If content is None, it is binary or unreadable; skip.
            if content is None:
                continue

            # Determine Markdown code block language
            ext = os.path.splitext(filename)[1].lower().replace('.', '')
            lang_map = {
                'py': 'python', 'sh': 'bash', 'md': 'markdown', 
                'json': 'json', 'yaml': 'yaml', 'yml': 'yaml',
                'cpp': 'cpp', 'c': 'c', 'h': 'cpp', 'java': 'java',
                'bat': 'bat', 'ps1': 'powershell' # Windows specific
            }
            lang = lang_map.get(ext, 'text')

            # Write content
            rel_path = os.path.relpath(file_path, startpath).replace('\\', '/') # Unify path separators
            content_str += f"### File: `{rel_path}`\n\n"
            content_str += f"```{lang}\n{content}\n```\n\n---\n\n"

    return content_str

def main():
    root_dir = os.getcwd()
    print(f"Scanning directory: {root_dir}...")
    
    try:
        header = f"# Project Documentation\n\nGenerated for path: `{root_dir}`\n\n"
        tree_section = get_file_tree(root_dir)
        content_section = get_file_contents(root_dir)
        
        final_md = header + tree_section + content_section
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_md)
        
        print(f"Success! Documentation saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()