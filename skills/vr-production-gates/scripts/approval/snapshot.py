#!/usr/bin/env python3
"""Shared content snapshot; never authenticates a user itself.

The legacy Pi --host-check operation accepts internal IPC from that extension.
MCode uses minimax.py for explicitly technical-only checks and native ask_user
for a real user decision; neither a snapshot nor a local JSON grants authority.
"""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_shooting_plan import check, digest


def snapshot(record_path):
    path=Path(record_path).resolve()
    record=json.loads(path.read_text(encoding='utf-8'))
    if record.get('presentation',{}).get('mode') != 'linked_document':
        raise ValueError('Host gate requires a linked_document submission')
    result=check(path,'review',False)
    if not result['passed']:
        raise ValueError('Script review failed: '+', '.join(result['errors']))
    document=(path.parent/record['presentation']['document_path']).resolve()
    identity={'plan_sha256':result['plan_sha256'],'bundle_sha256':result['bundle_sha256'],
              'document_sha256':digest(document),'document_path':str(document)}
    fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {**identity,'record_path':str(path),'version':record['plan']['version'],
            'source_namespace':record['scope'].get('source_namespace'),
            'authorized_actions':record['scope']['authorized_actions'],'fingerprint':fingerprint,
            'review_passed':True,'host_user_approved':False}


def production_check(record_path, request):
    """Consume a live host assertion over stdin, retaining every technical check."""
    phase=request.get('phase');claim=request.get('claim',False)
    if phase not in ('capture','post') or type(claim) is not bool or (claim and phase!='capture'):
        raise ValueError('Expected capture/post; claim is capture-only')
    current=snapshot(record_path)
    if request.get('fingerprint')!=current['fingerprint']:
        raise ValueError('Host confirmation snapshot changed')
    return check(Path(record_path).resolve(),phase,claim,host_confirmation=current)


if __name__=='__main__':
    try:
        value=production_check(sys.argv[1],json.load(sys.stdin)) if sys.argv[2:]==['--host-check'] else snapshot(sys.argv[1])
        print(json.dumps(value,ensure_ascii=False,allow_nan=False))
        if value.get('passed') is False:sys.exit(2)
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));sys.exit(2)
