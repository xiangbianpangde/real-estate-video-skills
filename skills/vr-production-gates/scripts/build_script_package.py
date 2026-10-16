#!/usr/bin/env python3
"""One record -> one Chinese HTML with route/detail + supporting Markdown/receipt.
Creates a new output directory. Does not export PNG or assert visual acceptance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from storyboard.render import load, render_html, render_markdown


def build_package(record_path, output_dir, floorplan):
    record_path=Path(record_path).resolve()
    record,images=load(record_path,floorplan)
    html=render_html(record,images,floorplan)
    # Rebase file references for the new output directory, rather than duplicating data.
    output_dir=Path(output_dir).resolve()
    import copy
    rebased=copy.deepcopy(record)
    for seg in rebased['segments']:
        seg['reference_image']=os.path.relpath((record_path.parent/seg['reference_image']).resolve(),output_dir)
    for a in rebased['assets']:
        a['path']=os.path.relpath((record_path.parent/a['path']).resolve(),output_dir)
    for key in ['render_validation']:
        if key in rebased['scope']:
            entry=rebased['scope'][key]
            entry['path']=os.path.relpath((record_path.parent/entry['path']).resolve(),output_dir)
    if 'visual_acceptance' in rebased['scope']:
        for entry in rebased['scope']['visual_acceptance'].values():
            entry['path']=os.path.relpath((record_path.parent/entry['path']).resolve(),output_dir)
    floor=Path(floorplan)
    if not floor.is_absolute():floor=record_path.parent/floor
    md=render_markdown(rebased,os.path.relpath(floor.resolve(),output_dir))
    receipt={'schema':'storyboard-generation/v1','source_record_sha256':hashlib.sha256(record_path.read_bytes()).hexdigest(),
             'board_html_sha256':hashlib.sha256(html.encode()).hexdigest(),'script_markdown_sha256':hashlib.sha256(md.encode()).hexdigest(),
             'segments':[s['id'] for s in record['segments']],'visual_review':'PENDING','capture_authorized':False}
    output_dir.mkdir(parents=True,exist_ok=False)
    (output_dir/'视频剧本.html').write_text(html, encoding='utf-8')
    (output_dir/'剧本正文.md').write_text(md, encoding='utf-8')
    receipt['document']='视频剧本.html'
    (output_dir/'generation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record',required=True);p.add_argument('--floorplan',required=True);p.add_argument('--output-dir',required=True)
    a=p.parse_args();print(json.dumps(build_package(a.record,a.output_dir,a.floorplan),ensure_ascii=False,indent=2))
