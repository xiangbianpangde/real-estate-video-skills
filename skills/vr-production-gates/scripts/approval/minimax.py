#!/usr/bin/env python3
"""MCode confirmation-card preparation and content-only production checks.

No Hook, MCP server, persisted approval, or user identity authentication. A card
payload is not a submitted card; the Agent must call the native ask_user tool.
"""
import argparse
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot import snapshot
from check_shooting_plan import check


def boundary():
    return {'gate_type': 'minimax_code_native_confirmation_flow',
            'hard_tool_interception': False, 'user_approval_verified': False,
            'production_authorized': False}


def review(record_path):
    """Check complete content and prepare, but do not submit, a native card."""
    current = snapshot(record_path)
    record = json.loads(Path(current['record_path']).read_text(encoding='utf-8'))
    scope = record['scope']
    version = current['version']
    source = str(current.get('source_namespace') or '本房源')
    dimensions = scope.get('render_config', {})
    output = str((Path(current['record_path']).parent / scope['output_dir']).resolve())
    question = (
        f"是否批准房源 {source} 的 {version} 完整脚本并开始本地制作？"
        f"完整脚本：{current['document_path']}。"
        f"范围：{scope['duration_s']}秒，{dimensions.get('width', '未填')}×{dimensions.get('height', '未填')}，"
        f"空间：{'、'.join(scope.get('coverage', []))}；动作：{'、'.join(current['authorized_actions'])}；"
        f"拍法与连续性：{json.dumps(scope.get('editing_policy', {}), ensure_ascii=False)}；"
        f"声音：{scope.get('voiceover', '按完整脚本')}；配乐：{scope.get('bgm', '按完整脚本')}；"
        f"不授权：{'、'.join(scope.get('not_authorized', [])) or '脚本外操作'}。"
        f"输出：{output}，保留原件，不覆盖已批准版本。"
        "此确认不授权公开发布或新增收费；未批准保持暂停。"
    )
    card = {
        'requiresExplicitResponse': True,
        'title': f'审核视频脚本 {version}',
        'steps': [{
            'id': 'script_approval', 'header': '本版脚本审核',
            'question': question,
            'options': [
                {'id': 'approve_current_script', 'label': f'批准 {version} 本版脚本，按所列范围开始制作'},
                {'id': 'leave_unchanged', 'label': '暂不批准，保持暂停，不开始制作'},
            ],
            'selectionMode': 'single',
        }],
    }
    return {**current, **boundary(), 'passed': True,
            'state': 'USER_CONFIRMATION_REQUIRED', 'card_submitted': False,
            'link': f"[视频脚本 {version}]({Path(current['document_path']).as_uri()})",
            'ask_user': card,
            'next_action': '先向用户交付完整链接和文件，再单独调用原生 ask_user；waiting_for_user 后立即停下。此输出不代表用户批准。'}


def technical_check(record_path, fingerprint, phase, claim=False):
    """Check unchanged reviewed content, never assert a host/user confirmation."""
    if not isinstance(fingerprint, str) or not re.fullmatch(r'[0-9a-f]{64}', fingerprint):
        raise ValueError('Expected the original review fingerprint, not an approval value')
    if phase not in ('capture', 'post') or type(claim) is not bool or (claim and phase != 'capture'):
        raise ValueError('Expected capture/post; claim is capture-only')
    current = snapshot(record_path)
    if current['fingerprint'] != fingerprint:
        raise ValueError('Reviewed content snapshot changed; resubmit and ask the user again')
    result = check(Path(record_path).resolve(), phase, claim, content_snapshot=current)
    return {**result, **boundary(), 'technical_checks_only': True,
            'authorization_source': 'not_authenticated_by_this_cli',
            'confirmation_required_in_current_conversation': True,
            'fingerprint': current['fingerprint']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    prepare = actions.add_parser('review', help='Check complete script and prepare native ask_user arguments')
    prepare.add_argument('--record', required=True, type=Path)
    technical = actions.add_parser('check', help='Technical checks only; not user authorization')
    technical.add_argument('--record', required=True, type=Path)
    technical.add_argument('--fingerprint', required=True)
    technical.add_argument('--phase', required=True, choices=('capture', 'post'))
    technical.add_argument('--claim', action='store_true', help='Reserve capture output; call only after actual user approval')
    args = parser.parse_args(argv)
    if args.action == 'check' and args.claim and args.phase != 'capture':
        parser.error('--claim requires --phase capture')
    try:
        result = review(args.record) if args.action == 'review' else technical_check(
            args.record, args.fingerprint, args.phase, args.claim)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {**boundary(), 'passed': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result['passed'] else 2


if __name__ == '__main__':
    sys.exit(main())
