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
    def test_route_board_is_independent_and_in_document(self):
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        route=(self.root/'package/route-board.html').read_text();md=(self.root/'package/plan.md').read_text()
        self.assertIn('data-route-chapter="S01"',route);self.assertIn('data-route-chapter="S02"',route)
        self.assertIn('P0 → P1',route);self.assertIn('0.00–4.00秒',route);self.assertIn('主体收束',route)
        self.assertIn('route-board.png',md);self.assertIn('一、完整方案板',md);self.assertIn('户型运镜路线图',md)
    def test_bound_first_last_preview_preserved(self):
        (self.root/'preview.png').write_bytes((self.root/'source.png').read_bytes())
        from run import sha
        self.record['assets'].append({'path':'preview.png','sha256':sha(self.root/'preview.png'),'role':'design_preview','origin':'rendered_board'})
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        md=(self.root/'package/plan.md').read_text();self.assertIn('首尾层次与字幕顺序',md);self.assertIn('../preview.png',md)

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
        route=(self.root/'package/route-board.html').read_text();self.assertIn('S01 / S02',route)

if __name__=='__main__':unittest.main()
