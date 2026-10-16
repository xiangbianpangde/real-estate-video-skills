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


def validate_editing(record):
    scope=record.get('scope',{});policy=scope.get('editing_policy')
    if policy is None:return
    keys=('single_take_required','allow_cuts','allow_remove_intervals','allow_speed_changes')
    if not isinstance(policy,dict) or any(type(policy.get(k)) is not bool for k in keys):
        raise ValueError('Explicit editing permissions required')
    if policy['single_take_required'] and (policy['allow_cuts'] or policy['allow_remove_intervals'] or scope.get('continuity_class') not in {'same_point_rotation','cross_room_travel'}):
        raise ValueError('Single take cannot permit cuts or deleted source intervals')
    if not policy['allow_cuts'] and record.get('review_route',{}).get('cuts'):
        raise ValueError('Single take/cut prohibition conflicts with route cuts')
    mapping=scope.get('speed_map')
    if mapping is None:return
    duration=scope.get('editing_source_duration_s')
    if type(duration) not in (int,float) or not math.isfinite(duration) or duration<=0 or not isinstance(mapping,list) or not mapping:
        raise ValueError('Speed map requires finite source duration and intervals')
    previous=0
    for part in mapping:
        if not isinstance(part,dict):raise ValueError('Speed map interval required')
        start,end,speed=(part.get(k) for k in ('source_start_s','source_end_s','speed'))
        if any(type(x) not in (int,float) or not math.isfinite(x) for x in (start,end,speed)) or start<0 or end<=start or speed<=0:
            raise ValueError('Speed map requires finite positive intervals and speed')
        if not policy['allow_speed_changes'] and speed!=1:raise ValueError('Speed map speed change not allowed')
        if policy['single_take_required'] and abs(start-previous)>1e-6:
            raise ValueError('Speed map cannot omit, overlap or reorder source intervals')
        previous=end
    if policy['single_take_required'] and abs(previous-duration)>1e-6:
        raise ValueError('Speed map must cover the complete original')


def validate_production_profile(record):
    scope=record.get('scope',{})
    if scope.get('production_profile')!='house-short-v1':return
    duration=scope.get('duration_s')
    if type(duration) not in (int,float) or not 25<=duration<=35:
        raise ValueError('Fixed production requires 25-35 seconds')
    config=scope.get('render_config',{})
    if (config.get('width'),config.get('height'))!=(720,1280):
        raise ValueError('Fixed production requires 720x1280 portrait')
    policy=scope.get('editing_policy',{})
    if policy.get('single_take_required') is not True or policy.get('allow_cuts') is not False or policy.get('allow_remove_intervals') is not False:
        raise ValueError('Fixed production requires complete single take without cuts')
    if scope.get('voiceover_provider') not in {'mcode','minimax_cn'} or scope.get('bgm_source')!='specified_library':
        raise ValueError('Fixed production requires mcode or minimax_cn voiceover and specified BGM library')
    if 'bathroom' not in scope.get('shot_constraints',{}).get('excluded_spaces',[]):
        raise ValueError('Fixed production excludes bathroom')


def validate(record):
    validate_production_profile(record)
    validate_editing(record)
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
            if not isinstance(lines, list) or not lines or not all(isinstance(t, str) and t.strip() for t in lines):
                raise ValueError('Opening composite requires headline text')
        if any(not isinstance(visual.get(k, ''), str) for k in ('cta', 'disclaimer')):
            raise ValueError('Ending text fields must be strings')
        if visual.get('risk_level', 'limitation') not in {'limitation', 'pending', 'info'}:
            raise ValueError('Unknown risk label')
        if record.get('scope', {}).get('subtitle_content_mode') == 'verbatim_voiceover' and seg.get('subtitle_text', seg.get('text')) != seg.get('text'):
            raise ValueError('Verbatim subtitles must use the complete voiceover text')
        for field in ('action', 'focus', 'reference_image'):
            if not isinstance(seg.get(field), str) or not seg[field].strip():
                raise ValueError('Missing chapter field: ' + field)
        for field in ('text', 'risk', 'music'):
            if not isinstance(seg.get(field, ''), str):
                raise ValueError('Chapter text field must be a string: ' + field)
    scope = record.get('scope', {})
    constraints = scope.get('shot_constraints')
    if constraints is not None:
        bounds = constraints.get('duration_range_s', [])
        if (len(bounds) != 2 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in bounds)
                or not 0 < bounds[0] <= bounds[1]
                or not bounds[0] <= scope.get('duration_s', -1) <= bounds[1]
                or not bounds[0] <= previous <= bounds[1]):
            raise ValueError('Shot duration outside current user range')
        excluded = constraints.get('excluded_spaces', [])
        route_spaces = scope.get('route_space_ids', [])
        if not isinstance(excluded,list) or any(not isinstance(x,str) or not x for x in excluded):
            raise ValueError('Explicit excluded space IDs required')
        if not isinstance(route_spaces,list) or not route_spaces or any(not isinstance(x,str) or not x for x in route_spaces):
            raise ValueError('Full route space classification required')
        used = set(route_spaces)
        for seg in segments:
            spaces = seg.get('space_ids', [])
            if not isinstance(spaces,list) or not spaces or any(not isinstance(x,str) or not x for x in spaces):
                raise ValueError('Chapter space classification required')
            used.update(spaces)
            if constraints.get('avoid_wall_facing') is True and seg.get('framing_status') not in {'subject','pending'}:
                raise ValueError('Blank wall or cabinet-door primary framing rejected')
        if used.intersection(excluded):
            raise ValueError('Excluded space appears in chapter or return route')
        # Labels describe the plan; they cannot certify camera frames or new dynamics.
    ds = record.get('design_system')
    if ds is not None:
        if ds.get('id') != 'real-estate-storyboard' or ds.get('version') not in {'1.0.0','1.1.0','1.2.0','1.3.0'}:
            raise ValueError('Unsupported design system version')
        if segments[0]['visual'].get('role') != 'opening' or segments[-1]['visual'].get('role') != 'ending':
            raise ValueError('Standard script requires explicit opening and ending roles')
        if abs(previous-record['scope']['duration_s']) > record['scope'].get('duration_tolerance_s', .001):
            raise ValueError('Chapter timeline and scope duration disagree')
    from .route_board import validate_route
    validate_route(record)
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
