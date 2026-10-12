"""Run the delivered golden checker with only its output directory relocated."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;CONCEPT=HERE.parent/'concept'
sys.path.insert(0,str(CONCEPT))
(HERE/'models').mkdir(exist_ok=True);(HERE/'results').mkdir(exist_ok=True)
config=json.loads((CONCEPT/'results/best.json').read_text())['config']
(HERE/'golden_config.json').write_text(json.dumps(config))
sys.argv=[str(__file__),str(HERE/'golden_config.json'),'96']
source=(CONCEPT/'golden.py').read_text()
exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
