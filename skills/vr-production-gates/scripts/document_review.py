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


def event_words(event):
    content=event.get('content',event.get('message',{}).get('content',[]))
    if isinstance(content,str):return content
    return '\n'.join(c.get('text','') for c in content if c.get('type') in ('text','input_text','output_text'))


def user_request(message):
    # In structured question replies, the question itself is not authorization.
    reply=re.search(r'<send_user_message_question_reply>\s*([\s\S]*?)\s*</send_user_message_question_reply>',message)
    if reply:
        answers=json.loads(reply[1])
        return '\n'.join(a.get('answer','') for a in answers).strip()
    return message.rsplit('## My request:',1)[-1].strip()


CONFIRMATION = json.loads((Path(__file__).parent/'approval/confirmation.json').read_text(encoding='utf-8'))


def approves_current(value, version):
    if not isinstance(value, str):return False
    value=re.sub(CONFIRMATION['whitespace'],' ',value).strip(' ')
    flags=re.I | re.ASCII
    if not value or len(value)>300 or re.search(CONFIRMATION['reject'],value,flags):return False
    if any(v.lower()!=version.lower() for v in re.findall(CONFIRMATION['versions'],value,flags)):return False
    prefix=re.match(CONFIRMATION['prefix'],value,flags)
    if not prefix:return False
    rest=value[prefix.end():]
    while rest:
        if rest[0] in CONFIRMATION['separators']:rest=rest[1:];continue
        token=next((word for word in CONFIRMATION['tail_tokens'] if rest.startswith(word)),None)
        if token:rest=rest[len(token):];continue
        token=re.match(r'v[\w.-]+',rest,flags)
        if not token or token[0].lower()!=version.lower():return False
        rest=rest[token.end():]
    return True


class Cards(HTMLParser):
    """Collect visible per-chapter words in the canonical document."""
    def __init__(self):
        super().__init__();self.ids=[];self.words={};self.stack=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('script','style'):self.hidden+=1
        if tag not in {'img','br','hr','meta','link','input','source','wbr'}:
            self.stack.append((tag,attrs.get('data-segment')))
        if 'data-segment' in attrs:
            sid=attrs['data-segment'];self.ids.append(sid);self.words[sid]=[]
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:del self.stack[i:];break
    def handle_data(self,data):
        if not self.hidden:
            for _,sid in self.stack:
                if sid is not None:self.words[sid].append(data)


def check_linked_document(record, base):
    """One current HTML contract for review, host snapshots and production checks.

    Byte equality to the standard renderer rejects hidden/substituted content;
    legacy rendered_document retains its own historical transcript contract.
    """
    name=record['presentation'].get('document_path')
    if not isinstance(name,str) or not name or Path(name).is_absolute() or '://' in name:
        raise ValueError('Review document must be an explicit local relative path')
    document=(base/name).resolve();plan=(base/record['plan']['path']).resolve()
    if document==plan:return document
    entries=[a for a in record['assets'] if (base/a['path']).resolve()==document]
    if (len(entries)!=1 or entries[0].get('role') not in {'integrated_review_source','storyboard_source'}
            or not document.is_file() or hashlib.sha256(document.read_bytes()).hexdigest()!=entries[0].get('sha256')):
        raise ValueError('HTML review document must bind its actual bytes as a script asset')
    floorplan=record.get('review_route',{}).get('floorplan')
    if not floorplan:
        floors=[a['path'] for a in record['assets'] if a.get('role')=='floorplan']
        if len(floors)!=1:raise ValueError('HTML review requires a bound floorplan for canonical rendering')
        floorplan=floors[0]
    from storyboard.model import validate, bind_images
    from storyboard.render import render_html
    validate(record)
    source=document.read_text(encoding='utf-8')
    if source!=render_html(record,bind_images(record,base,floorplan),floorplan):
        raise ValueError('HTML review document differs from the standard renderer; regenerate before submitting')
    cards=Cards();cards.feed(source)
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
    return document


def check_submission(presentation,approval,events,path,plan_sha,bundle_sha,version=None):
    items=[e.get('payload',{}) if e.get('type')=='response_item' else e for e in events]
    shown=next((i for i,e in enumerate(items) if e.get('id')==presentation.get('assistant_event_id')),None)
    decided=next((i for i,e in enumerate(items) if e.get('id')==approval.get('user_event_id')),None)
    errors=[]
    if shown is None or decided is None or shown>=decided:return ['document_approval_order_invalid']
    role=lambda e:e.get('role',e.get('message',{}).get('role'))
    shown_text=event_words(items[shown])
    links=re.findall(r'\]\(([^\)]+)\)',shown_text)
    def link_path(link):
        link=link.strip('<>')
        parsed=urlparse(link)
        return Path(unquote(parsed.path if parsed.scheme=='file' else link.split('#',1)[0])).resolve()
    if role(items[shown])!='assistant' or not any(link_path(link)==path for link in links):
        errors.append('document_not_presented')
    user=items[decided];message=event_words(user);request=user_request(message)
    quote=approval.get('explicit_text','')
    yes=r'审核通过|批准|同意执行|确认执行|接受[，,、\s]*(?:现在)?(?:开始|继续)|\bapprove[ds]?\b'
    no=r'不.{0,3}批准|未批准|暂不|先修改|先调整|不要|拒绝|不同意|不能|not approve|do not approve'
    accepted=approves_current(quote,version) if version else bool(re.search(yes,quote,re.I) and not re.search(no,quote,re.I))
    if role(user)!='user' or quote!=request or not accepted:
        errors.append('invalid_user_approval')
    # Ambient browser state is not the user's selection. Bind an explicit
    # approval object when one is recorded, rather than infer it from a tab.
    target=approval.get('document_path')
    if target and (path.parent/target).resolve()!=path:
        errors.append('approved_document_mismatch')
    snapshot=(approval.get('plan_sha256'),approval.get('bundle_sha256'))
    if any(snapshot):
        if snapshot!=(plan_sha,bundle_sha):errors.append('approval_snapshot_mismatch')
    else:
        # Historical transcripts may pin content through an earlier gate result.
        # New linked-document approvals store this snapshot internally instead;
        # users never need to read or repeat a digest.
        bound=False
        for item in items[:shown]:
            if item.get('type') not in ('function_call_output','custom_tool_call_output'):continue
            output=str(item.get('output',''))
            for _ in range(3):output=output.replace('\\"','"').replace('\\n','\n')
            if plan_sha in output and bundle_sha in output and re.search(r'"passed"\s*:\s*true',output):bound=True
        if not bound:errors.append('missing_approval_snapshot')
    return errors


def check_document(presentation, approval, events, base, assets, body, plan_sha, bundle_sha, plan_path=None, record=None):
    name=presentation.get('document_path')
    if presentation.get('mode')=='linked_document':
        path=check_linked_document(record,base)
        return check_submission(presentation,approval,events,path,plan_sha,bundle_sha,record['plan']['version'])
    else:
        path=(base/name).resolve() if name else None
    entry=assets.get(name,{})
    if not name or entry.get('role')!='integrated_review_source':return ['unbound_review_document']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=entry.get('sha256'):
        return ['review_document_sha_mismatch']
    errors=[];doc=Document();doc.feed(path.read_text())
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
        target=(plan_path.parent/image).resolve() if plan_path else (base/image).resolve()
        expected.extend(a.get('sha256') for n,a in assets.items() if (base/n).resolve()==target)
    if len(doc.images)<len(expected) or not set(expected).issubset(digests):errors.append('images_missing_from_document')
    return errors+check_submission(presentation,approval,events,path,plan_sha,bundle_sha)
