#!/usr/bin/env python3
"""Read-only review snapshot for the Pi approval gate. No user identity claims.

Uses the existing full script checker before pinning the actual review document.
Operational settings are excluded by the existing linked-document bundle digest;
model-written status/approval/transcript fields never grant host authorization.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_shooting_plan import check, digest
from storyboard.render import load, render_html


class Cards(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.words={}; self.stack=[]; self.hidden=0
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in ('script','style'): self.hidden+=1
        if tag not in {'img','br','hr','meta','link','input','source','wbr'}:
            self.stack.append((tag,attrs.get('data-segment')))
        if 'data-segment' in attrs:
            sid=attrs['data-segment'];self.ids.append(sid);self.words[sid]=[]
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.hidden=max(0,self.hidden-1)
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:];break
    def handle_data(self, data):
        if not self.hidden:
            for _,sid in self.stack:
                if sid is not None:self.words[sid].append(data)


def snapshot(record_path):
    path=Path(record_path).resolve()
    record=json.loads(path.read_text(encoding='utf-8'))
    if record.get('presentation',{}).get('mode') != 'linked_document':
        raise ValueError('Host gate requires a linked_document submission')
    result=check(path,'review',False)
    if not result['passed']:
        raise ValueError('Script review failed: '+', '.join(result['errors']))
    presentation=record['presentation']; name=presentation.get('document_path')
    if not isinstance(name,str) or not name or Path(name).is_absolute() or '://' in name:
        raise ValueError('Review document must be an explicit local relative path')
    document=(path.parent/name).resolve()
    plan=(path.parent/record['plan']['path']).resolve()
    if document != plan:
        assets=[a for a in record['assets'] if (path.parent/a['path']).resolve()==document]
        if (len(assets)!=1 or assets[0].get('role') not in {'integrated_review_source','storyboard_source'}
                or assets[0].get('sha256') != digest(document)):
            raise ValueError('HTML review document must bind its actual bytes as a script asset')
        # Accept only the standard current renderer's exact HTML, not arbitrary
        # HTML whose required words could be hidden by CSS/template/active content.
        floorplan=record.get('review_route',{}).get('floorplan')
        if not floorplan:
            floorplans=[a['path'] for a in record['assets'] if a.get('role')=='floorplan']
            if len(floorplans)!=1:raise ValueError('HTML review requires a bound floorplan for canonical rendering')
            floorplan=floorplans[0]
        checked,images=load(path,floorplan)
        if document.read_text(encoding='utf-8')!=render_html(checked,images,floorplan):
            raise ValueError('HTML review document differs from the standard renderer; regenerate before submitting')
        cards=Cards(); cards.feed(document.read_text(encoding='utf-8'))
        if cards.ids != [s['id'] for s in record['segments']]:
            raise ValueError('HTML review document must include every chapter in order')
        normalize=lambda text: ''.join(text.split())
        for seg in record['segments']:
            visible=normalize(''.join(cards.words.get(seg['id'],[])))
            fields={key:seg.get(key,'') for key in ('action','focus','text','risk','music')}
            fields.update({f'highlight-{n}':value for n,value in enumerate(seg.get('highlights',[]))})
            for field,value in fields.items():
                if normalize(value) not in visible:
                    raise ValueError('HTML review document omits chapter '+seg['id']+' '+field)
    document_sha=digest(document)
    identity={'plan_sha256':result['plan_sha256'],'bundle_sha256':result['bundle_sha256'],
              'document_sha256':document_sha,'document_path':str(document)}
    fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {**identity,'record_path':str(path),'version':record['plan']['version'],
            'source_namespace':record['scope'].get('source_namespace'),
            'authorized_actions':record['scope']['authorized_actions'],'fingerprint':fingerprint,
            'review_passed':True,'host_user_approved':False}


if __name__=='__main__':
    try:
        print(json.dumps(snapshot(sys.argv[1]),ensure_ascii=False,allow_nan=False))
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));sys.exit(2)
