"""Complete review-only route view. Shared by the board, standalone and script."""
import math
import struct


def validate_route(record):
    route=record.get('review_route')
    required=record.get('design_system',{}).get('version')=='1.1.0'
    if route is None:
        if required:raise ValueError('Complete review route required')
        return
    if not isinstance(route,dict) or route.get('purpose')!='script_review_only' or route.get('included_in_video') is not False:
        raise ValueError('Route must be explicitly review-only')
    if not route.get('floorplan') or not isinstance(route.get('caption'),str) or not route['caption'].strip():
        raise ValueError('Route floorplan and limitations required')
    if route.get('route')!=record['scope'].get('route'):
        raise ValueError('Route sequence differs from scope')
    try:seq=[int(x) for x in route['route'].split('→')]
    except (KeyError,AttributeError,ValueError):raise ValueError('Explicit numeric route sequence required')
    if not seq or any(x<0 for x in seq):raise ValueError('Explicit numeric route sequence required')
    nodes=route.get('nodes',[]);points={}
    for node in nodes:
        index=node.get('pano_index');xy=node.get('floorplan_xy')
        if type(index) is not int or index<0 or index in points or not isinstance(xy,list) or len(xy)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in xy):
            raise ValueError('Unique route nodes with finite coordinates required')
        points[index]=xy
    if any(x not in points for x in seq):raise ValueError('Route references unknown node')
    chapters=route.get('chapters',[]);segments=record['segments']
    if not isinstance(chapters,list) or [c.get('id') for c in chapters]!=[s['id'] for s in segments]:
        raise ValueError('Route chapters must match script')
    traversed=[]
    for chapter,seg in zip(chapters,segments):
        if any(chapter.get(key)!=expected for key,expected in [('title',seg['visual']['title']),('start_s',seg['start_s']),('end_s',seg['end_s'])]):
            raise ValueError('Route chapter identity mismatch: '+seg['id'])
        ids=chapter.get('pano_indices')
        if not isinstance(ids,list) or not ids or any(type(x) is not int or x not in points for x in ids) or chapter.get('stop_pano')!=ids[-1]:
            raise ValueError('Route chapter path mismatch: '+seg['id'])
        if chapter.get('motion_kind') not in {'static','pan','travel','orbit','fov'}:
            raise ValueError('Explicit route chapter motion required')
        for node in ids:
            if not traversed or traversed[-1]!=node:traversed.append(node)
    compact=[]
    for node in seq:
        if not compact or compact[-1]!=node:compact.append(node)
    if traversed!=compact:raise ValueError('Chapter paths do not cover the full route')


ROUTE_CSS='''
.route-review{background:white;border:1px solid #d5e5e8;border-radius:16px;padding:28px;margin:24px 0;color:#193c47}
.route-review h2{font-size:34px;margin:0 0 12px}.route-grid{display:grid;grid-template-columns:1.05fr 1fr;gap:36px}
.route-map{display:block;width:100%;height:1160px}.route-list{list-style:none;margin:0;padding:0}
.route-list li{padding:14px 12px;border-bottom:1px solid #d5e5e8;line-height:1.5}
.route-list b{display:block;font-size:25px}.route-list span,.route-list code{display:block;font:22px/1.6 inherit}
.route-list code{font-family:inherit;color:#176cb1;font-size:23px}.route-list span{color:#527984;font-size:21px}
.route-note{background:#e7f3fc;border-left:5px solid #1577ce;padding:16px;font-size:21px;line-height:1.65}
.route-legend{font-size:21px;color:#527984;line-height:1.65}.route-review p{overflow-wrap:anywhere}
'''


