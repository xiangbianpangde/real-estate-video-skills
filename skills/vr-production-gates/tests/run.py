#!/usr/bin/env python3
"""Python 3.10+; real CLI regression, fixtures are synthetic (not production assets)."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_shooting_plan.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png(path):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")) + chunk(b"IEND", b""))


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="vr-plan-test-")
        self.root = Path(self.tmp.name)
        png(self.root / "overview.png")
        png(self.root / "S01.png")
        png(self.root / "S02.png")
        self.body = ("# 图文脚本 v1\n\n![方案](overview.png)\n\n"
                     "## S01\n![首镜源](S01.png)\n推进；空间；核证字幕；已批准素材库BGM；已披露\n\n"
                     "## S02\n![尾镜源](S02.png)\n推进；空间；核证字幕；已批准素材库BGM；已披露\n\n"
                     "## 制作范围\n室内连续背景+户型图；室内获准CTA；素材库指定授权池；公共区；连续相机轨迹；已核证；仅内部\n"
                     "成像方法model_mesh；房源HOUSE-TEST/WORK-TEST；预检报告precheck.json\n")
        (self.root / "plan_v1.md").write_text(self.body)
        (self.root / "source.bin").write_bytes(b"frozen source")
        self.record = {
            "schema": "vr-production-plan/v2", "status": "SCRIPT_APPROVED_ONCE",
            "plan": {"version": "v1", "path": "plan_v1.md", "sha256": sha(self.root / "plan_v1.md")},
            "assets": [{"path": p, "sha256": sha(self.root / p), "role": role, "origin": "actual_source"}
                       for p, role in [("overview.png", "overview"), ("S01.png", "reference"),
                                       ("S02.png", "reference"), ("source.bin", "source")]],
            "segments": [{"id": f"S0{i}", "start_s": (i-1)*5, "end_s": i*5,
                          "reference_image": f"S0{i}.png", "action": "推进", "focus": "空间",
                          "text": "核证字幕", "highlights": [], "music": "已批准素材库BGM", "risk": "已披露"}
                         for i in [1, 2]],
            "scope": {"capture_medium": "model_render", "validation_scope": "model_only",
                      "continuity_class": "cross_room_travel", "max_capture_attempts": 1,
                      "duration_s": 10, "duration_tolerance_s": 0.5, "output_dir": "take01",
                      "authorized_actions": ["capture", "opening", "ending", "subtitles", "bgm", "encode", "qc"],
                      "subtitle_content_mode": "editorial_keywords", "subtitle_delivery": "burned_in",
                      "opening": "室内连续背景+户型图", "ending": "室内获准CTA", "bgm": "素材库指定授权池",
                      "coverage": ["公共区"], "route": "连续相机轨迹", "facts_and_rights": "已核证；仅内部",
                      "not_authorized": ["publish", "paid_service", "reshoot"]},
            "exploration": {"key_prechecks": 1, "full_route_prechecks": 1, "comparisons_by_issue": {"glass": 2},
                            "stop_reason": "源限制已披露，不追加随机探索"},
            "presentation": {"transcript_path": "review.jsonl", "assistant_event_id": "shown", "mode": "inline_cards"},
            "approval": {"user_event_id": "approved", "explicit_text": "批准这版及列明完整制作范围"}
        }
        # Evidence files are synthetic gate fixtures, not real visual-QC proof.
        config = {"renderer": "test-renderer@1", "width": 720, "height": 1280,
                  "dpr": 1, "fov_axis": "vertical", "fov_deg": 85.57}
        self.record["scope"].update({"source_namespace": "HOUSE-TEST/WORK-TEST",
                                    "render_method": "model_mesh", "render_config": config})
        self.precheck = {"schema": "vr-render-precheck/v1", "source_namespace": "HOUSE-TEST/WORK-TEST",
                         "capture_medium": "model_render", "validation_scope": "model_only",
                         "render_method": "model_mesh", "render_config": config,
                         "continuity_class": "cross_room_travel", "route": "连续相机轨迹",
                         "coverage": ["公共区"], "source_sha256": {"source.bin": sha(self.root / "source.bin")},
                         "evidence_kind": "continuous_media", "complete_interval_reviewed": True,
                         "checks": {"control": "PASS", "visual": "PASS", "playback": "PASS", "state_restore": "PASS"},
                         "evidence": {}}
        for key, name in [("media", "precheck.webm"), ("telemetry", "telemetry.json"),
                          ("review", "visual-review.md"), ("restore", "restore.json")]:
            (self.root / name).write_bytes(("synthetic:" + key).encode())
            entry = {"path": name, "sha256": sha(self.root / name)}
            self.precheck["evidence"][key] = entry
            self.record["assets"].append({**entry, "role": "precheck", "origin": "synthetic_fixture"})
        self.save_precheck()
        self.events = [{"id": "shown", "message": {"role": "assistant", "content": [
            {"type": "text", "text": self.body + "\nSHA256: " + self.record["plan"]["sha256"]}]}},
            {"id": "approved", "parentId": "shown", "message": {"role": "user", "content": [
                {"type": "text", "text": self.record["approval"]["explicit_text"]}]}}]
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save_precheck(self):
        path = self.root / "precheck.json"
        path.write_text(json.dumps(self.precheck, ensure_ascii=False))
        entry = {"path": "precheck.json", "sha256": sha(path)}
        self.record["scope"]["render_validation"] = entry
        self.record["assets"] = [a for a in self.record["assets"] if a["path"] != "precheck.json"]
        self.record["assets"].append({**entry, "role": "precheck_report", "origin": "synthetic_fixture"})
        if hasattr(self, "events"):
            # Re-present this synthetic variant so the test isolates render validity,
            # not a stale bundle approval (covered by the existing drift cases).
            del self.presented_bundle_sha
            self.events[0]["message"]["content"][0]["text"] = self.body + "\nSHA256: " + self.record["plan"]["sha256"]

    def save(self):
        bundle = {key: self.record[key] for key in ("plan", "assets", "segments", "scope", "exploration")}
        bundle_sha = hashlib.sha256(json.dumps(bundle, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        if not hasattr(self, "presented_bundle_sha"):
            self.presented_bundle_sha = bundle_sha
        text = self.events[0]["message"]["content"][0]["text"]
        if "BUNDLE_SHA256:" not in text:
            self.events[0]["message"]["content"][0]["text"] = text + "\nBUNDLE_SHA256: " + self.presented_bundle_sha
        trace = self.root / "review.jsonl"
        trace.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in self.events))
        self.record["presentation"]["transcript_sha256"] = sha(trace)
        (self.root / "record.json").write_text(json.dumps(self.record, ensure_ascii=False))

    def run_gate(self, phase="capture", claim=False):
        self.save()
        argv = [sys.executable, str(SCRIPT), "--record", str(self.root / "record.json"), "--phase", phase]
        if claim:
            argv.append("--claim")
        result = subprocess.run(argv, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return result.returncode, data

    def rejected(self, code, phase="capture", claim=False):
        exit_code, data = self.run_gate(phase, claim=claim)
        self.assertNotEqual(exit_code, 0, data)
        self.assertIn(code, data["errors"], data)
        self.assertFalse((self.root / "take01").exists())

    def visual_reference_record(self, visual="PASS_WITH_LIMITATIONS"):
        # Synthetic reference/decision: proves contract handling, not actual video quality.
        (self.root / "accepted-reference.mp4").write_bytes(b"synthetic accepted kitchen reference")
        criteria = "参考中的过渡重影属于接受范围，按整体布局与观看效果比较。"
        decision = {"schema": "vr-visual-acceptance/v1",
                    "reference_sha256": sha(self.root / "accepted-reference.mp4"),
                    "criteria": criteria,
                    "user_event": {"id": "criteria-user", "message": {"role": "user", "content": criteria}}}
        (self.root / "visual-decision.json").write_text(json.dumps(decision, ensure_ascii=False))
        policy = {"reference": {"path": "accepted-reference.mp4", "sha256": decision["reference_sha256"]},
                  "decision": {"path": "visual-decision.json", "sha256": sha(self.root / "visual-decision.json")}}
        self.record["scope"]["visual_acceptance"] = policy
        for key, role in [("reference", "acceptance_reference"), ("decision", "acceptance_decision")]:
            self.record["assets"].append({**policy[key], "role": role, "origin": "synthetic_fixture"})
        self.precheck["visual_acceptance"] = json.loads(json.dumps(policy))
        self.precheck["checks"]["visual"] = visual
        self.limitation = "S01 0–5秒：过渡门框重影，到达后主体可读。"
        self.precheck["visual_review"] = {"within_user_criteria": True, "limitations": [self.limitation]}
        self.body += ("\n## 用户视觉基准\naccepted-reference.mp4 SHA256: " + decision["reference_sha256"]
                      + "\nvisual-decision.json\n" + criteria + "\n" + self.limitation + "\n")
        path = self.root / "plan_v1.md"
        path.write_text(self.body)
        self.record["plan"]["sha256"] = sha(path)
        self.save_precheck()
        self.save()

    def save_visual_decision(self, decision):
        path = self.root / "visual-decision.json"
        path.write_text(json.dumps(decision, ensure_ascii=False))
        self.record["scope"]["visual_acceptance"]["decision"]["sha256"] = sha(path)
        next(a for a in self.record["assets"] if a["role"] == "acceptance_decision")["sha256"] = sha(path)
        self.precheck["visual_acceptance"] = json.loads(json.dumps(self.record["scope"]["visual_acceptance"]))
        self.save_precheck()

    def test_complete_plan_readonly(self):
        code, data = self.run_gate()
        self.assertEqual(code, 0, data)
        self.assertTrue(data["read_only"])
        self.assertFalse((self.root / "take01").exists())

    def test_missing_picture(self):
        (self.root / "S01.png").unlink()
        self.rejected("missing_asset:S01.png")

    def test_text_only(self):
        p = self.root / "plan_v1.md"
        p.write_text("# 图文脚本 v1\nS01\nS02\n")
        self.record["plan"]["sha256"] = sha(p)
        self.rejected("missing_embedded_reference:S01")

    def test_path_only_is_not_submission(self):
        self.events[0]["message"]["content"][0]["text"] = "请批准plan_v1.md SHA256:" + self.record["plan"]["sha256"]
        self.rejected("plan_not_actually_presented")

    def test_missing_submission(self):
        self.record.pop("presentation")
        # Write directly because save intentionally needs a presentation.
        (self.root / "record.json").write_text(json.dumps(self.record))
        r = subprocess.run([sys.executable, str(SCRIPT), "--record", str(self.root / "record.json"), "--phase", "capture"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing_presentation", json.loads(r.stdout)["errors"])

    def test_content_version_drift(self):
        (self.root / "plan_v1.md").write_text(self.body + "未获准新CTA")
        self.rejected("plan_sha_mismatch")

    def test_image_version_drift(self):
        (self.root / "S01.png").write_bytes((self.root / "S01.png").read_bytes() + b"changed")
        self.rejected("asset_sha_mismatch:S01.png")

    def test_refreshed_hash_without_resubmission(self):
        p = self.root / "plan_v1.md"
        p.write_text(self.body + "新版本")
        self.record["plan"]["sha256"] = sha(p)
        self.rejected("plan_not_actually_presented")

    def test_abstract_image_not_real_source(self):
        self.record["assets"][1]["origin"] = "schematic"
        self.rejected("non_source_reference:S01")

    def test_wrong_user_role(self):
        self.events[1]["message"]["role"] = "assistant"
        self.rejected("invalid_user_approval")

    def test_approval_not_reply_to_submission(self):
        self.events[1]["parentId"] = "other"
        self.rejected("approval_not_bound_to_submission")

    def test_draft_not_capture_ready(self):
        self.record["status"] = "DRAFT"
        self.rejected("not_approved")
        code, data = self.run_gate("review")
        self.assertEqual(code, 0, data)

    def test_exploration_over_budget(self):
        self.record["exploration"]["comparisons_by_issue"]["glass"] = 3
        self.rejected("exploration_budget_exceeded")

    def test_card_fields_hidden_in_json(self):
        self.body = self.body.replace("推进；空间；核证字幕；已批准素材库BGM；已披露", "", 1)
        (self.root / "plan_v1.md").write_text(self.body)
        self.record["plan"]["sha256"] = sha(self.root / "plan_v1.md")
        self.rejected("card_content_not_in_plan:S01", "review")

    def test_scope_hidden_in_json(self):
        self.body = self.body.split("## 制作范围")[0]
        (self.root / "plan_v1.md").write_text(self.body)
        self.record["plan"]["sha256"] = sha(self.root / "plan_v1.md")
        self.rejected("scope_not_in_plan", "review")

    def test_not_approved_phrase(self):
        self.record["approval"]["explicit_text"] = "不予批准"
        self.events[1]["message"]["content"][0]["text"] = "不予批准"
        self.rejected("invalid_user_approval")

    def test_missing_post_permission(self):
        self.record["scope"]["authorized_actions"].remove("bgm")
        self.rejected("incomplete_production_scope")

    def test_output_exists(self):
        (self.root / "take01").mkdir()
        code, data = self.run_gate()
        self.assertNotEqual(code, 0)
        self.assertIn("capture_attempt_already_used", data["errors"])

    def test_one_capture_then_post_not_reshoot(self):
        code, data = self.run_gate(claim=True)
        self.assertEqual(code, 0, data)
        self.assertFalse(data["read_only"])
        code, data = self.run_gate(claim=True)
        self.assertNotEqual(code, 0)
        self.assertIn("capture_attempt_already_used", data["errors"])
        code, data = self.run_gate("post")
        self.assertEqual(code, 0, data)
        self.assertTrue(data["read_only"])

    def test_concurrent_capture_only_one_claim(self):
        argv = [sys.executable, str(SCRIPT), "--record", str(self.root / "record.json"), "--phase", "capture", "--claim"]
        processes = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        codes = [p.communicate() and p.returncode for p in processes]
        self.assertEqual(sorted(codes), [0, 2])

    def test_scope_drift_without_reapproval(self):
        self.record["scope"]["ending"] = "未经批准新CTA"
        self.rejected("bundle_not_actually_presented")

    def test_claim_invalid_after_record_drift(self):
        code, data = self.run_gate(claim=True)
        self.assertEqual(code, 0, data)
        self.record["scope"]["ending"] = "改尾镜"
        self.rejected_post("capture_claim_mismatch")

    def rejected_post(self, expected):
        code, data = self.run_gate("post")
        self.assertNotEqual(code, 0)
        self.assertIn(expected, data["errors"])

    def post_only_record(self):
        # This is a synthetic, separately approved amendment, not retroactive capture approval.
        (self.root / "existing-master.webm").write_bytes(b"original immutable master")
        self.record["assets"].append({"path": "existing-master.webm", "sha256": sha(self.root / "existing-master.webm"),
                                      "role": "master", "origin": "actual_source"})
        self.record["scope"]["execution_mode"] = "post_only"
        self.record["scope"]["authorized_actions"].remove("capture")
        self.record["scope"]["base_media"] = {"path": "existing-master.webm", "sha256": sha(self.root / "existing-master.webm")}
        self.record["scope"]["output_dir"] = "post_v2"
        if hasattr(self, "presented_bundle_sha"):
            del self.presented_bundle_sha
        self.events[0]["message"]["content"][0]["text"] = self.body + "\nSHA256: " + self.record["plan"]["sha256"]
        self.save()

    def test_newly_approved_post_amendment_without_capture(self):
        self.post_only_record()
        code, data = self.run_gate("post")
        self.assertEqual(code, 0, data)
        self.assertFalse((self.root / "post_v2").exists())
        self.assertFalse((self.root / "take01").exists())
        code, data = self.run_gate("capture", claim=True)
        self.assertNotEqual(code, 0)
        self.assertIn("post_only_does_not_authorize_capture", data["errors"])
        self.assertFalse((self.root / "post_v2").exists())

    def test_post_only_base_media_drift(self):
        self.post_only_record()
        (self.root / "existing-master.webm").write_bytes(b"modified")
        code, data = self.run_gate("post")
        self.assertNotEqual(code, 0)
        self.assertIn("asset_sha_mismatch:existing-master.webm", data["errors"])

    def test_post_only_cannot_overwrite(self):
        self.post_only_record()
        (self.root / "post_v2").mkdir()
        code, data = self.run_gate("post")
        self.assertNotEqual(code, 0)
        self.assertIn("post_output_already_exists", data["errors"])

    def test_nan_duration_rejected(self):
        self.record["scope"]["duration_s"] = float("nan")
        self.rejected("invalid_duration")

    def test_missing_render_precheck_blocks_claim(self):
        del self.record["scope"]["render_validation"]
        del self.presented_bundle_sha
        self.events[0]["message"]["content"][0]["text"] = self.body + "\nSHA256: " + self.record["plan"]["sha256"]
        self.rejected("missing_render_validation", claim=True)
        code, data = self.run_gate("review")
        self.assertEqual(code, 0, data)

    def test_prior_method_pass_does_not_transfer(self):
        self.precheck["render_method"] = "panorama_same_point"
        self.save_precheck()
        self.rejected("render_precheck_identity_mismatch:render_method")

    def test_other_source_pass_does_not_transfer(self):
        self.precheck["source_namespace"] = "OTHER/WORK"
        self.save_precheck()
        self.rejected("render_precheck_identity_mismatch:source_namespace")

    def test_static_endpoints_not_dynamic_proof(self):
        self.precheck["evidence_kind"] = "static_endpoints"
        self.save_precheck()
        self.rejected("render_precheck_not_continuous")

    def test_visual_fail_not_overridden_by_control_pass(self):
        self.precheck["checks"]["visual"] = "FAIL"
        self.save_precheck()
        self.rejected("render_precheck_not_passed:visual", claim=True)

    def test_invalid_control_not_visual_pass(self):
        self.precheck["checks"]["control"] = "FAIL"
        self.save_precheck()
        self.rejected("render_precheck_not_passed:control")

    def test_partial_review_not_complete(self):
        self.precheck["complete_interval_reviewed"] = False
        self.save_precheck()
        self.rejected("render_precheck_not_continuous")

    def test_route_or_config_drift_requires_new_precheck(self):
        self.precheck["route"] = "其他路线"
        self.precheck["render_config"] = {**self.precheck["render_config"], "fov_deg": 95}
        self.save_precheck()
        self.rejected("render_precheck_identity_mismatch:route")

    def test_media_evidence_missing_blocks_capture(self):
        (self.root / "precheck.webm").unlink()
        self.rejected("missing_asset:precheck.webm")

    def test_source_hash_in_precheck_must_match(self):
        self.precheck["source_sha256"]["source.bin"] = "0" * 64
        self.save_precheck()
        self.rejected("render_precheck_source_mismatch")

    def test_panorama_reprojection_cannot_claim_cross_point_travel(self):
        self.record["scope"].update({"capture_medium": "panorama_reprojection",
                                     "validation_scope": "same_point_source", "render_method": "panorama_same_point"})
        self.rejected("panorama_reprojection_cannot_travel")

    def test_precheck_evidence_hash_drift_rejected_before_claim(self):
        (self.root / "telemetry.json").write_bytes(b"changed camera controls")
        self.rejected("asset_sha_mismatch:telemetry.json", claim=True)

    def test_panorama_navigation_requires_own_valid_report(self):
        self.body = self.body.replace("model_mesh", "panorama_sdk_navigation")
        path = self.root / "plan_v1.md"
        path.write_text(self.body)
        self.record["plan"]["sha256"] = sha(path)
        self.record["scope"].update({"capture_medium": "panorama_navigation", "render_method": "panorama_sdk_navigation"})
        self.precheck.update({"capture_medium": "panorama_navigation", "render_method": "panorama_sdk_navigation"})
        self.save_precheck()
        code, data = self.run_gate(claim=True)
        self.assertEqual(code, 0, data)
        self.assertTrue((self.root / "take01/capture-claim.json").is_file())

    def test_same_point_can_reuse_matching_continuous_evidence(self):
        self.body = self.body.replace("model_mesh", "panorama_same_point")
        path = self.root / "plan_v1.md"
        path.write_text(self.body)
        self.record["plan"]["sha256"] = sha(path)
        values = {"capture_medium": "panorama_reprojection", "render_method": "panorama_same_point",
                  "validation_scope": "same_point_source", "continuity_class": "same_point_rotation"}
        self.record["scope"].update(values)
        self.precheck.update(values)
        self.save_precheck()
        code, data = self.run_gate()
        self.assertEqual(code, 0, data)
        self.assertFalse((self.root / "take01").exists())

    def test_malformed_or_draft_config_rejected(self):
        self.record["scope"]["render_config"] = {"renderer": "", "width": 720, "height": 1280,
                                                  "dpr": 1, "fov_axis": "vertical", "fov_deg": 85.57}
        self.rejected("invalid_render_config")

    def test_render_binding_hidden_from_plan(self):
        path = self.root / "plan_v1.md"
        path.write_text(self.body.replace("预检报告precheck.json", "预检报告待填"))
        self.record["plan"]["sha256"] = sha(path)
        self.rejected("render_binding_not_in_plan", "review")

    def test_post_only_not_blocked_by_failed_render_precheck(self):
        self.precheck["checks"]["visual"] = "FAIL"
        self.save_precheck()
        self.post_only_record()
        code, data = self.run_gate("post")
        self.assertEqual(code, 0, data)
        self.assertFalse((self.root / "post_v2").exists())

    def test_user_reference_limits_can_capture_and_post(self):
        self.visual_reference_record()
        code, data = self.run_gate(claim=True)
        self.assertEqual(code, 0, data)
        self.assertTrue((self.root / "take01/capture-claim.json").is_file())
        code, data = self.run_gate("post")
        self.assertEqual(code, 0, data)

    def test_user_reference_clean_pass(self):
        self.visual_reference_record("PASS")
        self.precheck["visual_review"]["limitations"] = []
        self.save_precheck()
        code, data = self.run_gate()
        self.assertEqual(code, 0, data)

    def test_limits_without_user_reference_rejected(self):
        self.precheck["checks"]["visual"] = "PASS_WITH_LIMITATIONS"
        self.save_precheck()
        self.rejected("missing_visual_acceptance", claim=True)

    def test_user_reference_outside_criteria_rejected(self):
        self.visual_reference_record()
        self.precheck["visual_review"]["within_user_criteria"] = False
        self.save_precheck()
        self.rejected("visual_acceptance_not_matched", claim=True)

    def test_user_reference_comparison_missing_rejected(self):
        self.visual_reference_record()
        self.precheck.pop("visual_review")
        self.save_precheck()
        self.rejected("visual_acceptance_not_matched")

    def test_user_reference_clean_pass_cannot_skip_comparison(self):
        self.visual_reference_record("PASS")
        self.precheck.pop("visual_review")
        self.save_precheck()
        self.rejected("visual_acceptance_not_matched")

    def test_user_reference_limits_cannot_be_empty(self):
        self.visual_reference_record()
        self.precheck["visual_review"]["limitations"] = []
        self.save_precheck()
        self.rejected("missing_visual_limitations")

    def test_user_reference_limits_must_be_visible_in_plan(self):
        self.visual_reference_record()
        self.precheck["visual_review"]["limitations"] = ["S02 5–10秒：未展示的新缺陷"]
        self.save_precheck()
        self.rejected("visual_limitations_not_in_plan")

    def test_user_reference_binding_hidden_from_plan(self):
        self.visual_reference_record()
        self.body = self.body.replace("accepted-reference.mp4 SHA256:", "参考地址未展示 SHA256:")
        path = self.root / "plan_v1.md"
        path.write_text(self.body)
        self.record["plan"]["sha256"] = sha(path)
        self.save_precheck()
        self.rejected("visual_acceptance_not_in_plan", "review")

    def test_user_reference_criteria_hidden_from_plan(self):
        self.visual_reference_record()
        decision = json.loads((self.root / "visual-decision.json").read_text())
        self.body = self.body.replace(decision["criteria"], "标准未展示")
        path = self.root / "plan_v1.md"
        path.write_text(self.body)
        self.record["plan"]["sha256"] = sha(path)
        self.save_precheck()
        self.rejected("visual_acceptance_not_in_plan")

    def test_user_reference_wrong_decision_role_rejected(self):
        self.visual_reference_record()
        decision = json.loads((self.root / "visual-decision.json").read_text())
        decision["user_event"]["message"]["role"] = "assistant"
        self.save_visual_decision(decision)
        self.rejected("invalid_visual_acceptance_decision")

    def test_user_reference_criteria_cannot_be_agent_rewrite(self):
        self.visual_reference_record()
        decision = json.loads((self.root / "visual-decision.json").read_text())
        decision["criteria"] = "AI自行增加零重影门槛"
        self.save_visual_decision(decision)
        self.rejected("invalid_visual_acceptance_decision")

    def test_user_reference_decision_sha_mismatch_rejected(self):
        self.visual_reference_record()
        decision = json.loads((self.root / "visual-decision.json").read_text())
        decision["reference_sha256"] = "0" * 64
        self.save_visual_decision(decision)
        self.rejected("visual_reference_decision_mismatch")

    def test_user_reference_asset_role_required(self):
        self.visual_reference_record()
        next(a for a in self.record["assets"] if a["role"] == "acceptance_reference")["role"] = "source"
        self.save_precheck()
        self.rejected("unbound_visual_acceptance:reference")

    def test_user_reference_report_cannot_use_other_policy(self):
        self.visual_reference_record()
        self.precheck["visual_acceptance"]["reference"]["sha256"] = "0" * 64
        self.save_precheck()
        self.rejected("render_precheck_identity_mismatch:visual_acceptance")

    def test_user_reference_media_drift_blocks_claim(self):
        self.visual_reference_record()
        (self.root / "accepted-reference.mp4").write_bytes(b"other reference")
        self.rejected("asset_sha_mismatch:accepted-reference.mp4", claim=True)

    def test_user_reference_fail_is_not_overridden(self):
        self.visual_reference_record("FAIL")
        self.rejected("render_precheck_not_passed:visual", claim=True)

    def test_user_reference_control_fail_still_blocks(self):
        self.visual_reference_record()
        self.precheck["checks"]["control"] = "FAIL"
        self.save_precheck()
        self.rejected("render_precheck_not_passed:control", claim=True)

    def test_user_reference_partial_media_review_still_blocks(self):
        self.visual_reference_record()
        self.precheck["complete_interval_reviewed"] = False
        self.save_precheck()
        self.rejected("render_precheck_not_continuous", claim=True)

    def test_user_reference_change_cannot_keep_old_approval(self):
        self.visual_reference_record()
        self.run_gate("review")
        self.record["scope"]["visual_acceptance"]["reference"]["sha256"] = "0" * 64
        self.rejected("bundle_not_actually_presented")

    def layout_record(self):
        self.record["schema"] = "vr-production-plan/v3"
        (self.root / "storyboard.html").write_text("<main>synthetic layout fixture</main>")
        self.record["scope"]["storyboard_layout"] = {"kind": "overview_board", "board": "overview.png",
                                                       "source": "storyboard.html", "review": "layout-review.json"}
        self.layout = {"schema": "vr-storyboard-layout-review/v1", "board_sha256": sha(self.root / "overview.png"),
                       "source_sha256": sha(self.root / "storyboard.html"), "segment_ids": ["S01", "S02"],
                       "all_images_loaded": True, "no_overflow": True, "reference_structure_matches": True,
                       "motion_diagrams_reviewed": True, "opening_composite_reviewed": True,
                       "review_basis": "Synthetic gate evidence; does not establish layout quality"}
        self.save_layout()

    def save_layout(self):
        (self.root / "layout-review.json").write_text(json.dumps(self.layout))
        self.record["assets"] = [a for a in self.record["assets"] if a['role'] not in ('storyboard_source', 'layout_review')]
        for name, role in (("storyboard.html", "storyboard_source"), ("layout-review.json", "layout_review")):
            self.record["assets"].append({"path": name, "sha256": sha(self.root / name), "role": role})

    def test_v3_raw_images_without_board_evidence_rejected(self):
        self.record['schema'] = 'vr-production-plan/v3'
        self.rejected('missing_storyboard_layout', phase='review')

    def test_v3_layout_binding_valid(self):
        self.layout_record()
        code, result = self.run_gate('review')
        self.assertEqual(code, 0, result)

    def test_v3_layout_cannot_omit_section(self):
        self.layout_record()
        self.layout['segment_ids'] = ['S01']
        self.save_layout()
        self.rejected('layout_review_segments_mismatch', phase='review')

    def test_v3_overflow_blocks_submission(self):
        self.layout_record()
        self.layout['no_overflow'] = False
        self.save_layout()
        self.rejected('layout_review_not_passed:no_overflow', phase='review')

    def test_v3_changed_board_needs_new_layout_review(self):
        self.layout_record()
        (self.root / 'overview.png').write_bytes((self.root / 'overview.png').read_bytes() + b'changed')
        self.record['assets'][0]['sha256'] = sha(self.root / 'overview.png')
        self.rejected('layout_review_sha_mismatch', phase='review')

    def test_v3_layout_requires_reference_comparison(self):
        self.layout_record()
        self.layout['reference_structure_matches'] = False
        self.save_layout()
        self.rejected('layout_review_not_passed:reference_structure_matches', phase='review')

    def test_v3_missing_motion_visual_review_rejected(self):
        self.layout_record()
        self.layout.pop('motion_diagrams_reviewed')
        self.save_layout()
        self.rejected('layout_review_not_passed:motion_diagrams_reviewed', phase='review')

    def test_v3_unreviewed_opening_composite_rejected(self):
        self.layout_record()
        self.layout['opening_composite_reviewed'] = False
        self.save_layout()
        self.rejected('layout_review_not_passed:opening_composite_reviewed', phase='review')

    def test_malformed_json_fails_closed(self):
        (self.root / "broken.json").write_text("{")
        r = subprocess.run([sys.executable, str(SCRIPT), "--record", str(self.root / "broken.json"), "--phase", "capture"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(json.loads(r.stdout)["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
