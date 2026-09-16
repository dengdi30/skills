"""Exercise the monitor's notification contract without network or model calls."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_upstream_flow_subject", ROOT / "scripts/check_upstream.py"
)
MONITOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MONITOR
SPEC.loader.exec_module(MONITOR)

MAIN_COMMIT = "a" * 40
RUN_URL = "https://github.com/example/skills/actions/runs/123"


def group(name="grill-me"):
    return MONITOR.Group(
        id=name,
        repository="https://github.com/example/skills",
        ref="refs/heads/main",
        base="b" * 40,
        skill_paths=(f"skills/{name}",),
        license_paths=("LICENSE",),
    )


def candidate(item, fingerprint="c" * 64):
    return MONITOR.Result(
        group=item,
        status="new",
        head="d" * 40,
        fingerprint=fingerprint,
        files=[f"skills/{item.id}/SKILL.md"],
        diff="--- a/SKILL.md\n+++ b/SKILL.md\n-old instruction\n+new instruction\n",
    )


def summary():
    return {
        "summary": "增加一个澄清步骤。",
        "changes": [{"path": "skills/grill-me/SKILL.md", "description": "先澄清目标。"}],
    }


def receipt(candidates=(), notification_id="receipt", *, login="github-actions[bot]", kind="Bot"):
    marker = {"version": 1, "notification_id": notification_id, "candidates": list(candidates)}
    return {
        "id": 1,
        "html_url": "https://github.com/example/skills/issues/1#issuecomment-1",
        "user": {"login": login, "type": kind},
        "body": "report\n" + MONITOR.MARKER + json.dumps(marker) + "\n-->",
    }


class FakeIssue:
    """Store a published comment so a second run sees actual receipts."""

    def __init__(self, comments=()):
        self.comments = list(comments)
        self.created = []

    def list_comments(self):
        return list(self.comments)

    def create_comment(self, body):
        item = receipt()
        item["id"] = len(self.comments) + 1
        item["html_url"] = f"https://github.com/example/skills/issues/1#issuecomment-{item['id']}"
        item["body"] = body
        self.created.append(item)
        self.comments.append(item)
        return item


class MonitorFlowTest(unittest.TestCase):
    def run_monitor(self, groups, check, issue, summarize, **kwargs):
        return MONITOR.monitor(
            groups, check, issue, summarize,
            main_commit=MAIN_COMMIT, run_url=RUN_URL, **kwargs,
        )

    def test_unchanged_run_is_silent_and_does_not_call_model(self):
        item = group()
        issue, model = FakeIssue(), Mock()
        report = self.run_monitor(
            [item], lambda g: MONITOR.Result(g, status="unchanged"), issue, model, publish=True,
        )
        self.assertEqual(report.body, "")
        self.assertEqual(report.failures, [])
        self.assertEqual(issue.created, [])
        model.assert_not_called()

    def test_existing_candidate_does_not_publish_or_call_model(self):
        item = group()
        issue = FakeIssue([receipt([{"group": item.id, "fingerprint": "c" * 64}])])
        model = Mock()
        report = self.run_monitor([item], candidate, issue, model, publish=True)
        self.assertEqual(report.body, "")
        self.assertEqual(issue.created, [])
        model.assert_not_called()

    def test_identical_content_at_a_new_commit_does_not_renotify(self):
        item, issue = group(), FakeIssue()
        model = Mock(return_value=summary())
        self.run_monitor([item], candidate, issue, model, publish=True)
        same_content = candidate(item)
        same_content.head = "e" * 40
        self.run_monitor([item], lambda _: same_content, issue, model, publish=True)
        self.assertEqual(len(issue.created), 1)
        model.assert_called_once()

    def test_changed_content_is_not_suppressed_by_previous_candidate(self):
        item = group()
        issue = FakeIssue([receipt([{"group": item.id, "fingerprint": "b" * 64}])])
        model = Mock(return_value=summary())
        self.run_monitor([item], candidate, issue, model, publish=True)
        self.assertEqual(len(issue.created), 1)
        self.assertEqual(MONITOR.read_notified(issue.created), {(item.id, "c" * 64)})
        model.assert_called_once_with(candidate(item).diff, candidate(item).files)

    def test_human_marker_cannot_suppress_a_new_candidate(self):
        item = group()
        issue = FakeIssue([receipt(
            [{"group": item.id, "fingerprint": "c" * 64}], login="someone", kind="User",
        )])
        model = Mock(return_value=summary())
        report = self.run_monitor([item], candidate, issue, model, publish=True)
        self.assertEqual(len(issue.created), 1)
        self.assertTrue(report.comment_url)
        model.assert_called_once()

    def test_new_groups_share_one_comment_and_receipt(self):
        groups = [group("grill-me"), group("handoff")]
        issue = FakeIssue()
        report = self.run_monitor(groups, candidate, issue, Mock(return_value=summary()), publish=True)
        self.assertEqual(len(issue.created), 1)
        self.assertEqual(
            MONITOR.read_notified(issue.created),
            {(item.id, "c" * 64) for item in groups},
        )
        self.assertEqual(report.comment_url, issue.created[0]["html_url"])
        self.assertIn(MAIN_COMMIT, report.body)
        self.assertIn(RUN_URL, report.body)

    def test_group_failure_does_not_hide_another_groups_update(self):
        broken, good = group("broken"), group("handoff")
        issue = FakeIssue()

        def check(item):
            if item.id == "broken":
                raise MONITOR.MonitorError("cannot fetch upstream")
            return candidate(item)

        report = self.run_monitor(
            [broken, good], check, issue, Mock(return_value=summary()), publish=True,
        )
        self.assertEqual(len(issue.created), 1)
        self.assertIn(("broken", "cannot fetch upstream"), report.failures)
        self.assertIn("cannot fetch upstream", report.body)
        self.assertEqual(MONITOR.read_notified(issue.created), {("handoff", "c" * 64)})

    def test_model_failure_still_publishes_and_deduplicates_candidate(self):
        item, issue = group(), FakeIssue()
        model = Mock(side_effect=MONITOR.MonitorError("OpenRouter unavailable"))
        report = self.run_monitor([item], candidate, issue, model, publish=True)
        self.assertEqual(len(issue.created), 1)
        self.assertTrue(report.failures)
        self.assertIn("OpenRouter unavailable", report.body)
        self.assertIn(item.repository, report.body)
        self.assertIn("b" * 40, report.body)
        self.assertIn("d" * 40, report.body)
        self.assertEqual(MONITOR.read_notified(issue.created), {(item.id, "c" * 64)})
        self.run_monitor([item], candidate, issue, model, publish=True)
        self.assertEqual(len(issue.created), 1)
        model.assert_called_once()

    def test_failure_only_run_posts_each_time_without_fault_dedup(self):
        item, issue = group(), FakeIssue()
        check = Mock(side_effect=MONITOR.MonitorError("missing LICENSE"))
        model = Mock()
        for _ in range(2):
            report = self.run_monitor([item], check, issue, model, publish=True)
            self.assertIn("missing LICENSE", report.body)
        self.assertEqual(len(issue.created), 2)
        self.assertEqual(MONITOR.read_notified(issue.created), set())
        model.assert_not_called()

    def test_history_failure_checks_all_groups_but_suppresses_candidates(self):
        groups = [group("grill-me"), group("handoff")]
        issue = FakeIssue()
        issue.list_comments = Mock(side_effect=MONITOR.MonitorError("history unavailable"))
        check, model = Mock(side_effect=candidate), Mock()
        report = self.run_monitor(groups, check, issue, model, publish=True)
        self.assertEqual(check.call_count, 2)
        model.assert_not_called()
        self.assertEqual(len(issue.created), 1)
        self.assertIn("history unavailable", report.body)
        self.assertEqual(MONITOR.read_notified(issue.created), set())

    def test_corrupt_bot_history_is_reported_without_marking_candidates_notified(self):
        broken = receipt()
        broken["body"] = MONITOR.MARKER + "{broken\n-->"
        issue, model = FakeIssue([broken]), Mock()
        report = self.run_monitor([group()], candidate, issue, model, publish=True)
        self.assertTrue(report.failures)
        self.assertEqual(len(issue.created), 1)
        self.assertEqual(MONITOR.read_notified(issue.created), set())
        model.assert_not_called()

    def test_preview_can_render_without_issue_or_model(self):
        report = self.run_monitor([group()], candidate, None, None)
        self.assertEqual(report.failures, [])
        self.assertEqual(report.comment_url, "")
        self.assertTrue(report.body)

    def test_preview_never_creates_comment(self):
        issue = FakeIssue()
        self.run_monitor([group()], candidate, issue, Mock(return_value=summary()))
        self.assertEqual(issue.created, [])

    def test_model_verification_can_run_without_updates(self):
        item, model = group(), Mock(return_value=summary())
        report = self.run_monitor(
            [item], lambda g: MONITOR.Result(g, status="unchanged"), FakeIssue(), model,
            verify_model=True, publish=True,
        )
        self.assertTrue(report.model_verified)
        self.assertEqual(report.body, "")
        model.assert_called_once()

    def test_model_verification_failure_does_not_skip_regular_updates(self):
        model = Mock(side_effect=[MONITOR.MonitorError("probe failed"), summary()])
        issue = FakeIssue()
        report = self.run_monitor([group()], candidate, issue, model, verify_model=True, publish=True)
        self.assertFalse(report.model_verified)
        self.assertEqual(model.call_count, 2)
        self.assertIn("probe failed", report.body)
        self.assertEqual(MONITOR.read_notified(issue.created), {("grill-me", "c" * 64)})


class PublishOnceTest(unittest.TestCase):
    def test_successful_publish_returns_comment(self):
        issue = FakeIssue()
        result = MONITOR.publish_once(issue, receipt(notification_id="target")["body"], "target")
        self.assertEqual(result, issue.created[0])

    def test_ambiguous_response_recovers_existing_receipt_without_reposting(self):
        existing = receipt(notification_id="target")
        issue = Mock()
        issue.create_comment.side_effect = MONITOR.MonitorError("response lost")
        issue.list_comments.return_value = [existing]
        self.assertEqual(MONITOR.publish_once(issue, existing["body"], "target"), existing)
        issue.create_comment.assert_called_once()

    def test_absent_receipt_after_ambiguous_response_raises_without_retry(self):
        issue = Mock()
        issue.create_comment.side_effect = MONITOR.MonitorError("response lost")
        issue.list_comments.return_value = [receipt(notification_id="other")]
        with self.assertRaises(MONITOR.MonitorError):
            MONITOR.publish_once(issue, receipt(notification_id="target")["body"], "target")
        issue.create_comment.assert_called_once()

    def test_recovery_does_not_trust_human_receipt_or_bot_name_with_user_type(self):
        for login, kind in [("someone", "User"), ("github-actions[bot]", "User")]:
            with self.subTest(login=login, kind=kind):
                issue = Mock()
                issue.create_comment.side_effect = MONITOR.MonitorError("response lost")
                issue.list_comments.return_value = [receipt(notification_id="target", login=login, kind=kind)]
                with self.assertRaises(MONITOR.MonitorError):
                    MONITOR.publish_once(issue, receipt(notification_id="target")["body"], "target")
                issue.create_comment.assert_called_once()

    def test_unreadable_history_after_publish_failure_raises_without_retry(self):
        issue = Mock()
        issue.create_comment.side_effect = MONITOR.MonitorError("response lost")
        issue.list_comments.side_effect = MONITOR.MonitorError("history unavailable")
        with self.assertRaises(MONITOR.MonitorError):
            MONITOR.publish_once(issue, receipt(notification_id="target")["body"], "target")
        issue.create_comment.assert_called_once()


if __name__ == "__main__":
    unittest.main()
