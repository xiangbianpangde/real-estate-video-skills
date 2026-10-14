#!/usr/bin/env python3
"""Render a source-backed overview board HTML from a plan record (no video capture).
Export the HTML to PNG with a browser, inspect it, then bind both and the review.
"""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path


MOTION_KINDS = {"static", "pan", "travel", "orbit", "fov"}


def motion_svg(kind):
    if kind not in MOTION_KINDS:
        raise ValueError("Explicit supported motion kind required")
    shapes = {
        "static": '<rect x="12" y="18" width="60" height="44" rx="3"/><path d="M42 18v44M12 40h60"/>',
        "pan": '<path d="M18 58L44 18 70 58Z"/><path d="M8 25Q44 2 80 25M73 16l7 9-12 2"/>',
        "travel": '<rect x="10" y="35" width="25" height="20"/><path d="M35 40l12-6v22l-12-6M51 45h33m-11-9 11 9-11 9"/>',
        "orbit": '<circle cx="44" cy="42" r="9"/><path d="M15 44a30 23 0 1 1 8 16M11 53l12 7 3-13"/>',
        "fov": '<rect x="12" y="17" width="60" height="48"/><rect x="25" y="27" width="34" height="28" stroke-dasharray="4 3"/><path d="M16 21l9 8M68 61l-9-8"/>'
    }
    return '<svg class="motion-diagram" role="img" aria-label="镜头动作示意：'+kind+'" viewBox="0 0 92 82" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="#298675" stroke-width="3">'+shapes[kind]+'</g></svg>'


def build(record_path, output, floorplan):
    record_path = Path(record_path).resolve()
    record = json.loads(record_path.read_text())
    base = record_path.parent
    esc = lambda s: html.escape(str(s))

    def image(path):
        data = Path(path).read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('PNG source required')
        return 'data:image/png;base64,' + base64.b64encode(data).decode()

    assets = {a['path']: a for a in record['assets']}
    source_origin = 'synthetic_fixture' if record.get('fixture') is True else 'actual_source'
    floor = Path(floorplan).resolve()
    if not any((base / a['path']).resolve() == floor and a.get('origin') == source_origin
               and hashlib.sha256(floor.read_bytes()).hexdigest() == a.get('sha256')
               for a in record['assets']):
        raise ValueError('Floorplan source binding mismatch')
    cards = []
    names = record['scope']['coverage']
    for n, seg in enumerate(record['segments']):
        source = base / seg['reference_image']
        asset = assets[seg['reference_image']]
        if asset['origin'] != source_origin or hashlib.sha256(source.read_bytes()).hexdigest() != asset['sha256']:
            raise ValueError('Source image binding mismatch: ' + seg['id'])
        visual = seg.get('visual', {})
        if not visual.get('title') or visual.get('motion', {}).get('kind') not in MOTION_KINDS:
            raise ValueError('Explicit visual title and motion required: ' + seg['id'])
        title = visual['title']
        preview = f'<img class="source" alt="{esc(seg["id"])}真实源参考" src="{image(source)}">'
        caption = '合成测试素材 · 非真实房源' if record.get('fixture') else '真实源参考 · 不是最终成片'
        if visual.get('layout') == 'opening_composite':
            headlines = visual.get('headline_lines')
            if not isinstance(headlines, list) or len(headlines) != 2 or not all(isinstance(t, str) and t.strip() for t in headlines):
                raise ValueError('Opening composite requires two explicit headline lines')
            preview = f'''<div class="opening-preview" data-preview="opening_composite">
<img class="opening-background" src="{image(source)}" alt="真实室内背景">
<div class="opening-headlines"><b>{esc(headlines[0])}</b><strong>{esc(headlines[1])}</strong></div>
<div class="opening-floorplan"><img src="{image(floor)}" alt="真实户型图浮层"></div></div>'''
            caption = '首镜布局测试 · 虚构素材，非房源成片' if record.get('fixture') else '首镜布局预览 · 源图合成设计，非已录成片'
        elif visual.get('layout') != 'source_reference':
            raise ValueError('Explicit supported visual layout required: ' + seg['id'])
        motion = visual['motion']
        if not motion.get('label'):
            raise ValueError('Motion diagram explanation required')
        duration = seg['end_s'] - seg['start_s']
        cards.append(f'''<article class="card" data-segment="{esc(seg['id'])}">
<div class="bar">{esc(seg['id'])} · {duration:.1f}秒</div>
<div class="content"><div class="eyebrow">{seg['start_s']:.2f}–{seg['end_s']:.2f}秒</div>
<h2>{esc(title)}</h2>{preview}
<div class="caption">{caption}</div>
<div class="tag">官方全景连续导航 · {esc(seg['id'])}</div>
<div class="method">{motion_svg(motion["kind"])}<b>{esc(motion["label"])}</b><p>{esc(seg['action'])}</p></div>
<div class="field"><b>观看重点</b><p>{esc(seg['focus'])}</p></div>
<div class="field"><b>口播 / 完整逐字字幕</b><p>{esc(seg['text'])}</p></div>
<div class="caption">黄标：{esc('、'.join(seg['highlights']))}</div>
<div class="risk"><b>画面限制</b><p>{esc(seg['risk'])}</p></div>
</div></article>''')
    scope = record['scope']
    board_content = record.get('board_content', {})
    dimensions = scope.get('render_config', {})
    title = record.get('storyboard_title', '房源介绍 · 完整拍前图文方案')
    doc = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{esc(title)}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f7faf9;color:#193c47;font:22px/1.55 "PingFang SC","Microsoft YaHei",sans-serif}}
