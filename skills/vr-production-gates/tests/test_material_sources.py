"""Fixed-library selection failures; synthetic files do not certify image content."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/inspect_listing_materials.py'


class MaterialSourcesTests(unittest.TestCase):
    def inspect(self, root):
        spec = importlib.util.spec_from_file_location('listing_materials', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.inspect_materials(root)

    def test_named_floorplan_preferred_over_detail_and_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / '武汉-123-测试小区'
            info = root / '01-房源信息/房源信息.json'
            info.parent.mkdir(parents=True)
            info.write_text(json.dumps({'listing_id':'123','community':'测试小区'}))
            for rel in ['原始户型图/户型图.jpg','原始户型图/floorplan-detail.jpg','VR户型图/catalog.jpg']:
                p = root / '03-户型图' / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'synthetic image')
            result = self.inspect(root)
            self.assertEqual(result['floorplan']['recommended'], '03-户型图/原始户型图/户型图.jpg')
            self.assertEqual(len(result['floorplan']['candidates']), 2)
            self.assertTrue(result['floorplan']['visual_check_required'])
            self.assertNotIn('catalog.jpg', str(result['floorplan']['candidates']))

    def test_single_detail_candidate_still_needs_image_inspection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'武汉-123-测试小区'
            p=root/'01-房源信息/房源信息.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps({'listing_id':'123'}))
            p=root/'03-户型图/原始户型图/floorplan-detail.jpg';p.parent.mkdir(parents=True)
            p.write_bytes(b'synthetic image')
            result=self.inspect(root)
            self.assertTrue(result['floorplan']['visual_check_required'])
            self.assertEqual(len(result['floorplan']['candidates']),1)

    def test_mismatched_listing_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'武汉-123-测试小区'
            p=root/'01-房源信息/房源信息.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps({'listing_id':'456'}))
            with self.assertRaisesRegex(ValueError,'identity'):
                self.inspect(root)

    def test_panorama_catalog_is_not_room_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'武汉-123-测试小区'
            for rel,data in [('01-房源信息/房源信息.json',{'listing_id':'123'}),
                             ('04-完整VR素材/VR配置/defaultWork.json',{'observers':[{'index':0,'position':[1,2,3],'accessible_nodes':[1]}]}),
                             ('04-完整VR素材/点位及空间清单/点位清单.json',[{'index':0,'front':'test'}])]:
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data))
            spatial=self.inspect(root)['spatial_inventory']
            self.assertEqual(spatial['room_mapping_status'],'UNVERIFIED')
            self.assertEqual(spatial['point_list_fields'],['front','index'])
            self.assertEqual(spatial['observers'][0]['position'],[1,2,3])
