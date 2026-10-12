"""Parse the current round's scripts without executing their top-level jobs."""
import ast,json
from pathlib import Path
H=Path(__file__).resolve().parent;rows=[]
for file in sorted(H.glob('*v7_r07.py')):
 try:ast.parse(file.read_text(encoding='utf-8-sig'),filename=str(file));rows.append(dict(file=file.name,pass_=True))
 except (SyntaxError,UnicodeError) as e:rows.append(dict(file=file.name,pass_=False,error=str(e)))
out=dict(pass_=all(r['pass_'] for r in rows),files=len(rows),rows=rows,scope='Syntax only; geometry and task gates are independently checked.')
(H/'results/syntax_v7.json').write_text(json.dumps(out,indent=2));print('SYNTAX',out['pass_'],len(rows),[r for r in rows if not r['pass_']]);assert out['pass_']
