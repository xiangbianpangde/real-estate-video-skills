"""Bind an existing rendered document approval to raw Codex response items.

Checks source bytes, visible script/images, prior digest and event order. Like the
inline gate this does not authenticate transcript authors or certify aesthetics.
"""
import base64
import hashlib
from html.parser import HTMLParser
import json
import re
from urllib.parse import unquote, urlparse
from pathlib import Path


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words=[]
        self.images=[]
        self.hidden=0

    def handle_starttag(self, tag, attrs):
        if tag in ('style','script'): self.hidden+=1
        if tag=='img': self.images.append(dict(attrs).get('src',''))

    def handle_endtag(self, tag):
        if tag in ('style','script'): self.hidden=max(0,self.hidden-1)

    def handle_data(self, data):
        if not self.hidden:self.words.append(data)


def check_document(presentation, approval, events, base, assets, body, plan_sha, bundle_sha):
    errors=[]
    name=presentation.get('document_path')
    entry=assets.get(name,{})
    if not name or entry.get('role')!='integrated_review_source':
        return ['unbound_review_document']
    path=(base/name).resolve()
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=entry.get('sha256'):
        return ['review_document_sha_mismatch']
    doc=Document();doc.feed(path.read_text())
    norm=lambda s: re.sub(r'\s+','',s)
    visible=norm(''.join(doc.words))
    for line in body.splitlines():
        if not line.strip() or line.startswith('!['):continue
        line=re.sub(r'^(?:#{1,6}\s+|-\s+)','',line)
        if norm(line) not in visible:errors.append('script_missing_from_document');break
    digests=set()
    for src in doc.images:
        if src.startswith('data:image/png;base64,'):
            try:digests.add(hashlib.sha256(base64.b64decode(src.split(',',1)[1],validate=True)).hexdigest())
            except ValueError:errors.append('invalid_document_image')
    expected=[]
    for image in re.findall(r'!\[[^\]]+\]\(([^\)]+)\)',body):
        target=(base/image).resolve()
        expected.extend(a.get('sha256') for n,a in assets.items() if (base/n).resolve()==target)
    if len(doc.images)<len(expected) or not set(expected).issubset(digests):errors.append('images_missing_from_document')
    items=[e.get('payload',{}) for e in events if e.get('type')=='response_item']
    shown=next((i for i,e in enumerate(items) if e.get('type')=='message' and e.get('id')==presentation.get('assistant_event_id')),None)
    decided=next((i for i,e in enumerate(items) if e.get('type')=='message' and e.get('id')==approval.get('user_event_id')),None)
    words=lambda e:'\n'.join(c.get('text','') for c in e.get('content',[]) if c.get('type') in ('input_text','output_text'))
    if shown is None or decided is None or shown>=decided:return errors+['document_approval_order_invalid']
    links=re.findall(r'\]\(([^\)]+)\)',words(items[shown]))
    presented=any(Path(unquote(urlparse(link).path if link.startswith('file:') else link)).resolve()==path for link in links)
    if items[shown].get('role')!='assistant' or not presented:errors.append('document_not_presented')
    user=items[decided];message=words(user)
    request=message.rsplit('## My request:',1)[-1].strip()
    quote=approval.get('explicit_text','')
    if user.get('role')!='user' or quote!=request or not re.search(r'审核通过|批准|同意执行|确认执行|\bapprove[ds]?\b',quote,re.I) or re.search(r'不.{0,3}批准|未批准|暂不|不要|拒绝|不同意|不能|not approve|do not approve',quote,re.I):errors.append('invalid_user_approval')
    current=re.search(r'Current URL:\s*(\S+)',message)
    parsed=urlparse(current[1]) if current else None
    if not parsed or parsed.scheme!='file' or Path(unquote(parsed.path)).resolve()!=path:errors.append('approved_document_mismatch')
    # A real read-only gate output before display pins the approved content digest.
    bound=False
    for item in items[:shown]:
        if item.get('type') not in ('function_call_output','custom_tool_call_output'):continue
        output=str(item.get('output',''))
        for _ in range(3):output=output.replace('\\"','"').replace('\\n','\n')
        if plan_sha in output and bundle_sha in output and re.search(r'"passed"\s*:\s*true',output) and re.search(r'"phase"\s*:\s*"review"',output):bound=True
    if not bound:errors.append('document_digest_not_presented_before_approval')
    return errors
