"""Rewrite the Windows absolute paths baked into the copied robot_rail XML/JSON so they resolve on this Mac."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # .../kitchen_robot
SEP = r'(?:\\\\|\\|/)'
PAT = re.compile(r'C:' + SEP + 'Users' + SEP + 'admin' + SEP + 'Documents' + SEP + 'YJGames' + SEP + r'''([^"'<>\s,]*)''')

def fix(m):
    rest = re.sub(SEP, '/', m.group(1))
    return f'{ROOT}/{rest}'

n_files = n_subs = 0
for p in (ROOT / 'robot_rail').rglob('*'):
    if p.suffix not in ('.xml', '.json') or not p.is_file():
        continue
    t = p.read_text(encoding='utf-8', errors='surrogateescape')
    new, k = PAT.subn(fix, t)
    if k:
        p.write_text(new, encoding='utf-8', errors='surrogateescape'); n_files += 1; n_subs += k
print(f'{n_files} files, {n_subs} paths rewritten')

# Windows CJK font (msyh.ttc) used for captions -> a Mac CJK font
FONT = re.compile(r"C:(?:\\\\|\\|/)Windows(?:\\\\|\\|/)Fonts(?:\\\\|\\|/)msyh(?:bd)?\.ttc")
n = 0
for p in (ROOT / 'robot_rail' / 'sim').rglob('*.py'):
    t = p.read_text(encoding='utf-8', errors='surrogateescape')
    new, k = FONT.subn('/System/Library/Fonts/STHeiti Medium.ttc', t)
    if k:
        p.write_text(new, encoding='utf-8', errors='surrogateescape'); n += k
print(f'{n} font paths rewritten')
