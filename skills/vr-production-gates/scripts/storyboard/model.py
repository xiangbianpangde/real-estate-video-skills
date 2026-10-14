"""Semantic validation shared by both outputs; does not certify source facts."""
import hashlib
import math
from pathlib import Path

MOTION_KINDS = {'static', 'pan', 'travel', 'orbit', 'fov'}
LAYOUTS = {'source_reference', 'opening_composite', 'ending_composite'}


def motion_steps(visual):
    motion = visual.get('motion', {})
    if 'steps' in motion and 'kind' in motion:
        raise ValueError('Choose a single motion or ordered steps, not both')
    steps = motion.get('steps', [motion])
    if not isinstance(steps, list) or not steps:
        raise ValueError('Motion diagram steps required')
    for step in steps:
        if not isinstance(step, dict) or step.get('kind') not in MOTION_KINDS or not isinstance(step.get('label'), str) or not step['label'].strip():
            raise ValueError('Explicit supported motion kind and label required')
    return steps


def validate(record):
    segments = record.get('segments', [])
    if not segments:
        raise ValueError('At least one chapter required')
    ids = set()
    previous = 0
    for n, seg in enumerate(segments):
        sid = seg.get('id')
        if not isinstance(sid, str) or sid in ids:
            raise ValueError('Unique chapter ID required')
        ids.add(sid)
        start, end = seg.get('start_s'), seg.get('end_s')
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) for t in (start, end)) or end <= start or abs(start-previous) > .001:
            raise ValueError('Continuous finite chapter timeline required: ' + sid)
        previous = end
        visual = seg.get('visual', {})
        if not isinstance(visual.get('title'), str) or not visual['title'].strip() or visual.get('layout') not in LAYOUTS:
            raise ValueError('Explicit visual title and layout required: ' + sid)
        motion_steps(visual)
        layout = visual['layout']
        role = visual.get('role')
        if record.get('design_system') and role not in {'opening','chapter','ending'}:
            raise ValueError('Explicit narrative role required')
        if role == 'opening' and layout != 'opening_composite':
            raise ValueError('Opening role requires composed preview')
        if role == 'ending' and layout != 'ending_composite':
            raise ValueError('Ending role requires composed preview')
        if layout == 'opening_composite':
            lines = visual.get('headline_lines')
            if not isinstance(lines, list) or len(lines) != 2 or not all(isinstance(t, str) and t.strip() for t in lines):
                raise ValueError('Opening composite requires two headline lines')
        if layout == 'ending_composite' and not str(visual.get('cta', '')).strip():
            raise ValueError('Ending composite requires explicit CTA')
        if visual.get('risk_level', 'limitation') not in {'limitation', 'pending', 'info'}:
            raise ValueError('Unknown risk label')
        if record.get('scope', {}).get('subtitle_content_mode') == 'verbatim_voiceover' and seg.get('subtitle_text', seg.get('text')) != seg.get('text'):
            raise ValueError('Verbatim subtitles must use the complete voiceover text')
        for field in ('action', 'focus', 'text', 'risk', 'reference_image'):
            if not isinstance(seg.get(field), str) or not seg[field].strip():
                raise ValueError('Missing chapter field: ' + field)
    ds = record.get('design_system')
    if ds is not None:
        if ds.get('id') != 'real-estate-storyboard' or ds.get('version') != '1.0.0':
            raise ValueError('Unsupported design system version')
        if segments[0]['visual'].get('role') != 'opening' or segments[-1]['visual'].get('role') != 'ending':
            raise ValueError('Standard script requires explicit opening and ending roles')
        if abs(previous-record['scope']['duration_s']) > record['scope'].get('duration_tolerance_s', .001):
            raise ValueError('Chapter timeline and scope duration disagree')
    return record


def bind_images(record, base, floorplan):
    origin = 'synthetic_fixture' if record.get('fixture') is True else 'actual_source'
    entries = record['assets']
    paths = {}
    for name in {s['reference_image'] for s in record['segments']} | {str(floorplan)}:
        target = (base / name).resolve()
        candidates = [a for a in entries if (base / a['path']).resolve() == target]
        if len(candidates) != 1 or candidates[0].get('origin') != origin:
            raise ValueError('Source image identity missing or ambiguous: ' + name)
        data = target.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n') or hashlib.sha256(data).hexdigest() != candidates[0].get('sha256'):
            raise ValueError('Source image SHA or PNG mismatch: ' + name)
        paths[name] = data
    return paths
