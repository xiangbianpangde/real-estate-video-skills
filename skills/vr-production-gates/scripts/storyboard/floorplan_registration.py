"""Explicit 2D registration, independent checks and room containment. No image recognition."""
import math


def point(value):
    if not isinstance(value,list) or len(value)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in value):
        raise ValueError('Finite 2D coordinate required')
    return value


def project(xy, matrix):
    x,y=point(xy)
    if not isinstance(matrix,list) or len(matrix)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in matrix):
        raise ValueError('Similarity matrix must be [a,b,tx,ty]')
    a,b,tx,ty=matrix
    if a*a+b*b<=1e-12:raise ValueError('Nonzero similarity scale required')
    return [a*x-b*y+tx,b*x+a*y+ty]


def fit_similarity(anchors):
    if not isinstance(anchors,list) or len(anchors)<3:raise ValueError('Three non-collinear anchors required')
    source=[point(a['world_xy']) for a in anchors];target=[point(a['floorplan_xy']) for a in anchors]
    for coords in (source,target):
        x0,y0=coords[0]
        if not any(abs((x-x0)*(v-y0)-(y-y0)*(u-x0))>1e-8 for x,y in coords[1:] for u,v in coords[1:]):
            raise ValueError('Three non-collinear anchors required')
    n=len(source);sx=sum(p[0] for p in source)/n;sy=sum(p[1] for p in source)/n
    tx=sum(p[0] for p in target)/n;ty=sum(p[1] for p in target)/n
    denominator=sum((x-sx)**2+(y-sy)**2 for x,y in source)
    a=sum((x-sx)*(u-tx)+(y-sy)*(v-ty) for (x,y),(u,v) in zip(source,target))/denominator
    b=sum((x-sx)*(v-ty)-(y-sy)*(u-tx) for (x,y),(u,v) in zip(source,target))/denominator
    matrix=[a,b,tx-a*sx+b*sy,ty-b*sx-a*sy]
    return {'matrix':matrix,'max_anchor_error_px':max(math.dist(project(p,matrix),q) for p,q in zip(source,target))}


def contains(xy, polygon):
    x,y=point(xy);vertices=[point(p) for p in polygon]
    if len(vertices)<3:raise ValueError('Room polygon needs three vertices')
    inside=False
    for (a,b),(c,d) in zip(vertices,vertices[1:]+vertices[:1]):
        if abs((x-a)*(d-b)-(y-b)*(c-a))<1e-8 and min(a,c)<=x<=max(a,c) and min(b,d)<=y<=max(b,d):return True
        if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:inside=not inside
    return inside


def validate_registration(route):
    reg=route.get('registration')
    if not isinstance(reg,dict) or reg.get('mode') not in {'room_schematic','world_similarity'}:
        raise ValueError('Explicit floorplan registration mode required')
    digest=reg.get('floorplan_sha256','')
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Registration must bind floorplan SHA256')
    rooms={}
    for room in reg.get('rooms',[]):
        name=room.get('id');polygon=room.get('polygon',[])
        if not isinstance(name,str) or not name or name in rooms or len(polygon)<3:raise ValueError('Unique room polygon required')
        contains(polygon[0],polygon)
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
        if abs(area)<1e-8:raise ValueError('Room polygon must enclose an area')
        rooms[name]=polygon
    for node in route['nodes']:
        if not isinstance(node.get('room_evidence'),str) or not node['room_evidence'].strip() or node.get('room_id') not in rooms:
            raise ValueError('Room identity evidence required for every plotted node')
        if not contains(node['floorplan_xy'],rooms[node['room_id']]):
            raise ValueError('Node outside verified room: '+str(node['pano_index']))
    if reg['mode']=='room_schematic':return
    if reg.get('axis') not in {'xy','xz','yz','x-z','z-x'}:raise ValueError('Explicit world axis convention required')
    tolerance=reg.get('max_error_px')
    if type(tolerance) not in (int,float) or not math.isfinite(tolerance) or tolerance<=0:raise ValueError('Source-specific error tolerance required')
    anchors=reg.get('anchors',[]);fit=fit_similarity(anchors);matrix=reg.get('matrix')
    if any(not str(anchor.get('evidence','')).strip() for anchor in anchors):
        raise ValueError('Anchor correspondence evidence required')
    if fit['max_anchor_error_px']>tolerance or any(math.dist(project(a['world_xy'],matrix),a['floorplan_xy'])>tolerance for a in anchors):
        raise ValueError('Anchor residual exceeds stated tolerance')
    checks=reg.get('checks',[])
    if not checks:raise ValueError('Independent check required beyond fit anchors')
    for check in checks:
        if not str(check.get('evidence','')).strip() or any(check['world_xy']==a['world_xy'] for a in anchors) or math.dist(project(check['world_xy'],matrix),point(check['floorplan_xy']))>tolerance:
            raise ValueError('Independent check failed or duplicates fit anchor')
    for node in route['nodes']:
        if math.dist(project(node.get('world_xy'),matrix),node['floorplan_xy'])>tolerance:
            raise ValueError('Node transform differs from recorded coordinate')


if __name__=='__main__':
    import argparse
    import json
    from pathlib import Path
    parser=argparse.ArgumentParser(description='Python 3.10+; fit explicit anchor JSON or validate a review_route JSON. Read-only, prints result.')
    parser.add_argument('input',type=Path)
    parser.add_argument('--fit',action='store_true',help='Input contains anchors; prints fit without certifying room identity')
    args=parser.parse_args()
    data=json.loads(args.input.read_text(encoding='utf-8'))
    if args.fit:print(json.dumps(fit_similarity(data['anchors']),ensure_ascii=False,indent=2))
    else:
        validate_registration(data)
        print(json.dumps({'structural_checks':'PASS','image_identity_and_visual_review':'NOT_CHECKED_BY_THIS_CLI'},ensure_ascii=False))
