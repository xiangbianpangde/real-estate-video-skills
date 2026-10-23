#!/usr/bin/env python3
"""Python 3.10+, stdlib only. Verify a versioned illustrated plan before capture.

Read-only by default. --phase capture --claim atomically reserves a new output
folder. The reservation prevents collisions, not another authorized attempt.
This is an entry-point gate, not a sandbox, identity verifier or visual-QC tool.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
HASH = re.compile(r"[0-9a-f]{64}\Z")
CORE = ("plan", "assets", "segments", "scope", "exploration")
ACTIONS = {"capture", "opening", "ending", "subtitles", "bgm", "encode", "qc"}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bundle_digest(record):
    core = {key: record.get(key) for key in CORE}
    if record.get('presentation', {}).get('mode') == 'linked_document':
        # Pin the reviewable content, not transient diagnosis counters, render
        # receipts or output folders. User-specified limits remain in the pin.
        operational = {'output_dir', 'render_validation', 'render_config', 'continuous_edit_evidence'}
        core['scope'] = {k: v for k, v in record.get('scope', {}).items() if k not in operational}
        core['assets'] = [a for a in record.get('assets', []) if a.get('role') not in
                          {'precheck', 'precheck_report', 'continuous_edit_report'}]
        core['exploration'] = {'limits': record.get('exploration', {}).get('limits', {})}
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def text(event):
    content = event.get("message", {}).get("content", [])
    if isinstance(content, str):
        return content
    return "\n".join(item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text")


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check(record_path, phase, claim):
    errors = []
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    base = record_path.parent.resolve()
    if (record.get("design_system") is not None
            or any(record.get("scope", {}).get(key) is not None
                   for key in ("shot_constraints", "editing_policy", "showcase"))):
        from storyboard.model import validate
        validate(record)
        if phase in ("capture", "post") and record.get("scope", {}).get("shot_constraints") is not None:
            if any(seg.get("framing_status") == "pending" for seg in record.get("segments", [])):
                errors.append("shot_framing_pending")

    def local(name, inside=False):
        if not isinstance(name, str) or not name or Path(name).is_absolute() or "://" in name:
            raise ValueError("expected a relative local path")
        path = (base / name).resolve()
        if inside and not path.is_relative_to(base):
            raise ValueError("output must stay within the plan directory")
        return path

    def asset_ok(name, expected, label):
        path = local(name)
        if not path.is_file():
            errors.append("missing_asset:" + label)
        elif not isinstance(expected, str) or not HASH.fullmatch(expected) or digest(path) != expected:
            errors.append("asset_sha_mismatch:" + label)
        return path

    def visual_acceptance(scope, assets):
        policy = scope.get("visual_acceptance")
        if policy is None:
            return
        if not isinstance(policy, dict):
            errors.append("invalid_visual_acceptance")
            return
        paths = {}
        for key, role in (("reference", "acceptance_reference"), ("decision", "acceptance_decision")):
            entry = policy.get(key)
            if not isinstance(entry, dict) or not entry.get("path"):
                errors.append("missing_visual_acceptance:" + key)
                continue
            bound = assets.get(entry["path"], {})
            if bound.get("role") != role or bound.get("sha256") != entry.get("sha256"):
                errors.append("unbound_visual_acceptance:" + key)
            paths[key] = asset_ok(entry["path"], entry.get("sha256"), "visual_acceptance_" + key)
        decision_path = paths.get("decision")
        if decision_path is None or not decision_path.is_file():
            return
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if not isinstance(decision, dict):
            errors.append("invalid_visual_acceptance_decision")
            return
        event = decision.get("user_event")
        criteria = decision.get("criteria")
        if (decision.get("schema") != "vr-visual-acceptance/v1" or not isinstance(event, dict)
                or not event.get("id") or event.get("message", {}).get("role") != "user"
                or not isinstance(criteria, str) or not criteria.strip() or criteria != text(event).strip()):
            errors.append("invalid_visual_acceptance_decision")
        reference = policy.get("reference", {})
        if not isinstance(reference, dict) or decision.get("reference_sha256") != reference.get("sha256"):
            errors.append("visual_reference_decision_mismatch")
        # Keep provenance internally; users need the criteria and limitations,
        # not literal source paths, hashes or a duplicate verbatim transcript.

    def render_precheck(scope, assets):
        validation = scope.get("render_validation")
        if not isinstance(validation, dict) or not validation.get("path"):
            errors.append("missing_render_validation")
            return
        name, expected = validation.get("path"), validation.get("sha256")
        report_asset = assets.get(name, {})
        if report_asset.get("role") != "precheck_report" or report_asset.get("sha256") != expected:
            errors.append("unbound_render_precheck")
        path = asset_ok(name, expected, "render_precheck")
        if not path.is_file():
            return
        report = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("schema") != "vr-render-precheck/v1":
            errors.append("invalid_render_precheck")
            return
        for key in ("source_namespace", "capture_medium", "validation_scope", "render_method",
                    "render_config", "continuity_class", "route", "coverage"):
            if report.get(key) != scope.get(key):
                errors.append("render_precheck_identity_mismatch:" + key)
        presentation = record.get("presentation", {})
        bindings = presentation.get("precheck_bindings", {}) if presentation.get("mode") == "rendered_document" else {}
        sources = {name: asset.get("sha256") for name, asset in assets.items() if asset.get("role") == "source"}
        source_map = bindings.get("sources")
        if source_map is not None:
            expected_sources = report.get("source_sha256", {})
            if (not expected_sources or set(source_map) != set(expected_sources)
                    or any(sources.get(source_map[n]) != h for n, h in expected_sources.items())):
                errors.append("render_precheck_source_mismatch")
        elif report.get("source_sha256") != sources:
            errors.append("render_precheck_source_mismatch")
        if report.get("evidence_kind") != "continuous_media" or report.get("complete_interval_reviewed") is not True:
            errors.append("render_precheck_not_continuous")
        checks = report.get("checks", {})
        for key in ("control", "playback") + (("state_restore",) if "state_restore" in checks else ()):
            if not isinstance(checks, dict) or checks.get(key) != "PASS":
                errors.append("render_precheck_not_passed:" + key)
        visual = checks.get("visual") if isinstance(checks, dict) else None
        if visual not in ("PASS", "PASS_WITH_LIMITATIONS"):
            errors.append("render_precheck_not_passed:visual")
        policy = scope.get("visual_acceptance")
        if policy is not None or visual == "PASS_WITH_LIMITATIONS":
            if policy is not None and report.get("visual_acceptance") != policy:
                errors.append("render_precheck_identity_mismatch:visual_acceptance")
            review = report.get("visual_review")
            if not isinstance(review, dict) or review.get("within_user_criteria") is not True:
                errors.append("visual_acceptance_not_matched")
            limitations = review.get("limitations") if isinstance(review, dict) else None
            if (not isinstance(limitations, list)
                    or any(not isinstance(item, str) or not item.strip() for item in limitations)
                    or (visual == "PASS_WITH_LIMITATIONS" and not limitations)):
                errors.append("missing_visual_limitations")
            elif any(item not in body for item in limitations):
                alignment = bindings.get("limitations", [])
                segments_by_id = {s.get("id"): s for s in record.get("segments", [])}
                if (len(alignment) != len(limitations)
                        or any(a.get("report_text") != item
                               or a.get("script_risk") != segments_by_id.get(a.get("segment_id"), {}).get("risk")
                               or not a.get("script_risk") or a["script_risk"] not in body
                               for a, item in zip(alignment, limitations))):
                    errors.append("visual_limitations_not_in_plan")
        evidence = report.get("evidence", {})
        for key in ("media", "review", "telemetry", "restore"):
            entry = evidence.get(key) if isinstance(evidence, dict) else None
            if key in ("telemetry", "restore") and entry is None:
                continue
            if not isinstance(entry, dict) or not entry.get("path"):
                errors.append("missing_render_precheck_evidence:" + key)
                continue
            actual_name = bindings.get("evidence", {}).get(entry["path"], entry["path"])
            bound = assets.get(actual_name, {})
            if bound.get("role") != "precheck" or bound.get("sha256") != entry.get("sha256"):
                errors.append("unbound_render_precheck_evidence:" + key)
            asset_ok(actual_name, entry.get("sha256"), "render_precheck_" + key)

    if record.get("schema") not in ("vr-production-plan/v2", "vr-production-plan/v3"):
        errors.append("unsupported_schema")
    plan = record.get("plan", {})
    plan_path = local(plan.get("path"))
    body = plan_path.read_text(encoding="utf-8")
    plan_sha = digest(plan_path)
    if plan_sha != plan.get("sha256"):
        errors.append("plan_sha_mismatch")
    if not plan.get("version") or plan["version"] not in body:
        errors.append("missing_plan_version")
    bundle_sha = bundle_digest(record)
    images = {url for alt, url in IMAGE.findall(body) if alt.strip()}
    assets = {}
    overview = []
    for a in record.get("assets", []):
        name = a["path"]
        if name in assets:
            errors.append("duplicate_asset:" + name)
        assets[name] = a
        path = asset_ok(name, a.get("sha256"), name)
        if a.get("role") in ("reference", "overview"):
            if path.suffix.lower() != ".png" or (path.is_file() and path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n"):
                errors.append("invalid_png:" + name)
            if a.get("role") == "overview":
                overview.append(name)
    image_paths = {(plan_path.parent / url).resolve() for url in images}
    if not overview or not all(local(p).resolve() in image_paths for p in overview):
        errors.append("missing_embedded_overview")
    for image in images:
        # Markdown URLs resolve from the Markdown, not from the record.
        path = (plan_path.parent / image).resolve()
        if not any(local(a) == path for a in assets):
            errors.append("unbound_embedded_image:" + image)
    # New illustrated boards bind actual render/review evidence. v2 stays historical.
    if record.get("schema") == "vr-production-plan/v3":
        layout = record.get("scope", {}).get("storyboard_layout")
        if not isinstance(layout, dict) or layout.get("kind") != "overview_board":
            errors.append("missing_storyboard_layout")
        else:
            bound = {}
            for key, role in (("board", "overview"), ("source", "storyboard_source"), ("review", "layout_review")):
                name = layout.get(key)
                entry = assets.get(name, {})
                if not name or entry.get("role") != role:
                    errors.append("unbound_storyboard_layout:" + key)
                else:
                    bound[key] = entry
            if len(bound) == 3:
                evidence = json.loads(local(layout["review"]).read_text())
                if not isinstance(evidence, dict) or evidence.get("schema") != "vr-storyboard-layout-review/v1":
                    errors.append("invalid_layout_review")
                else:
                    if (evidence.get("board_sha256") != bound["board"].get("sha256")
                            or evidence.get("source_sha256") != bound["source"].get("sha256")):
                        errors.append("layout_review_sha_mismatch")
                    expected_ids = [seg.get("id") for seg in record.get("segments", [])]
                    if evidence.get("segment_ids") != expected_ids:
                        errors.append("layout_review_segments_mismatch")
                    for key in ("all_images_loaded", "no_overflow", "reference_structure_matches", "motion_diagrams_reviewed", "opening_composite_reviewed"):
                        if evidence.get(key) is not True:
                            errors.append("layout_review_not_passed:" + key)
                    if not isinstance(evidence.get("review_basis"), str) or not evidence["review_basis"].strip():
                        errors.append("missing_layout_review_basis")
    if record.get('design_system',{}).get('version') == '1.1.0':
        route_layout=record.get('scope',{}).get('review_route_layout')
        if not isinstance(route_layout,dict):
            errors.append('missing_complete_route_layout')
        else:
            route_bound={}
            for key,role in [('board','review_route'),('source','review_route_source')]:
                name=route_layout.get(key);entry=assets.get(name,{})
                if not name or entry.get('role')!=role:
                    errors.append('unbound_complete_route_'+key)
                else:
                    asset_ok(name,entry.get('sha256'),'complete_route_'+key);route_bound[key]=name
            if 'board' in route_bound:
                route_image=local(route_bound['board'])
                if route_image not in {(plan_path.parent/name).resolve() for name in images} or '## 户型运镜路线图' not in body:
                    errors.append('complete_route_board_not_in_plan')
            if 'source' in route_bound:
                from html.parser import HTMLParser
                class RouteRows(HTMLParser):
                    def __init__(self):super().__init__();self.rows=[];self.complete=False
                    def handle_starttag(self,tag,attrs):
                        item=dict(attrs)
                        if item.get('data-complete-route-board')=='true':self.complete=True
                        if 'data-route-chapter' in item:self.rows.append(item)
                source=RouteRows();source.feed(local(route_bound['source']).read_text())
                expected=record['review_route']['chapters']
                def row_matches(row,chapter):
                    try:
                        return (row.get('data-route-chapter')==chapter['id']
                                and float(row.get('data-start','nan'))==chapter['start_s']
                                and float(row.get('data-end','nan'))==chapter['end_s']
                                and row.get('data-panos')=='→'.join(str(n) for n in chapter['pano_indices']))
                    except ValueError:return False
                if not source.complete or len(source.rows)!=len(expected) or not all(row_matches(a,b) for a,b in zip(source.rows,expected)):
                    errors.append('complete_route_source_mismatch')
    segments = record.get("segments", [])
    ids = set()
    previous = 0.0
    for segment in segments:
        sid = segment.get("id", "")
        if not re.fullmatch(r"S[0-9]{2,}", sid) or sid in ids:
            errors.append("invalid_segment_id:" + sid)
        ids.add(sid)
        card = re.search(r"^## " + re.escape(sid) + r"\b[^\n]*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
        if not card:
            errors.append("segment_not_in_plan:" + sid)
        card_body = card.group(1) if card else ""
        reference = segment.get("reference_image")
        a = assets.get(reference, {})
        if a.get("role") != "reference" or a.get("origin") != "actual_source":
            errors.append("non_source_reference:" + sid)
        if not reference or local(reference) not in {(plan_path.parent / p).resolve() for p in images}:
            errors.append("missing_embedded_reference:" + sid)
        fields = ("action", "focus")
        if any(not isinstance(segment.get(k), str) or not segment[k].strip() for k in fields) or not isinstance(segment.get("highlights"), list):
            errors.append("incomplete_card:" + sid)
        elif any(segment[k] not in card_body for k in fields):
            errors.append("card_content_not_in_plan:" + sid)
        # Bind all current reviewable words, not only action/focus. Otherwise a
        # new narration/risk can be approved against an older visible script.
        if any(not isinstance(segment.get(k, ""), str) or segment.get(k, "") not in card_body
               for k in ("text", "risk", "music")):
            errors.append("card_content_not_in_plan:" + sid)
        if any(not isinstance(h, str) or not h or h not in card_body for h in segment.get("highlights", [])):
            errors.append("highlights_not_in_plan:" + sid)
        start, end = segment.get("start_s"), segment.get("end_s")
        if not number(start) or not number(end) or abs(start - previous) > 0.001 or end <= start:
            errors.append("invalid_segment_timeline:" + sid)
        elif number(end):
            previous = end
    if not segments:
        errors.append("missing_opening_or_ending_card")
    if not any(a.get("role") == "source" for a in assets.values()):
        errors.append("missing_source_binding")
    scope = record.get("scope", {})
    execution_mode = scope.get("execution_mode", "capture_and_post")
    if execution_mode not in ("capture_and_post", "post_only"):
        errors.append("invalid_execution_mode")
    post_only = execution_mode == "post_only"
    authorized = scope.get("authorized_actions", [])
    required = scope.get("requested_actions", ["capture"] if phase == "capture" else [])
    if (not isinstance(authorized, list) or not authorized
            or not isinstance(required, list) or not set(required).issubset(set(authorized))):
        errors.append("incomplete_production_scope")
    if post_only:
        if "capture" in scope.get("authorized_actions", []) or phase == "capture":
            errors.append("post_only_does_not_authorize_capture")
        master = scope.get("base_media", {})
        a = assets.get(master.get("path"), {})
        if a.get("role") != "master" or master.get("sha256") != a.get("sha256"):
            errors.append("missing_base_media_binding")
    if scope.get("capture_medium") not in ("model_render", "panorama_reprojection", "panorama_navigation", "physical_capture"):
        errors.append("invalid_capture_medium")
    if scope.get("validation_scope") not in ("model_only", "physical_verified", "same_point_source"):
        errors.append("invalid_validation_scope")
    if scope.get("capture_medium") == "model_render" and scope.get("validation_scope") not in ("model_only", "physical_verified"):
        errors.append("invalid_model_scope")
    if scope.get("continuity_class") not in ("same_point_rotation", "cross_room_travel", "approved_cut_exception"):
        errors.append("invalid_continuity_class")
    if not post_only:
        methods = {"model_render": "model_mesh", "panorama_reprojection": "panorama_same_point",
                   "panorama_navigation": "panorama_sdk_navigation", "physical_capture": "physical_camera"}
        method = scope.get("render_method")
        if method != methods.get(scope.get("capture_medium")):
            errors.append("invalid_render_method")
        if scope.get("capture_medium") == "panorama_reprojection" and scope.get("continuity_class") == "cross_room_travel":
            errors.append("panorama_reprojection_cannot_travel")
        if scope.get("capture_medium") == "panorama_navigation" and scope.get("validation_scope") not in ("model_only", "physical_verified"):
            errors.append("invalid_panorama_navigation_scope")
        if not isinstance(scope.get("source_namespace"), str) or not scope["source_namespace"].strip():
            errors.append("missing_source_namespace")
        config = scope.get("render_config")
        if (not isinstance(config, dict) or not isinstance(config.get("renderer"), str) or not config["renderer"].strip()
                or any(type(config.get(k)) is not int or config[k] <= 0 for k in ("width", "height"))
                or not number(config.get("dpr")) or config["dpr"] <= 0
                or config.get("fov_axis") not in ("horizontal", "vertical")
                or not number(config.get("fov_deg")) or not 0 < config["fov_deg"] < 180):
            errors.append("invalid_render_config")
        visual_acceptance(scope, assets)
        if phase != "review":
            render_precheck(scope, assets)
    duration, tolerance = scope.get("duration_s"), scope.get("duration_tolerance_s")
    if not number(duration) or duration <= 0 or not number(tolerance) or tolerance < 0:
        errors.append("invalid_duration")
    elif abs(previous - duration) > 0.001:
        errors.append("timeline_duration_mismatch")
    if scope.get("subtitle_content_mode") not in ("verbatim_voiceover", "editorial_keywords"):
        errors.append("missing_subtitle_content_mode")
    if scope.get("subtitle_delivery") not in ("burned_in", "selectable_track", "both"):
        errors.append("missing_subtitle_delivery")
    if any(not scope.get(k) for k in ("opening", "ending", "coverage", "route", "facts_and_rights")):
        errors.append("incomplete_scope")
    scope_text = ("opening", "ending", "route", "facts_and_rights") + (("bgm",) if "bgm" in scope else ())
    if any(not isinstance(scope.get(k), str) or scope[k] not in body for k in scope_text):
        errors.append("scope_not_in_plan")
    if not isinstance(scope.get("coverage"), list) or any(not isinstance(s, str) or not s or s not in body for s in scope.get("coverage", [])):
        errors.append("coverage_not_in_plan")
    exploration = record.get("exploration", {})
    counts = [exploration.get("key_prechecks"), exploration.get("full_route_prechecks")]
    comparisons = exploration.get("comparisons_by_issue", {})
    if (any(c is not None and (type(c) is not int or c < 0) for c in counts)
            or not isinstance(comparisons, dict)
            or any(type(c) is not int or c < 0 for c in comparisons.values())):
        errors.append("invalid_exploration_counts")
    # Only user-specified limits constrain authorized diagnosis. There is no
    # built-in one-route/two-comparison quota or mandatory stop-reason ritual.
    limits = exploration.get("limits", {})
    if not isinstance(limits, dict):
        errors.append("invalid_exploration_limits")
    else:
        for key, limit in limits.items():
            if key not in ("key_prechecks", "full_route_prechecks") or type(limit) is not int or limit < 0:
                errors.append("invalid_exploration_limits")
            elif exploration.get(key, 0) > limit:
                errors.append("user_exploration_limit_exceeded:" + key)

    if phase != "review":
        if record.get("status") != "SCRIPT_APPROVED_ONCE":
            errors.append("not_approved")
        presentation = record.get("presentation")
        if not presentation:
            errors.append("missing_presentation")
        else:
            trace = asset_ok(presentation.get("transcript_path"), presentation.get("transcript_sha256"), "review_transcript")
            events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()] if trace.is_file() else []
            if presentation.get("mode") in ("rendered_document", "linked_document"):
                from document_review import check_document
                errors.extend(check_document(presentation, record.get("approval", {}), events,
                                             base, assets, body, plan_sha, bundle_sha, plan_path))
            else:
                shown_id = presentation.get("assistant_event_id")
                shown = next((e for e in events if e.get("id") == shown_id), {})
                shown_text = text(shown)
                if (presentation.get("mode") != "inline_cards" or shown.get("message", {}).get("role") != "assistant"
                        or body.strip() not in shown_text or plan_sha not in shown_text):
                    errors.append("plan_not_actually_presented")
                if "BUNDLE_SHA256: " + bundle_sha not in shown_text:
                    errors.append("bundle_not_actually_presented")
                approval = record.get("approval", {})
                decided = next((e for e in events if e.get("id") == approval.get("user_event_id")), {})
                quote = approval.get("explicit_text", "")
                if (decided.get("message", {}).get("role") != "user" or not quote or quote != text(decided).strip()
                        or not re.search(r"批准|同意执行|确认执行|\bapprove[ds]?\b", quote, re.I)
                        or re.search(r"不.{0,3}批准|未批准|暂不|不要|拒绝|不同意|不能|not approve|do not approve", quote, re.I)):
                    errors.append("invalid_user_approval")
                if (not shown_id or (decided.get("parentId") is not None and decided.get("parentId") != shown_id)
                        or shown not in events or decided not in events or events.index(decided) <= events.index(shown)):
                    errors.append("approval_not_bound_to_submission")

    output = local(scope.get("output_dir"), inside=True)
    if phase == "post" and scope.get("editing_policy", {}).get("single_take_required"):
        original = output / "raw-original.webm"
        evidence_path = output / "continuous-edit.json"
        if post_only:
            entry = scope.get("continuous_edit_evidence", {})
            bound = assets.get(entry.get("path"), {})
            if bound.get("role") != "continuous_edit_report" or bound.get("sha256") != entry.get("sha256"):
                errors.append("unbound_continuous_edit_evidence")
            if entry.get("path"):
                evidence_path = asset_ok(entry["path"], entry.get("sha256"), "continuous_edit_evidence")
            original = local(scope["base_media"]["path"])
        if not evidence_path.is_file():
            errors.append("missing_continuous_speed_map")
        else:
            evidence = json.loads(evidence_path.read_text())
            if (evidence.get("schema") != "vr-continuous-edit/v1" or not original.is_file()
                    or evidence.get("source_sha256") != digest(original)):
                errors.append("continuous_edit_source_mismatch")
            from storyboard.model import validate_editing
            merged = dict(record)
            merged["scope"] = dict(scope, editing_source_duration_s=evidence.get("source_duration_s"),
                                   speed_map=evidence.get("speed_map"))
            if not evidence.get("speed_map"):
                errors.append("missing_continuous_speed_map")
            else:
                validate_editing(merged)
    if output == base or output in [plan_path, record_path.resolve()] or any(output == local(a) or local(a).is_relative_to(output) for a in assets):
        errors.append("output_overlaps_input")
    record_sha = digest(record_path)
    claim_data = {"record_sha256": record_sha, "plan_sha256": plan_sha, "bundle_sha256": bundle_sha,
                  "state": "RESERVED_DIRECTORY"}
    # Read old receipts without rewriting historical approvals. New linked
    # submissions reserve a directory and have no implicit attempt allowance.
    legacy_claim = scope.get('max_capture_attempts') is not None and record.get('presentation', {}).get('mode') != 'linked_document'
    if legacy_claim:
        claim_data.update(max_capture_attempts=scope['max_capture_attempts'], state='CONSUMED_BEFORE_CAPTURE')
    if phase == "capture" and output.exists():
        errors.append("capture_attempt_already_used")
    if phase == "post":
        if post_only:
            # Re-entering a working directory is normal recovery. The caller
            # preserves existing media and writes changed outputs as new files.
            if output.exists() and not output.is_dir():
                errors.append("post_output_not_directory")
        else:
            claim_path = output / "capture-claim.json"
            receipt = json.loads(claim_path.read_text()) if claim_path.is_file() else {}
            matches = receipt == claim_data if legacy_claim else all(receipt.get(k) == claim_data[k] for k in ('plan_sha256', 'bundle_sha256', 'state'))
            if not matches:
                errors.append("capture_claim_mismatch")
    if claim and not errors:
        try:
            output.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            errors.append("capture_attempt_already_used")
        else:
            # Preserve a failed reservation; use a new directory for a retry.
            with (output / "capture-claim.json").open("x", encoding="utf-8") as f:
                json.dump(claim_data, f, ensure_ascii=False, indent=2)
                f.write("\n")
    return {"passed": not errors, "phase": phase, "read_only": not claim, "errors": sorted(set(errors)),
            "plan_sha256": plan_sha, "bundle_sha256": bundle_sha, "record_sha256": record_sha,
            "output_dir": str(output), "limits": ["Checks evidence structure and hashes, not real-world facts or user identity.",
                "Only the capture entry calling this gate is protected; direct bypass is not intercepted.",
                "Precheck hashes and declared results are verified; image correctness and report authorship are not certified."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--phase", choices=("review", "capture", "post"), default="review")
    parser.add_argument("--claim", action="store_true", help="Reserve a new capture directory, only with --phase capture")
    args = parser.parse_args()
    if args.claim and args.phase != "capture":
        parser.error("--claim requires --phase capture")
    try:
        result = check(args.record.resolve(), args.phase, args.claim)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        result = {"passed": False, "read_only": not args.claim, "errors": ["invalid_record:" + str(e)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    sys.exit(main())