#board{{width:{int(record.get('board_width', 2880))}px;padding:60px}}h1{{font-size:58px;margin:12px 0}}h2{{font-size:32px;margin:8px 0 18px}}h3{{font-size:34px;margin:0 0 20px}}
p{{margin:8px 0;overflow-wrap:anywhere}}.eyebrow{{color:#527984;font-weight:600;letter-spacing:1px}}.lead{{font-size:28px;color:#527984}}
.notice{{padding:24px 30px;background:#e4f2ee;border-left:8px solid #298675;margin:24px 0}}.disclosure{{color:#9a7339;margin:20px 0}}
.cards{{display:grid;grid-template-columns:repeat({len(cards)},1fr);gap:12px;align-items:stretch}}
.card{{min-width:0}}.bar{{background:#254f5e;color:white;text-align:center;padding:16px;border-radius:8px;margin-bottom:16px;font-weight:bold}}
.content{{border:2px solid #d5e5e8;border-top:6px solid #298675;border-radius:18px;background:white;padding:20px;height:calc(100% - 80px)}}
.source{{width:100%;height:310px;object-fit:contain;background:#f3f6f5;border-radius:8px}}.opening-preview{{position:relative;height:420px;aspect-ratio:9/16;margin:auto;max-width:100%;overflow:hidden;background:#eef3f1}}.opening-background{{width:100%;height:100%;object-fit:cover}}.opening-headlines{{position:absolute;top:26%;left:4%;width:92%;text-align:center;line-height:1.4;text-shadow:1px 1px 1px #111,-1px -1px 1px #111}}.opening-headlines b{{display:block;color:#ffdf50;font-size:21px}}.opening-headlines strong{{display:block;color:white;font-size:17px}}.opening-floorplan{{position:absolute;top:45%;left:5%;width:90%;height:40%;background:rgba(255,255,255,.75);border-radius:8px;padding:7px}}.opening-floorplan img{{width:100%;height:100%;object-fit:contain}}.caption{{font-size:19px;color:#5c7c88;margin:12px 0}}
.tag{{display:inline-block;background:#e4f2ee;color:#287f71;border:1px solid #b5dcd2;padding:6px 10px;margin:10px 0;font-size:19px}}
.motion-diagram{{width:88px;height:78px;float:left;margin-right:12px}}.method{{display:flow-root;background:#edf4f3;border-radius:8px;padding:12px}}.field{{border-bottom:1px solid #e0ebed;padding:14px 0}}.risk{{color:#805f30;background:#faf6ed;padding:12px;margin-top:16px;border-radius:8px;font-size:20px}}
.lower{{display:grid;grid-template-columns:760px 1fr;gap:24px;margin-top:30px}}.panel{{background:white;border:2px solid #d5e5e8;border-radius:18px;padding:28px}}
.floorplan{{width:100%;height:630px;object-fit:contain}}.note{{background:#eef4f5;padding:20px 24px;margin:16px 0;border-radius:10px}}
.footer{{background:#254f5e;color:white;border-radius:16px;padding:30px 36px;margin-top:30px;font-size:26px}}.small{{font-size:20px;color:#5c7c88;margin-top:16px}}
</style><main id="board">
<header><div class="eyebrow">{esc(scope['source_namespace'])} · {esc(record['plan']['version'])} · 整包待审核</div>
<h1>{esc(title)}</h1><div class="lead">{' → '.join(esc(s) for s in names)}</div>
<div class="notice"><b>先看整片方案，再一次确认：</b>约{scope['duration_s']:.1f}秒，{esc(dimensions.get('width', '按合同'))}×{esc(dimensions.get('height', '按合同'))}画幅；一次正式连续采集＋首尾、配音、逐字字幕、BGM与检查。</div>
<p class="disclosure">{esc(board_content.get('source_notice', '真实图片仅作取景参考。章节是连续镜头的叙事段，不是剪辑切点；已知过渡重影和局部遮挡原样披露。'))}</p></header>
<section class="cards">{''.join(cards)}</section>
<section class="lower"><div class="panel"><h3>原户型：整片布局锚点</h3><img class="floorplan" src="{image(floorplan)}" alt="当前房源真实户型图"><p>{esc(board_content.get('fact_caption', '事实口径见同版正文及原始来源'))}</p><p class="small">来源为本房源归档资料；不将图示作为现实行走或空间尺度证明。</p></div>
<div class="panel"><h3>本版修复了什么，哪些仍待审核</h3>
<div class="note"><b>变化一：恢复整体方案板</b><p>章节横向对照；图、时间、动作、口播、黄标和限制同卡呈现。附文保留全部源与范围绑定。</p></div>
<div class="note"><b>变化二：修正口播与字幕</b><p>{esc(board_content.get('text_changes', '字幕覆盖与交付方式按同版正文合同执行；标题不替代口播字幕。'))}</p></div>
<div class="note"><b>变化三：首尾与声音</b><p>{esc(scope['opening'])}。{esc(scope['ending'])}。</p><p>{esc(board_content.get('audio_caption', scope['bgm']))}</p></div>
<div class="note"><b>需随整包审核的限制</b><p>{esc(board_content.get('limitations', '逐章节核对卡片限制；接受范围以当前用户已声明基准为准。'))}</p></div>
<div class="note"><b>本轮修的是格式，没有新采集</b><p>复用原路线与预检；真实素材及旧版本保留。完成制作后再按S-ID审核成片，最终接受与发布分开。</p></div>
</div></section>
<footer class="footer"><b>确认顺序：一次整包审核 → 一次正式采集及包内后期 → 按章节审成片</b><p>这张图展示拍前方案，不表示已批准或已完成视频。仅内部审看，不含发布、付费服务和第二次采集。</p></footer>
<p class="small">成像方法：{esc(scope['render_method'])} · 源范围：{esc(scope['validation_scope'])} · 图文版本：{esc(record['plan']['version'])}</p>
</main></html>'''
    with Path(output).open('x', encoding='utf-8') as f:
        f.write(doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--floorplan', required=True)
    args = parser.parse_args()
    build(args.record, args.output, args.floorplan)
