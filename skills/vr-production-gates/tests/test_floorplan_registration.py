"""Geometric failures previously hidden by 'approximate' route labels."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from storyboard.floorplan_registration import fit_similarity, project, validate_registration


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.anchors=[{'world_xy':[0,0],'floorplan_xy':[10,20]},
                      {'world_xy':[2,0],'floorplan_xy':[30,20]},
                      {'world_xy':[0,2],'floorplan_xy':[10,40]}]
        self.route={'floorplan':'floor.png','nodes':[{'pano_index':9,'floorplan_xy':[15,25],
                    'room_id':'bath','room_evidence':'frame-p9: sink and shower visible'}],
                    'registration':{'mode':'room_schematic','floorplan_sha256':'a'*64,
                    'rooms':[{'id':'bath','polygon':[[10,20],[20,20],[20,30],[10,30]]},
                             {'id':'bed','polygon':[[30,20],[40,20],[40,30],[30,30]]}]}}

    def test_fit_uses_explicit_axis_and_preserves_geometry(self):
        result=fit_similarity(self.anchors)
        self.assertAlmostEqual(result['max_anchor_error_px'],0)
        self.assertEqual(project([1,1],result['matrix']),[20,30])

    def test_collinear_anchors_do_not_establish_registration(self):
        self.anchors[2]={'world_xy':[4,0],'floorplan_xy':[50,20]}
        with self.assertRaisesRegex(ValueError,'non-collinear'):
            fit_similarity(self.anchors)

    def test_room_schematic_does_not_need_global_metric_fit(self):
        validate_registration(self.route)

    def test_wet_point_inside_bedroom_rejected_even_if_approximate(self):
        self.route['nodes'][0]['floorplan_xy']=[35,25]
        with self.assertRaisesRegex(ValueError,'outside verified room'):
            validate_registration(self.route)

    def test_unknown_room_evidence_is_not_accepted(self):
        self.route['nodes'][0]['room_evidence']=''
        with self.assertRaisesRegex(ValueError,'Room identity evidence'):
            validate_registration(self.route)

    def calibrated(self):
        for anchor in self.anchors:anchor['evidence']='source SDK marker correspondence'
        reg=self.route['registration'];reg.update(mode='world_similarity',anchors=self.anchors,
            matrix=fit_similarity(self.anchors)['matrix'],axis='xz',max_error_px=1,
            checks=[{'world_xy':[1,1],'floorplan_xy':[20,30],'evidence':'independent SDK marker'}])
        self.route['nodes'][0]['world_xy']=[.5,.5]
        return reg

    def test_independent_check_exposes_bad_transform(self):
        reg=self.calibrated();validate_registration(self.route)
        reg['checks'][0]['floorplan_xy']=[45,70]
        with self.assertRaisesRegex(ValueError,'Independent check'):
            validate_registration(self.route)

    def test_fit_anchors_cannot_double_as_independent_check(self):
        reg=self.calibrated();reg['checks']=[dict(self.anchors[0],evidence='same anchor')]
        with self.assertRaisesRegex(ValueError,'Independent check'):
            validate_registration(self.route)

    def test_metric_nodes_must_use_actual_transform(self):
        self.calibrated();self.route['nodes'][0]['world_xy']=[1,1]
        with self.assertRaisesRegex(ValueError,'Node transform'):
            validate_registration(self.route)
