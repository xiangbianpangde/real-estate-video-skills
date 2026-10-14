#!/usr/bin/env python3
"""Compatibility entry: build only the board HTML; never captures video."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from storyboard.components import motion_svg
from storyboard.model import MOTION_KINDS
from storyboard.render import load, render_html


def build(record_path, output, floorplan):
    record, images = load(record_path, floorplan)
    html = render_html(record, images, floorplan)
    with Path(output).open('x',encoding='utf-8') as f: f.write(html)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--floorplan',required=True)
    a=p.parse_args()
    build(a.record,a.output,a.floorplan)
