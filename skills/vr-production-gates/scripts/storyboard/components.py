"""Reusable image roles, motion diagrams, chapter cards and risk labels."""
import base64
import html
from .model import MOTION_KINDS, motion_steps

esc = lambda value: html.escape(str(value))

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


def image(data):
    return 'data:image/png;base64,' + base64.b64encode(data).decode()


def preview(seg, images, floorplan, fixture=False):
    v = seg['visual']
    src = image(images[seg['reference_image']])
    alt = '虚构素材' if fixture else '真实源参考'
    layout = v['layout']
    if layout == 'source_reference':
        return f'<div class="preview"><img class="source" src="{src}" alt="{alt}"></div><p class="caption">{alt} · 非最终成片</p>'
    background = f'<img class="opening-background" src="{src}" alt="{alt}背景">'
    if layout == 'opening_composite':
        lines = v['headline_lines']
        headlines = ''.join(f'<{"b" if i == 0 else "strong"}>{esc(line)}</{"b" if i == 0 else "strong"}>' for i, line in enumerate(lines))
        layers = f'<div class="opening-headlines">{headlines}</div><div class="opening-floorplan"><img src="{image(images[str(floorplan)])}" alt="户型图浮层"></div>'
    else:
        layers = f'<div class="ending-cta">{esc(v.get("cta", ""))}</div><div class="ending-disclaimer">{esc(v.get("disclaimer", ""))}</div>'
    return f'<div class="preview"><div class="composite" data-preview="{layout}">{background}{layers}</div></div><p class="caption">{"虚构测试" if fixture else "源图合成"}布局预览 · 非已录成片</p>'


def motion_component(visual):
    return '<div class="motions">' + ''.join(f'<div class="motion">{motion_svg(s["kind"])}<b>{esc(s["label"])}</b></div>' for s in motion_steps(visual)) + '</div>'


def risk_tag(level, text):
    label = {'limitation':'已披露限制', 'pending':'待确认', 'info':'说明'}[level]
    return f'<div class="risk {level}"><b>{label}</b><p>{esc(text)}</p></div>'


def chapter_card(seg, images, floorplan, fixture=False):
    v = seg['visual']
    return f'''<article class="card" data-segment="{esc(seg['id'])}"><div class="bar">{esc(seg['id'])} · {seg['end_s']-seg['start_s']:.1f}秒</div>
<div class="content"><div class="eyebrow">{seg['start_s']:.2f}–{seg['end_s']:.2f}秒</div><h2>{esc(v['title'])}</h2>
{preview(seg, images, floorplan, fixture)}{motion_component(v)}
<div class="field"><b>镜头动作</b><p>{esc(seg['action'])}</p></div>
<div class="field"><b>观看重点</b><p>{esc(seg['focus'])}</p></div>
<div class="field"><b>口播</b><p>{esc(seg.get('text', '') or '无旁白')}</p></div>
<p class="caption">黄标：{esc('、'.join(seg.get('highlights', []))) or '无'}</p>
{risk_tag(v.get('risk_level','limitation'),seg['risk']) if seg.get('risk') else ''}</div></article>'''
