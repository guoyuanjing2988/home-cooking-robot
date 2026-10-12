"""Copied checked motion driver with new complete scene; no process bypass."""
from pathlib import Path
source=Path(__file__).with_name('rescue_meal.py').read_text()
source=source.replace('from rescue_spec import *','from station_spec import *').replace('v2/motion','v3/motion').replace('v2/models','v3/models').replace('v2/audit','v3/audit')
exec(compile(source,'<copied v2 motion driver / v3 scene>','exec'))
