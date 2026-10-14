"""Generate the board and detailed script from the same validated record."""
import json
from pathlib import Path
from .components import chapter_card, image, esc
from .model import validate, bind_images, motion_steps

DESIGN = Path(__file__).resolve().parents[2] / 'design-system'


def render_html(record, images, floorplan):
    tokens = json.loads((DESIGN/'tokens.json').read_text())
    css = []
    for group, values in tokens.items():
        if not isinstance(values, dict): continue
        for name, value in values.items():
            css.append(f'--{group}-{name}:{value}{"px" if isinstance(value,(float,int)) else ""};')
    count = len(record['segments'])
    width = int(record.get('board_width', min(2880,max(1280,count*330+96))))
    if not 960 <= width <= 6000: raise ValueError('Board width must be 960..6000 CSS pixels')
    columns = min(count,tokens['layout']['max_columns'],max(1,(width-2*tokens['space']['page'])//tokens['layout']['card_min_width']))
    css.extend([f'--board-width:{width}px;',f'--columns:{columns};'])
    scope, content = record['scope'], record.get('board_content',{})
    fixture = record.get('fixture') is True
    title = record.get('storyboard_title','房源介绍 · 拍前图文方案')
    subtitle_mode = scope.get('subtitle_content_mode','未声明')
    subtitle_delivery = scope.get('subtitle_delivery','未声明')
    cards = ''.join(chapter_card(s,images,floorplan,fixture) for s in record['segments'])
    notes = content.get('changes', [])
    if not isinstance(notes,list): raise ValueError('board_content.changes must be a list')
    changes = ''.join(f'<div class="note"><b>{esc(note["title"])}</b><p>{esc(note["text"])}</p></div>' for note in notes)
    shape = scope.get('render_config',{})
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{esc(title)}</title>
<style>:root{{{''.join(css)}}}{(DESIGN/'styles.css').read_text()}</style><main id="board">
<header><div class="eyebrow">{esc(scope['source_namespace'])} · {esc(record['plan']['version'])} · {esc(record.get('status','DRAFT'))}</div><h1>{esc(title)}</h1>
<p>{' → '.join(esc(s['visual']['title']) for s in record['segments'])}</p>
<div class="notice">约{scope['duration_s']:.1f}秒 · {esc(shape.get('width','待定'))}×{esc(shape.get('height','待定'))} · {esc(scope['render_method'])}</div>
<p class="status">{'全部为虚构测试素材，不是房源脚本，不授权采集。' if fixture else '真实源参考、动作示意与布局预览分别标注；本图不表示已完成视频或用户已接受。'}</p></header>
<section class="cards">{cards}</section><section class="lower"><div class="panel"><h3>户型：整体布局参考</h3><img class="floorplan" src="{image(images[str(floorplan)])}" alt="{'合成测试户型' if fixture else '当前房源户型原图'}"><p>{esc(content.get('fact_caption','事实详见同版来源及合同'))}</p><p class="caption">{'合成测试素材' if fixture else '保留原图比例；不作为现实路径测绘'}</p></div>
<div class="panel"><h3>整片设计与审核范围</h3>{changes}
<div class="note"><b>首尾设计</b><p>{esc(scope['opening'])}</p><p>{esc(scope['ending'])}</p></div>
<div class="note"><b>声音与字幕</b><p>{esc(scope.get('voiceover','按当前口播合同'))}</p><p>{esc(scope['bgm'])}</p><p>{esc(subtitle_mode)} / {esc(subtitle_delivery)}</p></div>
<div class="note"><b>已知限制与待确认项</b><p>{esc(content.get('limitations','逐卡核对标注的限制和待确认项。'))}</p></div></div></section>
<footer class="footer"><b>一次整包审核 → 一次正式采集及获批后期 → 按S-ID审成片</b><p>{esc(scope.get('facts_and_rights','事实及权利以同版合同为准'))}</p><p>发布与最终接受独立。本设计图不授予生产权限。</p></footer></main></html>'''


def render_markdown(record, floorplan):
    s = record['scope']
    lines = [f'# {record.get("storyboard_title","图文拍摄脚本")} · {record["plan"]["version"]}', '',
             f'状态：{record.get("status","DRAFT")}；方案板与本正文由同一record.json生成。', '',
             '![整体方案板](overview.png)', '', '## 制作范围', '',
             f'- 房源：{s["source_namespace"]}；方法：{s["render_method"]}；范围：{s.get("validation_scope","未声明")}。',
             f'- 时长：{s["duration_s"]}秒；配置：{json.dumps(s.get("render_config",{}),ensure_ascii=False)}。']
    for key in ['opening','ending','bgm','route','facts_and_rights']:
        lines.append(f'- {key}：{s.get(key,"未声明")}')
    lines += [f'- 覆盖：{"、".join(s.get("coverage",[]))}',f'- 字幕：{s.get("subtitle_content_mode","未声明")} / {s.get("subtitle_delivery","未声明")}。',
              f'- 授权范围：{json.dumps(s.get("authorized_actions",[]),ensure_ascii=False)}。',f'- 未授权：{json.dumps(s.get("not_authorized",[]),ensure_ascii=False)}。',f'- 原户型图：{floorplan}']
    for key in ['render_validation','visual_acceptance']:
        if key in s: lines += [f'- {key}：{json.dumps(s[key],ensure_ascii=False)}']
    content = record.get('board_content', {})
    lines += ['', '## 调整与待审核项', '']
    for note in content.get('changes', []):
        lines.append(f'- {note["title"]}：{note["text"]}')
    if content.get('limitations'):lines.append('- 限制：'+content['limitations'])
    if content.get('fact_caption'):lines.append('- 事实口径：'+content['fact_caption'])
    for seg in record['segments']:
        v=seg['visual']
        lines += ['',f'## {seg["id"]}｜{v["title"]}','',f'![{seg["id"]}源参考]({seg["reference_image"]})',
                  f'- 时码：{seg["start_s"]}–{seg["end_s"]}秒。',f'- 布局：{v["layout"]}；标题角色：{v.get("role","chapter")}。',
                  f'- 动作图示：{" → ".join(x["kind"]+" / "+x["label"] for x in motion_steps(v))}。']
        for field in ['action','focus','text','music','risk']:
            lines.append(f'- {field}：{seg.get(field,"未声明")}')
        lines += [f'- 黄标：{"、".join(seg.get("highlights",[]))}。']
        for field in ['headline_lines','cta','disclaimer']:
            if field in v: lines.append(f'- {field}：{json.dumps(v[field],ensure_ascii=False)}')
    lines += ['', '## 来源与审核边界','', '- 真实源参考不等于成片；动作图示不证明真实路径；首尾预览是排版设计。',
              '- 本正文、方案板、图源与实际回读绑定后才能提交一次整包审核。机器检查不代替目视和用户接受。']
    return '\n'.join(lines)+'\n'


def load(record_path, floorplan):
    record_path=Path(record_path).resolve()
    record=validate(json.loads(record_path.read_text()))
    images=bind_images(record,record_path.parent,floorplan)
    return record,images
