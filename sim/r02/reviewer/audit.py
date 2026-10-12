"""Read-only audit of every R02 text/script/result; outputs only in reviewer."""
import os, sys, json, ast, hashlib, difflib, csv, collections
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def functions(tree):
    out={}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for m in node.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)): out[node.name+'.'+m.name]=ast.dump(m, include_attributes=False)
        elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)): out[node.name]=ast.dump(node, include_attributes=False)
    return out
def main():
    inventory=[]; groups=collections.defaultdict(lambda: dict(files=0,bytes=0,phase_results=0,passed=0,seeds=set(),revisions=set()))
    scripts=[]; bad=[]; contact_sets=collections.defaultdict(set)
    for p in sorted((ROOT/'sim/r02').rglob('*')):
        if not p.is_file() or HERE in p.parents or '__pycache__' in str(p): continue
        ext=p.suffix.lower()
        if ext not in ('.py','.json','.csv','.md','.xml','.txt','.log'): continue
        row=dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p))
        txt=p.read_text(encoding='utf-8-sig',errors='replace')
        if ext=='.py':
            try:
                tree=ast.parse(txt); row['syntax_ok']=True
                scripts.append(dict(**row,functions=list(functions(tree)),lines=len(txt.splitlines())))
            except Exception as e: bad.append(dict(path=row['path'],error=str(e)))
        if ext=='.json':
            try:
                obj=json.loads(txt); group=str(p.parent.relative_to(ROOT/'sim/r02'))
                g=groups[group];g['files']+=1;g['bytes']+=len(p.read_bytes())
                if isinstance(obj,dict) and 'seeds' in obj and ('parts' in obj or 'rows' in obj) and ('id' in obj or 'logical_id' in obj):
                    g['phase_results']+=1; g['passed']+=bool(obj.get('ok',obj.get('verdict')=='FEASIBLE'));g['seeds'].add(obj['seeds']);g['revisions'].add(obj.get('model_revision','unspecified'))
                    if 'final_v4' in str(p):
                        for part in obj.get('parts',[]):
                            for r in part['rows']:
                                for hit in r.get('hits',[]): contact_sets['final_pairs'].add(tuple(sorted(hit['pair'])))
                row['parse_ok']=True
            except Exception as e: bad.append(dict(path=row['path'],error=str(e)))
        if ext=='.csv': row['rows']=len(list(csv.DictReader(txt.splitlines())))
        inventory.append(row)
    for p in sorted((ROOT/'posts/r02').glob('*.md')):
        if p.name=='reviewer.md':continue
        p.read_text(encoding='utf-8');inventory.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=digest(p)))
    sources={'inputs':ROOT/'inputs/prep_checker.py','golden':ROOT/'inputs/mandoline_golden.py','r01':ROOT/'sim/r01/concept/checker.py','r02':ROOT/'sim/r02/concept2/reference.py'}
    txts={k:p.read_text(encoding='utf-8-sig') for k,p in sources.items()}
    fs={k:functions(ast.parse(t)) for k,t in txts.items()}
    rules=dict(hashes={k:digest(p) for k,p in sources.items()},r01_r02_byte_identical=sources['r01'].read_bytes()==sources['r02'].read_bytes(),functions={})
    for key in ('Checker.bind_model','Checker.forbidden','Checker.grip','Checker.solve','Checker.target_rotation','Checker.run_seed','summarize'):
        rules['functions'][key]={k:hashlib.sha256(v[key].encode()).hexdigest() if key in v else None for k,v in fs.items()}
    rules['golden_top_level_functions']={key:hashlib.sha256(fs['golden'][key].encode()).hexdigest() for key in fs['golden']}
    rules['golden_note']='Golden is a separate top-level program, not a Checker class. Null means method absent, not a matching rule. Manual gate comparison: PAD adjustment +2*PAD, 10mm robot/environment or interarm, 5mm gripper/held, same-arm 0mm, 5mm/3deg IK; golden force cases remain 40/70/100N, not required unchanged for the explicitly redefined R02 process.'
    for a,b in (('inputs','r01'),('r01','r02')):
        d=''.join(difflib.unified_diff(txts[a].splitlines(True),txts[b].splitlines(True),fromfile=str(sources[a]),tofile=str(sources[b])))
        (OUT/f'{a}_to_{b}.diff').write_text(d,encoding='utf-8')
    proc=json.loads((ROOT/'sim/r02/tools/results/process_v2.json').read_text())
    write('process_keys.json',{k:(list(v) if isinstance(v,dict) else len(v) if isinstance(v,list) else v) for k,v in proc.items()})
    # Full source forces, instance recipe, held interfaces and process loops.
    write('process_review.json', {k:v for k,v in proc.items() if k not in ('layout_geometry_primitives','tools')})
    intended=[]
    for ph in proc['checker_instances']:
        intended.append(dict(id=ph['instance_id'],segments=[dict(label=s['label'],station=s['station'],poses=[{side:dict(held=h['held'],intended=h['intended'],work_site=h.get('work_site'),held_kg=h['held_kg'],nominal_forces_N=h['nominal_forces_N'],check_forces_N=h['check_forces_N']) for side,h in po.items()} for po in s['poses']]) for s in ph['segments']]))
    write('intended_and_loads.json',intended)
    for g in groups.values():g['seeds']=sorted(g['seeds']);g['revisions']=sorted(g['revisions'])
    write('inventory.json',inventory);write('script_inventory.json',scripts);write('results_inventory.json',dict(groups));write('rule_ast.json',rules);write('parse_errors.json',bad)
    inputs=list((ROOT/'inputs').glob('*'))+[ROOT/'DECISIONS.md']+list((ROOT/'sim/r01/concept').glob('*.py'))
    write('readonly_hashes.json',{str(p.relative_to(ROOT)):digest(p) for p in inputs if p.is_file()})
    write('summary.json',dict(files=len(inventory),scripts=len(scripts),bytes=sum(x['bytes'] for x in inventory),json_groups=len(groups),errors=bad,reference_identical=rules['r01_r02_byte_identical'],process_keys=list(proc),final_contact_pairs=len(contact_sets['final_pairs'])))
    print(json.dumps(json.loads((OUT/'summary.json').read_text(encoding='utf-8')),ensure_ascii=True))
if __name__=='__main__': main()
