"""Small offline helpers shared by the runnable examples. Requires FFmpeg."""
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else _sha(source)


def _sha(source):
    value=hashlib.sha256()
    for block in iter(lambda:source.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def probe(path):
    result=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    result['duration_s']=float(result['format']['duration'])
    return result


def write_json(path,data):
    with Path(path).open('x',encoding='utf-8') as output:json.dump(data,output,ensure_ascii=False,indent=2,allow_nan=False)


def output_folder(path,inputs):
    path=Path(path).resolve()
    if any(Path(f).resolve().is_relative_to(path) for f in inputs):raise ValueError('Output folder overlaps an input')
    path.mkdir(parents=True,exist_ok=False)
    return path
