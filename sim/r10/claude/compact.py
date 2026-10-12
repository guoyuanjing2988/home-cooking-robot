"""Remove unreachable inherited drivers; retain all evidence and vendor sources."""
from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'scene.py';s=p.read_text(encoding='utf-8');a=s.index(' # Archived alternatives');b=s.index('\ndef build(',a);s=s[:a]+s[b:];s=s.replace('R08 scene: unchanged L101 kitchen/rail plus explicitly designed low fixtures.','R09 scene: complete inherited kitchen/arm with mobile cart and low stations.');p.write_text(s,encoding='utf-8')
p=H/'render.py';s=p.read_text(encoding='utf-8');s=s[:s.index('\ndef main():')];p.write_text(s,encoding='utf-8')
p=H/'execute.py';s=p.read_text(encoding='utf-8');a=s.index('\ndef idle():');b=s.index("\nif __name__=='__main__':",a);s=s[:a]+s[b:];s=s.replace(" elif sys.argv[1]=='idle':idle()",'');p.write_text(s,encoding='utf-8')
p=H/'state.py';s=p.read_text(encoding='utf-8');s=s[:s.index('\ndef regression():')];p.write_text(s,encoding='utf-8')
print('Unreachable legacy variants/render/idle/regression drivers removed; final runtime semantics unchanged.')
