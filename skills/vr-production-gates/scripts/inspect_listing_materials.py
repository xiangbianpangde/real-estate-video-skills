#!/usr/bin/env python3
"""Read-only inventory of the fixed Beike listing library. Python 3.10+.

Names rank candidates; only actual image inspection establishes suitability.
Prints local paths and hashes, never copies sources or fetches signed URLs.
"""
import argparse
import hashlib
import json
from pathlib import Path


def inspect_materials(root):
    root = Path(root).resolve()
    facts_path = root / '01-房源信息/房源信息.json'
    facts = json.loads(facts_path.read_text(encoding='utf-8'))
    identity = str(facts.get('listing_id', ''))
    if not identity or identity not in root.name.split('-'):
        raise ValueError('Listing directory and facts identity mismatch')

    def entry(path):
        return {'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    original = root / '03-户型图/原始户型图'
    candidates = sorted((p for p in original.glob('*') if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}),
                        key=lambda p: (p.stem != '户型图', p.name))
    auxiliary = sorted((root / '03-户型图/VR户型图').glob('*'))
    groups = {
        'facts': '01-房源信息', 'photos': '02-房源图片', 'floorplans': '03-户型图',
        'vr': '04-完整VR素材', 'video_references': '05-视频素材', 'checks': '06-检查记录',
    }
    resources = ['04-完整VR素材/VR入口.txt', '04-完整VR素材/VR配置/defaultWork.json',
                 '04-完整VR素材/VR配置/vr-manifest.json', '04-完整VR素材/点位及空间清单/点位清单.json']
    work_path=root / '04-完整VR素材/VR配置/defaultWork.json'
    work=json.loads(work_path.read_text(encoding='utf-8')) if work_path.is_file() else {}
    observers=work.get('observers',[])
    point_path=root / '04-完整VR素材/点位及空间清单/点位清单.json'
    point_list=json.loads(point_path.read_text(encoding='utf-8')) if point_path.is_file() else []
    rows=point_list if isinstance(point_list,list) else []
    spatial={
        'observers':[{'pano_index':o.get('index'),'position':o.get('position'),
                      'floor_index':o.get('floor_index'),'accessible_nodes':o.get('accessible_nodes',[])} for o in observers],
        'floorplan_metadata_keys':[key for key in ('hierarchy_floor_plan','outline_floor_plan','standard_floor_plan_url') if work.get(key)],
        'point_list_fields':sorted({k for row in rows if isinstance(row,dict) for k in row}),
        'room_mapping_status':'UNVERIFIED',
        'note':'点位清单可能只是全景六面图索引；observers位置/相邻关系不等于正式户型像素或房间归属。floorplan元数据存在也不证明包含变换。',
    }
    return {
        'schema': 'beike-listing-materials/v1', 'root': str(root), 'listing_id': identity,
        'community': facts.get('community'), 'facts': entry(facts_path),
        'groups': {key: {'path': rel, 'present': (root / rel).is_dir()} for key,rel in groups.items()},
        'floorplan': {'recommended': str(candidates[0].relative_to(root)) if candidates else None,
                      'candidates': [entry(p) for p in candidates],
                      'auxiliary': [entry(p) for p in auxiliary if p.is_file()],
                      'visual_check_required': True,
                      'note': '核彩色布局、门窗及家具；文件名不证明图像类型。VR截图/catalog不自动替代正式户型。'},
        'vr_resources': [entry(root / rel) for rel in resources if (root / rel).is_file()],
        'missing_vr_resources': [rel for rel in resources if not (root / rel).is_file()],
        'spatial_inventory':spatial,
    }


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('listing_root', type=Path)
    args=parser.parse_args()
    print(json.dumps(inspect_materials(args.listing_root), ensure_ascii=False, indent=2))
