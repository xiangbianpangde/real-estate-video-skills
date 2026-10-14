#!/usr/bin/env python3
"""Check repository local Markdown links, embedded figures and JSON syntax.
Skips local session exports and external URLs. Does not claim runtime/UI coverage.
"""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]


def check():
    errors=[];documents=0;images=0
    paths=[ROOT/'README.md']
    for folder in ['skills','wiki','raw']: paths.extend((ROOT/folder).rglob('*.md'))
    for p in paths:
        if '__pycache__' in p.parts:continue
        documents+=1
        text=re.sub(r'```.*?```','',p.read_text(),flags=re.S)
        for match in re.finditer(r'(!?)\[([^\]]*)\]\(([^)]+)\)',text):
            bang,alt,target=match.groups();target=target.strip().strip('<>')
            if '://' in target or target.startswith(('mailto:','#','codex:')):continue
            name=unquote(target.split('#')[0])
            if not name:continue
            if not (p.parent/name).exists():errors.append(f'{p.relative_to(ROOT)}: missing {name}')
            if bang:
                images+=1
                if not alt.strip():errors.append(f'{p.relative_to(ROOT)}: empty image alt')
    for p in (ROOT/'skills').rglob('*.json'):
        try:json.loads(p.read_text())
        except (ValueError,UnicodeError) as e:errors.append(f'{p.relative_to(ROOT)}: {e}')
    return {'passed':not errors,'markdown_documents':documents,'image_references':images,'errors':errors}


if __name__=='__main__':
    result=check();print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['passed'] else 1)
