"""CLI route-board contract regression; synthetic sources, no visual certification."""
import copy,json,subprocess,sys,unittest
from pathlib import Path
import test_storyboard as fixtures

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/build_script_package.py'

class RouteBoardTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.RendererTests();self.fixture.setUp();self.root=self.fixture.p;self.record=self.fixture.record
        first=self.record['segments'][0];first['visual']['role']='opening'
        last=copy.deepcopy(first);last.update(id='S02',start_s=4,end_s=8);last['visual'].update(role='ending',title='室内收束',layout='ending_composite',cta='欢迎留言。',motion={'kind':'static','label':'主体收束'})
        self.record['segments'].append(last);self.record['scope'].update(duration_s=8,route='0→1')
        self.record['design_system']={'id':'real-estate-storyboard','version':'1.1.0'}
        self.record['review_route']={'purpose':'script_review_only','included_in_video':False,'floorplan':'floor.png','route':'0→1','caption':'人工示意对齐，不是现实测绘。','nodes':[{'pano_index':0,'floorplan_xy':[.2,.2]},{'pano_index':1,'floorplan_xy':[.8,.8]}],'chapters':[{'id':s['id'],'title':s['visual']['title'],'start_s':s['start_s'],'end_s':s['end_s'],'pano_indices':[0] if i==0 else [0,1],'stop_pano':i,'motion_kind':'static'} for i,s in enumerate(self.record['segments'])]}
    def tearDown(self):self.fixture.tearDown()
    def invoke(self):
        (self.root/'record.json').write_text(json.dumps(self.record));return subprocess.run([sys.executable,str(SCRIPT),'--record',str(self.root/'record.json'),'--floorplan','floor.png','--output-dir',str(self.root/'package')],capture_output=True,text=True)
    def editing_policy(self):
        self.record['scope'].update(continuity_class='cross_room_travel',editing_policy={'single_take_required':True,'allow_cuts':False,'allow_remove_intervals':False,'allow_speed_changes':True})

    def test_single_take_policy_rejects_cut_exception(self):
        from storyboard.model import validate
        self.editing_policy();self.record['scope']['continuity_class']='approved_cut_exception'
        with self.assertRaisesRegex(ValueError,'Single take'):
            validate(self.record)

    def test_single_take_policy_rejects_cut_deletion_permission(self):
        from storyboard.model import validate
        self.editing_policy();self.record['scope']['editing_policy']['allow_remove_intervals']=True
        with self.assertRaisesRegex(ValueError,'Single take'):
            validate(self.record)

    def test_single_take_speed_map_preserves_timeline(self):
        from storyboard.model import validate
        self.editing_policy();self.record['scope'].update(editing_source_duration_s=10,speed_map=[{'source_start_s':0,'source_end_s':4,'speed':1.25},{'source_start_s':4,'source_end_s':10,'speed':1}])
        validate(self.record)
        self.record['scope']['speed_map'][1]['source_start_s']=5
        with self.assertRaisesRegex(ValueError,'Speed map'):
            validate(self.record)

    def test_cut_is_separate_from_navigation(self):
        self.record['scope']['continuity_class']='approved_cut_exception'
        self.record['review_route']['cuts']=[{'from_pano':0,'to_pano':1,'label':'剪辑切换'}]
        from storyboard.route_board import route_document
        from storyboard.render import load
        (self.root/'record.json').write_text(json.dumps(self.record,ensure_ascii=False))
        record,images=load(self.root/'record.json','floor.png')
        page=route_document(record,images,'floor.png')
        self.assertIn('data-cut="0-1"',page)
        self.assertNotIn('data-edge="0-1"',page)
        self.assertIn('剪辑切换',page)

    def test_cut_cannot_claim_continuous_route(self):
        self.record['scope']['continuity_class']='cross_room_travel'
        self.record['review_route']['cuts']=[{'from_pano':0,'to_pano':1,'label':'剪辑切换'}]
        from storyboard.model import validate
        with self.assertRaisesRegex(ValueError,'Cut requires'):
            validate(self.record)

    def test_single_chinese_document_contains_full_route(self):
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        route=(self.root/'package/视频剧本.html').read_text();md=(self.root/'package/剧本正文.md').read_text()
        self.assertEqual([p.name for p in (self.root/'package').glob('*.html')],['视频剧本.html'])
        self.assertIn('data-route-chapter="S01"',route);self.assertIn('data-route-chapter="S02"',route)
        self.assertIn('P0 → P1',route);self.assertIn('0.00–4.00秒',route);self.assertIn('主体收束',route)
        self.assertIn('视频剧本.html',md);self.assertIn('一、完整方案板',md);self.assertIn('户型运镜路线图',md)
    def test_bound_first_last_preview_preserved(self):
        (self.root/'preview.png').write_bytes((self.root/'source.png').read_bytes())
        from run import sha
        self.record['assets'].append({'path':'preview.png','sha256':sha(self.root/'preview.png'),'role':'design_preview','origin':'rendered_board'})
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        md=(self.root/'package/剧本正文.md').read_text();self.assertIn('首尾层次与字幕顺序',md);self.assertIn('../preview.png',md)

    def test_missing_route_rejected(self):
        self.record.pop('review_route');result=self.invoke();self.assertNotEqual(result.returncode,0);self.assertIn('Complete review route required',result.stderr)
    def test_missing_chapter_rejected(self):
        self.record['review_route']['chapters'].pop();result=self.invoke();self.assertNotEqual(result.returncode,0);self.assertIn('Route chapters must match script',result.stderr)
    def test_stale_time_rejected(self):
        self.record['review_route']['chapters'][1]['end_s']=103;result=self.invoke();self.assertNotEqual(result.returncode,0);self.assertIn('Route chapter identity mismatch',result.stderr)
    def test_stale_route_rejected(self):
        self.record['review_route']['route']='1→0';result=self.invoke();self.assertNotEqual(result.returncode,0);self.assertIn('Route sequence differs from scope',result.stderr)
    def test_unknown_node_rejected(self):
        self.record['review_route']['nodes'].pop();result=self.invoke();self.assertNotEqual(result.returncode,0);self.assertIn('Route references unknown node',result.stderr)
    def test_same_node_keeps_multiple_chapter_labels(self):
        self.record['scope']['route']='0';self.record['review_route']['route']='0'
        self.record['review_route']['chapters'][1].update(pano_indices=[0],stop_pano=0)
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        route=(self.root/'package/视频剧本.html').read_text();self.assertIn('S01 / S02',route)

class RegistrationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=RouteBoardTests();self.fixture.setUp()
        self.record=self.fixture.record
    def tearDown(self):self.fixture.tearDown()
    def registration(self):
        from run import sha
        route=self.record['review_route']
        route['registration']={'mode':'room_schematic','floorplan_sha256':sha(self.fixture.root/'floor.png'),
                               'rooms':[{'id':'living','polygon':[[0,0],[1,0],[1,1],[0,1]]}]}
        for node in route['nodes']:node.update(room_id='living',room_evidence='synthetic fixture frame')
    def test_registered_schematic_keeps_complete_document(self):
        self.registration()
        result=self.fixture.invoke();self.assertEqual(result.returncode,0,result.stderr)
        page=(self.fixture.root/'package/视频剧本.html').read_text()
        self.assertIn('房间级近似示意',page)
        self.assertIn('data-route-chapter="S02"',page)
    def test_changed_floorplan_rejects_old_registration(self):
        self.registration();self.record['review_route']['registration']['floorplan_sha256']='0'*64
        result=self.fixture.invoke();self.assertNotEqual(result.returncode,0)
        self.assertIn('floorplan image changed',result.stderr)
        self.assertFalse((self.fixture.root/'package').exists())
    def test_new_real_plan_without_registration_rejected(self):
        self.record['fixture']=False;self.record['design_system']['version']='1.3.0'
        from storyboard.model import validate
        with self.assertRaisesRegex(ValueError,'registration mode'):validate(self.record)

if __name__=='__main__':unittest.main()

class ContinuousPlanTests(unittest.TestCase):
    def setUp(self):
        self.fixture=RouteBoardTests();self.fixture.setUp()
        self.record=self.fixture.record
        self.record['fixture']=False
        self.record['design_system']['version']='1.2.0'
        self.fixture.editing_policy()
    def tearDown(self):self.fixture.tearDown()
    def test_real_single_take_without_connected_motion_plan_rejected(self):
        from storyboard.model import validate
        with self.assertRaisesRegex(ValueError,'Connected motion'):
            validate(self.record)
    def test_connected_motion_plan_can_be_pending_dynamic_review(self):
        from storyboard.model import validate
        self.record['review_route']['transitions']=[{'from_pano':0,'to_pano':1,'movement':'forward','view':'先转向门口再正向移动','duration_s':2}]
        validate(self.record)
        self.record['review_route']['transitions'][0]['movement']='backward'
        with self.assertRaisesRegex(ValueError,'Forward'):
            validate(self.record)
