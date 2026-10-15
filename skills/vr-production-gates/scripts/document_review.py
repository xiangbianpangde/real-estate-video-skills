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


def check_submission(presentation,approval,events,path,plan_sha,bundle_sha):
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
    if role(user)!='user' or quote!=request or not re.search(yes,quote,re.I) or re.search(no,quote,re.I):
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


def check_document(presentation, approval, events, base, assets, body, plan_sha, bundle_sha, plan_path=None):
    name=presentation.get('document_path')
    if presentation.get('mode')=='linked_document':
        path=(base/name).resolve() if name else plan_path
        if path!=plan_path:
            entry=assets.get(name,{})
            if entry.get('role')!='integrated_review_source' or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=entry.get('sha256'):
                return ['unbound_review_document']
            # Linked HTML is checked just like a rendered-document submission.
        else:
            return check_submission(presentation,approval,events,path,plan_sha,bundle_sha)
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