def route_section(record, images, floorplan):
    from .components import esc,image,motion_component
    from .model import motion_steps
    validate_route(record)
    route=record['review_route']
    if route['floorplan']!=str(floorplan):raise ValueError('Route floorplan differs from bound image')
    width,height=struct.unpack('>II',images[str(floorplan)][16:24]);box=route.get('view_box',[0,0,width,height])
    if len(box)!=4 or any(type(x) not in (int,float) or not math.isfinite(x) for x in box) or min(box[:2])<0 or min(box[2:])<=0 or box[0]+box[2]>width or box[1]+box[3]>height:
        raise ValueError('Route map view box outside source image')
    points={n['pano_index']:n['floorplan_xy'] for n in route['nodes']};seq=[int(x) for x in route['route'].split('→')]
    parts=[f'<svg class="route-map" role="img" aria-label="完整章节路线与户型对应图" viewBox="{" ".join(str(x) for x in box)}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="route-arrow" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto"><path d="M0 0 L5 2.5 L0 5" fill="#1577ce"/></marker></defs><image href="{image(images[str(floorplan)])}" width="{width}" height="{height}"/>']
    seen=set()
    for a,b in zip(seq,seq[1:]):
        if a==b:continue
        x,y=points[a];u,v=points[b];back=(b,a) in seen;dash=' stroke-dasharray="17 12"' if back else ''
        parts.append(f'<path data-edge="{a}-{b}" data-return="{str(back).lower()}" d="M{x} {y} L{u} {v}" fill="none" stroke="white" stroke-width="13"/><path d="M{x} {y} L{u} {v}" fill="none" stroke="#1577ce" stroke-width="7"{dash} marker-end="url(#route-arrow)"/>');seen.add((a,b))
    anchors={}
    for c in route['chapters']:anchors.setdefault(c['stop_pano'],[]).append(c['id'])
    for node in sorted(set(seq)):
        x,y=points[node];label=' / '.join(anchors.get(node,[]));offset=route.get('label_offsets',{}).get(str(node),[36,-32])
        parts.append(f'<g data-node="{node}"><circle cx="{x}" cy="{y}" r="21" fill="#1577ce" stroke="white" stroke-width="5"/><text x="{x}" y="{y+7}" text-anchor="middle" font-size="22" fill="white">{node}</text><text x="{x+offset[0]}" y="{y+offset[1]}" font-size="29" fill="#1264a7" font-weight="bold" stroke="white" stroke-width="7" paint-order="stroke">{esc(label or "P"+str(node))}</text></g>')
    parts.append('</svg>');rows=[]
    for c,s in zip(route['chapters'],record['segments']):
        label=' → '.join(step['label'] for step in motion_steps(s['visual']))
        rows.append(f'<li data-route-chapter="{esc(s["id"])}" data-start="{s["start_s"]}" data-end="{s["end_s"]}" data-panos="{"→".join(str(n) for n in c["pano_indices"])}"><b>{esc(s["id"])} · {esc(s["visual"]["title"])}</b><span>{s["start_s"]:.2f}–{s["end_s"]:.2f}秒 · {esc(label)}</span><code>{" → ".join("P"+str(n) for n in c["pano_indices"])}</code></li>')
    return '<section class="route-review" data-complete-route-board="true"><h2>户型运镜路线图 · 仅用于剧本审核</h2><p class="route-legend">蓝线＋箭头：导航顺序　虚线：重复回程　圆点：点位　S-ID：章节停留点（同点可对应多章）</p><div class="route-grid"><div>'+''.join(parts)+'</div><div><ul class="route-list">'+''.join(rows)+'</ul><p class="route-note">'+esc(route['caption'])+'</p><p class="route-note">'+esc(record.get('board_content',{}).get('limitations','候选路线需按本方法动态验证，静态图不证明实际连续性。'))+'</p><p class="route-legend">本图不进入视频、不占成片时长，不继承旧版批准。</p></div></div></section>'


def route_document(record,images,floorplan):
    from .components import esc
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+esc(record.get('storyboard_title','完整路线方案板'))+'</title><style>*{box-sizing:border-box}body{width:1900px;margin:0;padding:36px;background:#f7faf9;font:22px/1.6 "PingFang SC",sans-serif;color:#193c47}h1{font-size:42px}'+ROUTE_CSS+'</style><h1>'+esc(record.get('storyboard_title','完整路线方案板'))+'</h1><p>'+esc(record['plan']['version'])+' · 五项逐章对应：S-ID、标题、时码、动作、导航路径</p>'+route_section(record,images,floorplan)+'</html>'
