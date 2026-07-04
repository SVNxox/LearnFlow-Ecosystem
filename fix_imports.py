
"""
Automatic Import Fixer for LearnFlow Domains

This script fixes import statements in Payment, Certificates, Mentorship,
Submissions, and Enrollment domains by adding 'src.backend.' prefix where needed.

Usage:
    python fix_imports.py --dry-run  
    python fix_imports.py            
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


DOMAINS = ['payment', 'certificates', 'mentorship', 'submissions', 'enrollment']


BASE_DIR = Path(__file__).parent / 'src' / 'backend'


def find_python_files(domain: str) -> List[Path]:
    """Find all Python files in domain's presentation layer."""
    domain_path = BASE_DIR / domain / 'presentation'
    if not domain_path.exists():
        print(f"⚠️  {domain} presentation layer not found at {domain_path}")
        return []

    python_files = []
    for root, dirs, files in os.walk(domain_path):
        
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    return python_files


def fix_imports_in_file(file_path: Path, domain: str, dry_run: bool = False) -> Tuple[bool, int]:
    """
    Fix import statements in a single file.

    Returns:
        (changed, num_fixes): Whether file was changed and number of fixes made
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False, 0

    original_content = content
    fixes = 0

    
    
    
    pattern1 = re.compile(
        rf'^(\s*)from {domain}\.([\w.]+) import',
        re.MULTILINE
    )

    def replace1(match):
        nonlocal fixes
        fixes += 1
        indent = match.group(1)
        rest = match.group(2)
        return f"{indent}from src.backend.{domain}.{rest} import"

    content = pattern1.sub(replace1, content)

    
    
    
    pattern2 = re.compile(
        rf'^(\s*)import {domain}\.([\w.]+)',
        re.MULTILINE
    )

    def replace2(match):
        nonlocal fixes
        fixes += 1
        indent = match.group(1)
        rest = match.group(2)
        return f"{indent}import src.backend.{domain}.{rest}"

    content = pattern2.sub(replace2, content)

    
    if content == original_content:
        return False, 0

    if not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False, 0

    return True, fixes


def fix_domain_imports(domain: str, dry_run: bool = False) -> Tuple[int, int]:
    """
    Fix all imports in a domain.

    Returns:
        (files_changed, total_fixes): Number of files changed and total fixes
    """
    files = find_python_files(domain)

    if not files:
        return 0, 0

    files_changed = 0
    total_fixes = 0

    for file_path in files:
        changed, fixes = fix_imports_in_file(file_path, domain, dry_run)

        if changed:
            files_changed += 1
            total_fixes += fixes

            relative_path = file_path.relative_to(BASE_DIR.parent.parent)
            status = "Would fix" if dry_run else "Fixed"
            print(f"  ✓ {status} {fixes} import(s) in {relative_path}")

    return files_changed, total_fixes


def main():
    """Main entry point."""
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("🔧 FIXING IMPORTS - Files will be modified\n")

    total_files = 0
    total_fixes = 0

    for domain in DOMAINS:
        print(f"📦 {domain.capitalize()} Domain:")
        files_changed, fixes = fix_domain_imports(domain, dry_run)

        if files_changed > 0:
            total_files += files_changed
            total_fixes += fixes
            print(f"   ✅ {files_changed} file(s), {fixes} fix(es)\n")
        else:
            print(f"   ℹ️  No fixes needed\n")

    print("=" * 60)
    if dry_run:
        print(f"📊 SUMMARY (DRY RUN):")
    else:
        print(f"📊 SUMMARY:")
    print(f"   Files that need fixing: {total_files}")
    print(f"   Total import fixes: {total_fixes}")
    print("=" * 60)

    if dry_run:
        print("\n💡 Run without --dry-run to apply changes:")
        print("   python fix_imports.py")
    else:
        print("\n✅ All imports fixed!")
        print("\n🧪 Next steps:")
        print("   1. Run: python manage.py check --settings=learnflow.settings.development")
        print("   2. Fix any remaining issues")
        print("   3. Update api/v1/urls.py to enable domains")

    return 0 if total_fixes == 0 else (1 if dry_run else 0)


if __name__ == '__main__':
    sys.exit(main())
