#!/usr/bin/env python3
"""Prepare local opening BGM excerpts and a listening index. Python 3.10+, FFmpeg.
Preserves input files; creates a new output folder. No downloads or generation.
"""
import argparse
import html
import json
import math
from pathlib import Path
import re
import subprocess
from urllib.parse import quote
from media import sha, write_json

AUDIO_EXTENSIONS = {'.mp3', '.ogg', '.flac', '.wav', '.m4a', '.aac', '.opus'}


def run(argv):
    result = subprocess.run(argv, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result


def measured(log):
    matches = re.findall(r'\{\s*"input_i".*?\}', log, re.S)
    if not matches:
        raise ValueError('No loudness measurement; inspect source decoding')
    values = json.loads(matches[-1])
    if not all(math.isfinite(float(values[k])) for k in ['input_i', 'input_tp', 'input_lra', 'input_thresh']):
        raise ValueError('No finite audio loudness; source may be silent')
    return values


def prepare(source_dir, output_dir, seconds=35):
    source_dir = Path(source_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('Positive finite excerpt length required')
    files = sorted(p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS)
    if not files:
        raise ValueError('No supported audio in source directory')
    if output_dir == source_dir or any(p.is_relative_to(output_dir) for p in files):
        raise ValueError('Output must not contain or replace an input file')
    output_dir.mkdir(parents=True, exist_ok=False)
    audio_dir = output_dir / '音频'
    audio_dir.mkdir()
    entries = []
    receipt = {'schema': 'bgm-opening-library/v1', 'source_dir': str(source_dir), 'requested_seconds': seconds,
               'purpose': 'opening excerpts for editing; adjust music level/ducking to final narration',
               'human_listening_verified': False, 'entries': entries}
    for n, src in enumerate(files, 1):
        before = sha(src)
        inspection = run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_streams', '-show_format', '-of', 'json', str(src)])
        info = json.loads(inspection.stdout)
        if not info['streams']:
            raise ValueError('No audio stream: ' + src.name)
        length = min(seconds, float(info['format']['duration']))
        if length <= 0:
            raise ValueError('Empty audio: ' + src.name)
        norm = 'loudnorm=I=-18:TP=-2:LRA=11'
        analysis = run(['ffmpeg', '-hide_banner', '-i', str(src), '-map', '0:a:0', '-vn', '-t', str(length),
                        '-af', norm + ':print_format=json', '-f', 'null', '-'])
        levels = measured(analysis.stderr)
        normalized = norm + ''.join(':' + a + '=' + levels[b] for a, b in [
            ('measured_I', 'input_i'), ('measured_TP', 'input_tp'), ('measured_LRA', 'input_lra'),
            ('measured_thresh', 'input_thresh'), ('offset', 'target_offset')]) + ':linear=true'
        fade = min(.8, length / 4)
        filters = normalized + f',afade=t=in:d=0.02,afade=t=out:st={length-fade}:d={fade}'
        stem = f'{n:02d}_{src.stem}_开头{length:g}秒'
        wav, preview = audio_dir / (stem + '.wav'), audio_dir / (stem + '.m4a')
        encode = ['ffmpeg', '-hide_banner', '-v', 'error', '-n', '-i', str(src), '-map', '0:a:0', '-vn',
                  '-t', str(length), '-af', filters, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', str(wav)]
        run(encode)
        run(['ffmpeg', '-v', 'error', '-n', '-i', str(wav), '-map', '0:a:0', '-c:a', 'aac', '-b:a', '256k',
             '-movflags', '+faststart', str(preview)])
        qc = {}
        for name, path in [('wav', wav), ('preview', preview)]:
            checked = run(['ffmpeg', '-hide_banner', '-i', str(path), '-map', '0:a:0', '-af', norm + ':print_format=json', '-f', 'null', '-'])
            audio_levels = measured(checked.stderr)
            if float(audio_levels['input_tp']) >= 0:
                raise ValueError('Encoded audio clipping: ' + path.name)
            duration = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)]).stdout)
            if abs(duration - length) > .08:
                raise ValueError('Excerpt duration mismatch: ' + path.name)
            qc[name] = {'path': str(path.relative_to(output_dir)), 'sha256': sha(path), 'duration_s': duration,
                        'integrated_lufs': float(audio_levels['input_i']), 'true_peak_dbfs': float(audio_levels['input_tp']), 'full_decode_passed': True}
        assert sha(src) == before, 'Source changed during processing'
        entry = {'source': str(src), 'source_sha256': before, 'source_duration_s': float(info['format']['duration']),
                 'source_tags': info['format'].get('tags', {}), 'source_probe_diagnostics': inspection.stderr,
                 'excerpt_source_s': [0, length], 'source_unchanged': True, 'target_lufs': -18, 'target_true_peak_dbfs': -2,
                 'fade_in_s': .02, 'fade_out_s': fade, 'filter': filters, 'wav_command': encode, 'outputs': qc,
                 'version_identity': 'filename and embedded tags retained; no inferred artist/version equivalence'}
        entries.append(entry)
        (output_dir / '清单.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
        print('Prepared:', src.name, flush=True)
    rows = []
    for e in entries:
        w, a = e['outputs']['wav'], e['outputs']['preview']
        rows.append('<section><h2>' + html.escape(Path(e['source']).stem) + '</h2><p>原曲0–' +
                    f'{e["excerpt_source_s"][1]:g}秒 · 48kHz立体声 · WAV 24-bit · {w["integrated_lufs"]:.1f} LUFS</p>' +
                    '<audio controls preload="none" src="' + quote(a['path']) + '"></audio><p><a href="' +
                    quote(w['path']) + '">剪辑用 WAV</a> · <a href="' + quote(a['path']) + '">试听/轻量 M4A</a></p></section>')
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BGM开头素材库</title><style>body{max-width:1000px;margin:35px auto;padding:0 20px;background:#f3f7f6;color:#193f49;font:17px/1.7 system-ui}section{background:white;padding:20px;margin:20px 0;border-radius:12px}audio{width:100%}h2{font-size:21px}a{color:#176d83}</style><h1>BGM开头素材库</h1><p>保留原曲开头；统一响度并作20ms入点与0.8秒结尾淡化。WAV用于剪辑，M4A用于试听。截短时需重做结尾淡出；与旁白混合时再降低音乐并平滑让位，本库响度不是成片混音音量。</p><p>曲名及版本沿用实际文件，不把不同DJ版本当作同一来源。技术检查通过不表示人工试听已通过。</p>' + ''.join(rows) + '</html>'
    (output_dir / '试听索引.html').write_text(page)
    (output_dir / '使用说明.md').write_text('# BGM开头素材库\n\n原曲不动；来源、区间、参数、文件SHA、实际时长及响度见清单.json。\n\n- 音频目录：WAV为48kHz/24-bit立体声剪辑母版，M4A为AAC试听版。\n- 默认取原曲0–35秒；短于35秒的来源只取实际全长，不循环或补静音。\n- 入点20ms、末尾0.8秒淡化，响度目标−18 LUFS、真峰目标−2 dBFS；实际值见清单。\n- 25–35秒房产视频可直接导入母版，按成片长度裁短并重新淡出；旁白处另作音量让位，不能将素材库响度当作最终混音音量。\n- 浏览器打开试听索引.html；来源含人声时需核听是否与旁白冲突。本工具不鉴定授权或曲目版本，不更改原文件。\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--seconds', type=float, default=35)
    args = parser.parse_args()
    prepare(args.source_dir, args.out, args.seconds)
