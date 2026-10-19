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
            'subtitle_content_mode':'verbatim_voiceover','subtitle_delivery':'burned_in',
            'audio_timeline_binding':'final_audio_alignment_sha256',
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

class SubtitleProfileRegression(unittest.TestCase):
    setUp=ProductionProfileTests.setUp
    def test_keyword_only_rejected(self):
        self.record['scope']['subtitle_content_mode']='editorial_keywords'
        with self.assertRaisesRegex(ValueError,'verbatim'):validate_production_profile(self.record)
    def test_unburned_subtitles_rejected(self):
        self.record['scope']['subtitle_delivery']='selectable_track'
        with self.assertRaisesRegex(ValueError,'burned'):validate_production_profile(self.record)

class HumanCameraProfileTests(unittest.TestCase):
    def base(self):
        return {'scope':{'production_profile':'human-camera-choice-v1','duration_s':25,'route':'客厅→阳台→主卧','camera_profile':{'aspect_ratio':'4:3','vertical_fov_deg':80,'height_m':1.6},'movement_choices':[{'id':'MOV-006','execution_status':'candidate'},{'id':'MOV-001','execution_status':'reference_only'},{'id':'MOV-005','execution_status':'style_reference_only'}]}}
    def test_human_camera_profile_accepts_declared_choices(self):
        from storyboard.model import validate_human_camera_profile
        validate_human_camera_profile(self.base())
    def test_mov005_cannot_be_upgraded(self):
        from storyboard.model import validate_human_camera_profile
        r=self.base();r['scope']['movement_choices'][-1]['execution_status']='candidate'
        with self.assertRaisesRegex(ValueError,'style reference'):validate_human_camera_profile(r)
    def test_default_profile_is_unaffected(self):
        from storyboard.model import validate_human_camera_profile
        validate_human_camera_profile({'scope':{'production_profile':'house-short-v1','duration_s':30}})
