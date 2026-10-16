#!/usr/bin/env python3
"""End-to-end CLI acceptance using bundled synthetic records; not a UI test."""
import argparse
import shutil
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/vr-production-gates'
EXAMPLES=SKILL/'assets/design-system/examples'


def verify():
    results=[]
    with tempfile.TemporaryDirectory(prefix='storyboard-acceptance-') as td:
        for name in ['valid','missing-motion','opening-without-floorplan','missing-ending-cta','summary-subtitles']:
            out=Path(td)/name
            inputs=Path(td)/(name+'-input');inputs.mkdir()
            source=EXAMPLES/(name+'.json')
            data=json.loads(source.read_text())
            if 'base' in data:
                record=json.loads((EXAMPLES/data['base']).read_text())
                for edit in data['edits']:
                    target=record
                    for key in edit['path'][:-1]:target=target[key]
                    if edit['op']=='remove':target.pop(edit['path'][-1])
                    else:target[edit['path'][-1]]=edit['value']
            else:record=data
            for image in ['scene.png','floorplan.png']:shutil.copy2(EXAMPLES/image,inputs/image)
            materialized=inputs/'record.json';materialized.write_text(json.dumps(record,ensure_ascii=False))
            cmd=[sys.executable,str(SKILL/'scripts/build_script_package.py'),'--record',str(materialized),'--floorplan','floorplan.png','--output-dir',str(out)]
            run=subprocess.run(cmd,capture_output=True,text=True)
            expected=name in {'valid','missing-ending-cta'}
            ok=(run.returncode==0 and out.is_dir()) if expected else (run.returncode!=0 and not out.exists())
            row={'case':name,'expected':'generated_document' if expected else 'rejected_without_output','exit_code':run.returncode,'passed':ok,'argv':cmd}
            if expected and ok:
                md=(out/'剧本正文.md').read_text();html=(out/'视频剧本.html').read_text();receipt=json.loads((out/'generation.json').read_text())
                for seg in record['segments']:
                    if seg['text'] not in md or seg['text'] not in html or seg['visual']['title'] not in md or seg['visual']['title'] not in html: row['passed']=False
                row['content_hashes_match']=(hashlib.sha256(md.encode()).hexdigest()==receipt['script_markdown_sha256'] and hashlib.sha256(html.encode()).hexdigest()==receipt['board_html_sha256'])
                row['passed'] &= row['content_hashes_match'] and receipt['visual_review']=='PENDING' and receipt['capture_authorized'] is False
                row['chapter_count']=len(record['segments'])
            elif not expected:row['error']=run.stderr.splitlines()[-1] if run.stderr else run.stdout[-500:]
            results.append(row)
    return {'schema':'storyboard-e2e/v1','kind':'CLI actual process acceptance; UI separate','passed':all(r['passed'] for r in results),'cases':results}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence-out',required=True);a=p.parse_args()
    result=verify();Path(a.evidence_out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['passed'] else 1)
