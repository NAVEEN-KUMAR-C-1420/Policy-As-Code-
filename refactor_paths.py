import os
from pathlib import Path
import re

backend_dir = Path("backend").resolve()

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    
    # 1. Replace PROJECT_ROOT definitions with import
    project_root_patterns = [
        r'PROJECT_ROOT\s*=\s*os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)',
        r'PROJECT_ROOT\s*=\s*os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)',
        r'PROJECT_ROOT\s*=\s*os\.path\.abspath\(os\.path\.join\(os\.path\.dirname\(__file__\),\s*"..",\s*".."\)\)',
        r'PROJECT_ROOT\s*=\s*os\.path\.abspath\(os\.path\.join\(os\.path\.dirname\(__file__\),\s*".."\)\)',
        r'PROJECT_ROOT\s*=\s*os\.path\.join\(os\.path\.dirname\(__file__\),\s*".."\)',
    ]
    
    for pattern in project_root_patterns:
        content = re.sub(pattern, 'from core.paths import BASE_DIR as PROJECT_ROOT', content)

    # Replace specific DB_PATH definition in init_db.py
    if "init_db.py" in str(filepath):
        content = re.sub(r'DB_PATH\s*=\s*os\.path\.join\(os\.path\.dirname\(__file__\),\s*"finance.db"\)',
                         'from core.paths import DATA_DIR\nDB_PATH = DATA_DIR / "finance.db"', content)

    # 2. Replace os.path.join(PROJECT_ROOT, "some", "path") with PROJECT_ROOT / "some" / "path"
    # Actually, pathlib division operator / works nicely.
    # Instead of regex, let's just make PROJECT_ROOT a string again by doing `PROJECT_ROOT = str(BASE_DIR)` to not break existing `os.path.join` calls?
    # NO! Prompt says: "Use pathlib everywhere. Do NOT use ... unless absolutely necessary."
    
    # It's better to just do `from core.paths import BASE_DIR as PROJECT_ROOT, AGENTS_DIR, DATA_DIR, LOG_DIR, REPORT_DIR`
    # Let's replace `os.path.join(PROJECT_ROOT, "agents")` with `AGENTS_DIR`
    content = content.replace('os.path.join(PROJECT_ROOT, "agents")', 'AGENTS_DIR')
    content = content.replace('os.path.join(PROJECT_ROOT, "data")', 'DATA_DIR')
    content = content.replace('os.path.join(PROJECT_ROOT, "logs")', 'LOG_DIR')
    content = content.replace('os.path.join(PROJECT_ROOT, "reports")', 'REPORT_DIR')
    content = content.replace('os.path.join(PROJECT_ROOT, "tests", "reports")', 'REPORT_DIR')
    
    # Replace os.path.join(AGENTS_DIR, ...) -> AGENTS_DIR / ...
    # regex for os.path.join(A, B, C) is hard. Let's do a simple one:
    content = re.sub(r'os\.path\.join\(([^,]+),\s*"([^"]+)"\)', r'\1 / "\2"', content)
    content = re.sub(r'os\.path\.join\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)', r'\1 / "\2" / "\3"', content)
    content = re.sub(r'os\.path\.join\(([^,]+),\s*([^,)]+)\)', r'\1 / \2', content)
    
    # 3. Replace os.path.exists(...) with (...).exists()
    # this requires matching the parenthesis. We can do simple ones:
    content = re.sub(r'os\.path\.exists\(([^)]+)\)', r'Path(\1).exists()', content)
    
    # 4. Replace os.makedirs(os.path.dirname(report_path), exist_ok=True)
    content = content.replace('os.makedirs(os.path.dirname(report_path), exist_ok=True)', 'Path(report_path).parent.mkdir(parents=True, exist_ok=True)')
    
    # 5. Add `from pathlib import Path` if we used Path
    if 'Path(' in content and 'from pathlib import Path' not in content:
        content = 'from pathlib import Path\n' + content
        
    # Inject imports for AGENTS_DIR, DATA_DIR, etc. if they are used but not imported
    imports = []
    for const in ['AGENTS_DIR', 'DATA_DIR', 'LOG_DIR', 'REPORT_DIR']:
        if const in content and f'import {const}' not in content and const not in project_root_patterns:
            imports.append(const)
    if imports:
        import_str = f'from core.paths import {", ".join(imports)}\n'
        content = import_str + content
    
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk(backend_dir):
    for file in files:
        if file.endswith(".py"):
            process_file(Path(root) / file)
