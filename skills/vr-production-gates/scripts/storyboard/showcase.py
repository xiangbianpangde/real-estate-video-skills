"""Current showcase choices; historical records without this block stay readable."""
import copy
import math

DEFAULT_SHOWCASE = {
    'space_order': ['living_room', 'balcony', 'primary_bedroom'],
    'primary_content': 'outdoor',
    'selection_source': 'default',
    'transition_speed_multiplier': 1.5,
}
CONTENT_LABELS = {'indoor': '室内', 'outdoor': '室外', 'transition': '转场移动'}


def showcase_options(record):
    declared = record.get('scope', {}).get('showcase')
    if declared is None:
        return None
    if not isinstance(declared, dict):
        raise ValueError('Showcase choices must be an object')
    return {**copy.deepcopy(DEFAULT_SHOWCASE), **declared}


def _validate_options(options):
    order = DEFAULT_SHOWCASE['space_order']
    if options['space_order'] != order:
        raise ValueError('Showcase space order must be living room, balcony, primary bedroom')
    primary = options['primary_content']
    source = options['selection_source']
    if primary not in {'indoor', 'outdoor'} or source not in {'default', 'user'}:
        raise ValueError('Showcase requires indoor/outdoor content and default/user selection')
    if source == 'default' and primary != 'outdoor':
        raise ValueError('Default showcase content is outdoor; indoor requires user selection')
    multiplier = options['transition_speed_multiplier']
    if type(multiplier) not in (int, float) or not math.isfinite(multiplier) or multiplier <= 1:
        raise ValueError('Showcase transition speed multiplier must be finite and greater than one')


def _compact(spaces):
    result = []
    for space in spaces:
        if not result or result[-1] != space:
            result.append(space)
    return result


def validate_showcase(record):
    options = showcase_options(record)
    if options is None:
        return
    _validate_options(options)
    order = options['space_order']
    primary = options['primary_content']
    route = record['scope'].get('route_space_ids')
    if (not isinstance(route, list) or not route
            or any(not isinstance(space, str) or space not in order for space in route)
            or _compact(route) not in [order, [order[0], order[1], order[0], order[2]]]):
        raise ValueError('Showcase route must cover only living room, balcony, primary bedroom in order')
    review = record.get('review_route')
    if review is not None:
        nodes = {n.get('pano_index'): n.get('room_id') for n in review.get('nodes', [])}
        try:
            actual = [nodes[int(n)] for n in review['route'].split('→')]
        except (KeyError, ValueError, AttributeError):
            raise ValueError('Showcase numeric route requires room IDs for every used node')
        if any(space not in order for space in actual) or _compact(actual) != _compact(route):
            raise ValueError('Showcase numeric route space labels differ from selected route')
    displayed = []
    times = {'indoor': 0., 'outdoor': 0.}
    for seg in record.get('segments', []):
        spaces = seg.get('space_ids')
        if (not isinstance(spaces, list) or not spaces
                or any(not isinstance(space, str) or space not in order for space in spaces)):
            raise ValueError('Showcase chapter contains missing or unselected space')
        mode = seg.get('content_mode')
        if mode not in CONTENT_LABELS:
            raise ValueError('Showcase chapter requires indoor/outdoor/transition content mode')
        start, end = seg.get('start_s'), seg.get('end_s')
        if (any(type(value) not in (int, float) or not math.isfinite(value) for value in (start, end))
                or start < 0 or end <= start):
            raise ValueError('Showcase chapter requires finite positive timing')
        if mode in times:
            if len(spaces) != 1:
                raise ValueError('Showcase display chapter must belong to one selected space')
            displayed.extend(spaces)
            times[mode] += end - start
    if _compact(displayed) != order:
        raise ValueError('Showcase display chapters must cover all three spaces in order')
    other = 'indoor' if primary == 'outdoor' else 'outdoor'
    if times[primary] <= times[other]:
        raise ValueError('Primary showcase content must receive more display time than secondary content')


def accelerate_transitions(report):
    """Return a new effective speed map; preserve the baseline and all intervals.

    Only opt-in current maps have showcase + per-interval content_mode. A receipt
    is not a baseline input: rejecting it avoids silently applying the boost twice.
    """
    mapping = copy.deepcopy(report['speed_map'])
    options = showcase_options({'scope': {'showcase': report.get('showcase')}})
    if options is None:
        return mapping
    _validate_options(options)
    if 'baseline_speed_map' in report:
        raise ValueError('Use the baseline speed map, not an already accelerated receipt')
    if not any(part.get('content_mode') == 'transition' for part in mapping):
        raise ValueError('Showcase speed map requires an actual transition interval')
    for part in mapping:
        if part.get('content_mode') not in CONTENT_LABELS:
            raise ValueError('Showcase speed map requires indoor/outdoor/transition classification')
        if part['content_mode'] == 'transition':
            part['speed'] *= options['transition_speed_multiplier']
    return mapping


def showcase_summary(record):
    options = showcase_options(record)
    if options is None:
        return ''
    source = '默认' if options['selection_source'] == 'default' else '用户选择'
    return (f'客厅→阳台→主卧 · {CONTENT_LABELS[options["primary_content"]]}为主（{source}）'
            f' · 仅转场移动在基准上×{options["transition_speed_multiplier"]:g}，展示段不额外加速')
