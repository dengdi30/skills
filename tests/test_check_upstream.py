import importlib.util
import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_upstream", ROOT / "scripts/check_upstream.py")
MONITOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MONITOR
SPEC.loader.exec_module(MONITOR)


def comment(candidates, login="github-actions[bot]", notification_id="test"):
    marker = {"version": 1, "notification_id": notification_id, "candidates": candidates}
    return {"user": {"login": login, "type": "Bot"},
            "body": "report\n<!-- upstream-monitor:v1\n" + json.dumps(marker) + "\n-->"}


class NotificationIdentityTest(unittest.TestCase):
    def test_identity_tracks_paths_modes_and_contents_but_not_listing_order(self):
        entries = [("100644", "blob", "a" * 40, "skill/SKILL.md"),
                   ("100644", "blob", "b" * 40, "LICENSE")]
        fp = MONITOR.content_fingerprint("https://github.com/example/skills", ["skill", "LICENSE"], entries)
        self.assertEqual(fp, MONITOR.content_fingerprint(
            "https://github.com/example/skills", ["LICENSE", "skill"], list(reversed(entries))))
        for changed in [("100755", "blob", "a" * 40, "skill/SKILL.md"),
                        ("100644", "blob", "c" * 40, "skill/SKILL.md"),
                        ("100644", "blob", "a" * 40, "skill/RENAMED.md")]:
            self.assertNotEqual(fp, MONITOR.content_fingerprint(
                "https://github.com/example/skills", ["skill", "LICENSE"], [changed, entries[1]]))

    def test_only_valid_bot_receipts_count(self):
        candidate = {"group": "grill-me", "fingerprint": "a" * 64}
        self.assertEqual(MONITOR.read_notified([comment([candidate])]), {("grill-me", "a" * 64)})
        self.assertEqual(MONITOR.read_notified([comment([candidate], login="someone")]), set())
        self.assertEqual(MONITOR.read_notified([{"user": {"login": "github-actions[bot]"}, "body": "hello"}]), set())

    def test_corrupt_bot_receipt_is_a_state_error_not_an_empty_history(self):
        broken = comment([])
        broken["body"] = "<!-- upstream-monitor:v1\n{broken\n-->"
        with self.assertRaises(MONITOR.MonitorError):
            MONITOR.read_notified([broken])


class GitComparisonTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.upstream = self.root / "upstream"
        self.upstream.mkdir()
        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "Fixture")
        self.run_git("config", "user.email", "fixture@example.test")
        self.write("skill/SKILL.md", "initial skill\n")
        self.write("dependency/SKILL.md", "initial dependency\n")
        self.write("LICENSE", "MIT\n")
        self.write("outside.txt", "unrelated\n")
        self.base = self.commit()
        self.group = MONITOR.Group("fixture", str(self.upstream), "refs/heads/main", self.base,
                                   ("skill", "dependency"), ("LICENSE",))
        self.index = 0

    def run_git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.upstream, stderr=subprocess.DEVNULL).decode().strip()

    def write(self, path, text):
        target = self.upstream / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self):
        self.run_git("add", ".")
        self.run_git("commit", "--allow-empty", "-m", "fixture")
        return self.run_git("rev-parse", "HEAD")

    def check(self):
        self.index += 1
        repo = MONITOR.GitRepository(str(self.upstream), self.root / f"cache-{self.index}")
        return MONITOR.check_group(self.group, repo)

    def test_unrelated_commits_do_not_become_candidates(self):
        self.write("outside.txt", "new unrelated content\n")
        self.commit()
        self.assertEqual(self.check().status, "unchanged")

    def test_dependency_changes_are_grouped_and_unrelated_heads_keep_identity(self):
        self.write("dependency/SKILL.md", "changed behavior\n")
        self.commit()
        first = self.check()
        self.assertEqual(first.status, "new")
        self.assertEqual(first.files, ["dependency/SKILL.md"])
        self.assertIn("changed behavior", first.diff)
        self.write("outside.txt", "another unrelated commit\n")
        self.commit()
        second = self.check()
        self.assertNotEqual(first.head, second.head)
        self.assertEqual(first.fingerprint, second.fingerprint)

    def test_license_changes_are_candidates(self):
        self.write("LICENSE", "changed terms\n")
        self.commit()
        self.assertEqual(self.check().files, ["LICENSE"])

    def test_missing_required_path_is_failure(self):
        (self.upstream / "skill/SKILL.md").unlink()
        self.commit()
        with self.assertRaises(MONITOR.MonitorError):
            self.check()


