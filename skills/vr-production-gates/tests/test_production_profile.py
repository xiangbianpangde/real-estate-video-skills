"""User-fixed requirements reject the options that were incorrectly proposed."""
import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from storyboard.model import validate_production_profile


class ProductionProfileTests(unittest.TestCase):
    def setUp(self):
        self.record={'scope':{'production_profile':'house-short-v1','duration_s':30,
            'render_config':{'width':720,'height':1280},
            'editing_policy':{'single_take_required':True,'allow_cuts':False,'allow_remove_intervals':False,'allow_speed_changes':True},
            'voiceover_provider':'mcode','bgm_source':'specified_library',
            'shot_constraints':{'excluded_spaces':['bathroom']}}}
    def test_current_requirements_and_local_speed_changes_allowed(self):
        validate_production_profile(self.record)
    def test_old_ninety_second_recommendation_rejected(self):
        self.record['scope']['duration_s']=90
        with self.assertRaisesRegex(ValueError,'25-35'):validate_production_profile(self.record)
    def test_landscape_rejected(self):
        self.record['scope']['render_config']={'width':1920,'height':1080}
        with self.assertRaisesRegex(ValueError,'portrait'):validate_production_profile(self.record)
    def test_cuts_or_deleted_intervals_rejected(self):
        for field in ['allow_cuts','allow_remove_intervals']:
            record=copy.deepcopy(self.record);record['scope']['editing_policy'][field]=True
            with self.assertRaisesRegex(ValueError,'single take'):validate_production_profile(record)
    def test_generated_music_or_unapproved_voice_provider_rejected(self):
        for field,value in [('bgm_source','generated'),('voiceover_provider','system_say')]:
            record=copy.deepcopy(self.record);record['scope'][field]=value
            with self.assertRaisesRegex(ValueError,'mcode'):validate_production_profile(record)
    def test_approved_minimax_cn_provider_allowed(self):
        self.record['scope']['voiceover_provider']='minimax_cn'
        validate_production_profile(self.record)
    def test_bathroom_exclusion_required(self):
        self.record['scope']['shot_constraints']['excluded_spaces']=[]
        with self.assertRaisesRegex(ValueError,'bathroom'):validate_production_profile(self.record)
    def test_historical_unprofiled_record_not_rewritten(self):
        validate_production_profile({'scope':{'duration_s':106.5}})