class ConfigurationTest(unittest.TestCase):
    def test_existing_catalog_produces_four_groups_without_duplicate_skill_list(self):
        config = MONITOR.load_config(ROOT / "third-party/upstream-monitor.json")
        groups, failures = MONITOR.load_groups(lambda p: (ROOT / p).read_bytes(), config)
        self.assertEqual(failures, [])
        self.assertEqual({g.id for g in groups}, {"baoyu-design", "handoff", "grill-me", "show-me"})
        interview = next(g for g in groups if g.id == "grill-me")
        self.assertEqual(set(interview.skill_paths), {"skills/productivity/grill-me", "skills/productivity/grilling"})
        self.assertEqual(interview.license_paths, ("LICENSE",))

    def test_inconsistent_group_versions_only_block_the_affected_group(self):
        def read(path):
            data = (ROOT / path).read_bytes()
            if path == "third-party/grilling.upstream.json":
                record = json.loads(data)
                record["commit"] = "a" * 40
                return json.dumps(record)
            return data
        groups, failures = MONITOR.load_groups(read, MONITOR.load_config(ROOT / "third-party/upstream-monitor.json"))
        self.assertEqual({g.id for g in groups}, {"baoyu-design", "handoff", "show-me"})
        self.assertEqual([scope for scope, _ in failures], ["grill-me"])

    def test_malformed_catalog_entry_does_not_skip_valid_groups(self):
        def read(path):
            data = (ROOT / path).read_bytes()
            if path == "distribution/catalog.json":
                catalog = json.loads(data)
                catalog["plugins"].insert(0, None)
                return json.dumps(catalog)
            return data
        groups, failures = MONITOR.load_groups(read, MONITOR.load_config(ROOT / "third-party/upstream-monitor.json"))
        self.assertEqual(len(groups), 4)
        self.assertTrue(failures)

    def test_malformed_dependency_configuration_is_reportable(self):
        config = json.loads((ROOT / "third-party/upstream-monitor.json").read_bytes())
        config["extra_paths"] = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config))
            with self.assertRaises(MONITOR.MonitorError):
                MONITOR.load_config(path)


class ServiceContractTest(unittest.TestCase):
    def test_github_history_reads_beyond_the_first_page(self):
        class API:
            def request(self, method, path, payload=None):
                if path.endswith("/issues/2"):
                    return {"state": "open", "locked": False}
                if path.endswith("page=1"):
                    return [{"body": "ordinary comment"} for _ in range(100)]
                if path.endswith("page=2"):
                    return [comment([{"group": "handoff", "fingerprint": "f" * 64}])]
                raise AssertionError(path)
        issue = MONITOR.GitHubIssue(API(), "owner/repo", 2)
        self.assertEqual(MONITOR.read_notified(issue.list_comments()), {("handoff", "f" * 64)})

    def model(self, content=None, finish_reason="stop"):
        if content is None:
            content = {"summary": "先澄清目标。", "changes": [{"path": "SKILL.md", "description": "新增澄清步骤。"}]}
        api = Mock(token="test-only-token")
        api.request.return_value = {"choices": [{"finish_reason": finish_reason, "message": {"content": json.dumps(content)}}]}
        config = MONITOR.load_config(ROOT / "third-party/upstream-monitor.json")["model"]
        return api, MONITOR.OpenRouterSummary(api, config)

    def test_model_request_has_cost_and_parameter_constraints(self):
        api, model = self.model()
        self.assertEqual(model("-old\n+new", ["SKILL.md"])["summary"], "先澄清目标。")
        payload = api.request.call_args.args[2]
        self.assertEqual(payload["model"], "deepseek/deepseek-v4-flash-0731")
        self.assertEqual(payload["reasoning"], {"enabled": False})
        self.assertEqual(payload["max_tokens"], 2000)
        self.assertTrue(payload["provider"]["require_parameters"])
        self.assertEqual(payload["provider"]["max_price"], {"prompt": 0.06, "completion": 0.18})
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])

    def test_oversized_diff_does_not_spend_money_on_partial_summary(self):
        api, model = self.model()
        with self.assertRaises(MONITOR.MonitorError):
            model("x" * 60001, ["SKILL.md"])
        api.request.assert_not_called()

    def test_incomplete_output_or_unknown_evidence_is_rejected(self):
        for api, model in [self.model(finish_reason="length"), self.model({"summary": "summary", "changes": [
                {"path": "not-in-diff.md", "description": "unsupported"}]})]:
            with self.subTest(api=api), self.assertRaises(MONITOR.MonitorError):
                model("diff", ["SKILL.md"])

    def test_malformed_choice_is_a_summary_failure(self):
        api, model = self.model()
        api.request.return_value = {"choices": [None]}
        with self.assertRaises(MONITOR.MonitorError):
            model("diff", ["SKILL.md"])

    def test_model_cannot_inject_mentions_or_notification_receipts(self):
        group = MONITOR.Group("handoff", "https://github.com/owner/repo", "refs/heads/main", "a" * 40, ("skill",), ("LICENSE",))
        result = MONITOR.Result(group, "new", "b" * 40, "c" * 64, ["skill/SKILL.md"], "diff",
                                summary={"summary": "@someone <!-- upstream-monitor:v1\n{}\n-->", "changes": []})
        report = MONITOR.Report("a" * 40, [result])
        body = MONITOR.render_comment(report, "", "test")
        self.assertEqual(body.count(MONITOR.MARKER), 1)
        self.assertNotIn("@someone", body)


if __name__ == "__main__":
    unittest.main()
