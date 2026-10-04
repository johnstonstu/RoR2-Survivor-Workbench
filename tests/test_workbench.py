"""Meaningful guards against broken/private releases and dishonest results."""

import contextlib
import copy
import io
import json
import struct
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile
import zlib
from pathlib import Path

from ror2_workbench.__main__ import main
from ror2_workbench.contract import load, metadata, task
from ror2_workbench.core import Invalid, digest, json_bytes, local, parse_json, read_json, relative, scan
from ror2_workbench.evidence import git_identity, identity, record
from ror2_workbench.release import archive_bytes, candidate, collect, icon, verify_bytes
from ror2_workbench.starter import create, png


class Project(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ror2-workbench-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        create(self.root, "TestSurvivor")

    def write_doc(self, doc):
        (self.root / "workbench.json").write_bytes(json_bytes(doc))

    def fixture(self):
        doc = load(self.root)
        doc["mode"] = "fixture"
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts/payload.txt").write_text("Synthetic owned payload.\n")
        doc["files"].append({"source":"artifacts/payload.txt", "destination":"plugins/TestSurvivor/payload.txt", "sha256":None, "license":"MIT", "provenance":"Original synthetic fixture"})
        self.write_doc(doc)
        self.pin()
        return load(self.root)

    def pin(self):
        doc = load(self.root)
        for entry in doc["files"]:
            entry["sha256"] = digest((self.root / entry["source"]).read_bytes())
        self.write_doc(doc)

    def cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([*args, "--root", str(self.root)])
        return code, json.loads(out.getvalue())

    def operator_result(self):
        doc = self.fixture()
        (self.root / "local/run.log").write_text("Current semantic assertions: 3 passed. Terminal scenario complete.\n")
        result = {"schema":1, "task_id":"first-skill", "input_hashes":identity(self.root, doc),
                  "tool_versions":{"synthetic-harness":"1.0"}, "limitations":["No native game validation."],
                  "checks":[{"id":"semantic", "level":"offline", "status":"passed", "terminal":True,
                             "exit_code":0, "assertions":3, "full_log_review":"passed", "log":"local/run.log", "observations":"Synthetic current assertions passed."}]}
        (self.root / "local/result.json").write_bytes(json_bytes(result))
        return result


class ContractTests(Project):
    def test_packet_is_bounded_current_and_invalidates_after_source_change(self):
        code, packet = self.cli("packet")
        self.assertEqual(code, 0)
        self.assertNotIn("source_text", packet)
        self.assertIn("goal", packet["context"]["task"])
        with (self.root / "mod/PluginIdentity.cs").open("a") as stream:
            stream.write("// Relevant input changed.\n")
        code, changed = self.cli("packet")
        self.assertEqual(code, 0)
        self.assertNotEqual(changed["context_fingerprint"], packet["context_fingerprint"])
        self.assertEqual(self.cli("packet", "--max-bytes", "1000")[0], 2)

    def test_new_scaffold_metadata_passes_but_release_fails(self):
        self.assertEqual(self.cli("check")[0], 0)
        self.assertEqual(self.cli("check", "--release")[0], 2)

    def test_init_never_overwrites(self):
        before = (self.root / "workbench.json").read_bytes()
        with self.assertRaises(Invalid):
            create(self.root, "Other")
        self.assertEqual((self.root / "workbench.json").read_bytes(), before)

    def test_manifest_version_mismatch_rejected(self):
        value = read_json(self.root / "package/manifest.json")
        value["version_number"] = "0.2.0"
        (self.root / "package/manifest.json").write_bytes(json_bytes(value))
        with self.assertRaises(Invalid):
            metadata(self.root, load(self.root))

    def test_prerelease_and_boolean_schema_rejected(self):
        for field, value in (("schema", True), ("identity", {"name":"TestSurvivor", "version":"1.0.0-beta"})):
            with self.subTest(field=field):
                doc = load(self.root)
                doc[field] = value
                self.write_doc(doc)
                with self.assertRaises(Invalid):
                    load(self.root)
                create_doc = doc
                create_doc["schema"] = 1
                create_doc["identity"] = {"name":"TestSurvivor", "version":"0.1.0"}
                self.write_doc(create_doc)

    def test_unknown_and_duplicate_json_fields_rejected(self):
        doc = load(self.root)
        doc["execute"] = "not a command runner"
        self.write_doc(doc)
        with self.assertRaises(Invalid):
            load(self.root)
        (self.root / "workbench.json").write_text('{"schema":1,"schema":1}')
        with self.assertRaises(Invalid):
            read_json(self.root / "workbench.json")

    def test_duplicate_case_and_prefix_destinations_rejected(self):
        original = load(self.root)
        for destination in ("README.md", "readme.md", "README.md/child.txt"):
            doc = copy.deepcopy(original)
            extra = copy.deepcopy(doc["files"][0])
            extra["destination"] = destination
            doc["files"].append(extra)
            self.write_doc(doc)
            with self.assertRaises(Invalid):
                load(self.root)

    def test_exact_dependencies_not_floating(self):
        for value in (["Author-Mod-latest"], ["Author-Mod-1.0.0", "Author-Mod-1.0.0"], "Author-Mod-1.0.0"):
            manifest = read_json(self.root / "package/manifest.json")
            manifest["dependencies"] = value
            (self.root / "package/manifest.json").write_bytes(json_bytes(manifest))
            with self.assertRaises(Invalid):
                metadata(self.root, load(self.root))

    def test_mod_requires_real_output_declaration_and_dependencies(self):
        doc = load(self.root)
        doc["mode"] = "mod"
        self.write_doc(doc)
        with self.assertRaises(Invalid):
            metadata(self.root, doc)
        manifest = read_json(self.root / "package/manifest.json")
        manifest["dependencies"] = ["Example-Loader-1.0.0"]
        (self.root / "package/manifest.json").write_bytes(json_bytes(manifest))
        with self.assertRaises(Invalid):
            metadata(self.root, doc)

    def test_commented_or_duplicate_version_is_not_identity(self):
        for source in ('// const string Version = "0.1.0";', 'const string Version = "0.1.0"; const string Version = "0.1.0";'):
            (self.root / "mod/PluginIdentity.cs").write_text(source)
            with self.assertRaises(Invalid):
                metadata(self.root, load(self.root))

    def test_done_task_with_pending_acceptance_fails(self):
        doc = load(self.root)
        value = read_json(self.root / "local/task.json")
        value["status"] = "done"
        (self.root / "local/task.json").write_bytes(json_bytes(value))
        with self.assertRaises(Invalid):
            task(self.root, doc)

    def test_passed_task_requires_evidence(self):
        value = read_json(self.root / "local/task.json")
        value["acceptance"][0]["status"] = "passed"
        (self.root / "local/task.json").write_bytes(json_bytes(value))
        with self.assertRaises(Invalid):
            task(self.root, load(self.root))


class SafetyTests(Project):
    def test_paths_reject_traversal_platform_hazards(self):
        for name in ("../outside", "/absolute", "a\\b", "a//b", "a/./b", "a:b", "a./b", "CON.txt", "a/NUL", "a?b", "a/*"):
            with self.subTest(name=name), self.assertRaises(Invalid):
                relative(name)

    def test_input_symlink_rejected(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("Do not read or ship this.")
        link = self.root / "linked.txt"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Host does not permit symlink creation; planned Linux CI can run this case.")
        with self.assertRaises(Invalid):
            local(self.root, "linked.txt")

    def test_prohibited_files_rejected_even_if_allowlisted(self):
        original = load(self.root)
        for destination in ("plugins/RoR2.dll", "plugins/UnityEngine.CoreModule.dll", "plugins/R2API.Core.dll", "plugins/SoundBanks/INIT.bnk", "plugins/asset.unitypackage", ".env", "plugins/trace.pdb"):
            with self.subTest(destination=destination):
                doc = copy.deepcopy(original)
                item = copy.deepcopy(doc["files"][0])
                item["destination"] = destination
                doc["files"].append(item)
                self.write_doc(doc)
                with self.assertRaises(Invalid):
                    load(self.root)

    def test_secret_and_personal_paths_in_utf8_and_utf16(self):
        path = "C:" + chr(92) + "Users" + chr(92) + "fictional" + chr(92) + "file"
        values = (path, "sk-" + "X" * 30, "api_key=" + "X" * 30, "-----BEGIN " + "PRIVATE KEY-----")
        for value in values:
            for encoding in ("utf-8", "utf-16-le"):
                with self.subTest(encoding=encoding), self.assertRaises(Invalid):
                    scan(value.encode(encoding), "synthetic")

    def test_stale_input_pin_and_unknown_license_block_release(self):
        doc = self.fixture()
        (self.root / "artifacts/payload.txt").write_text("Changed output.")
        with self.assertRaises(Invalid):
            candidate(self.root)
        self.pin()
        doc = load(self.root)
        doc["files"][-1]["license"] = "unknown"
        self.write_doc(doc)
        with self.assertRaises(Invalid):
            candidate(self.root)

    def test_png_truncation_crc_and_missing_pixels_rejected(self):
        good = png()
        bad_crc = bytearray(good)
        bad_crc[30] ^= 1
        no_pixels = good[:33] + good[-12:]
        for data in (good[:24], bytes(bad_crc), no_pixels, b"not a PNG"):
            with self.assertRaises(Invalid):
                icon(data)
        icon(good)

    def test_png_wrong_dimensions_even_with_valid_crc(self):
        data = bytearray(png())
        data[16:20] = struct.pack(">I", 128)
        data[29:33] = struct.pack(">I", zlib.crc32(data[12:29]))
        with self.assertRaises(Invalid):
            icon(bytes(data))


class PackageTests(Project):
    def test_archive_receipt_ancestor_collision_writes_nothing(self):
        self.fixture()
        for archive, receipt in (("dist/review.zip", "dist/review.zip/receipt.json"), ("dist/receipt.json/review.zip", "dist/receipt.json")):
            with self.subTest(archive=archive):
                self.assertEqual(self.cli("package", "--output", archive, "--receipt", receipt)[0], 2)
                self.assertFalse((self.root / "dist").exists())

    def test_existing_file_parent_writes_nothing(self):
        self.fixture()
        (self.root / "local/not-directory").write_text("Keep this file.")
        self.assertEqual(self.cli("package", "--output", "dist/review.zip", "--receipt", "local/not-directory/receipt.json")[0], 2)
        self.assertFalse((self.root / "dist").exists())

    def test_concurrent_input_change_prevents_outputs(self):
        self.fixture()
        original = archive_bytes
        def change_input(files):
            archive = original(files)
            (self.root / "artifacts/payload.txt").write_text("Changed during collection.")
            return archive
        with patch("ror2_workbench.__main__.archive_bytes", side_effect=change_input):
            self.assertEqual(self.cli("package", "--output", "dist/review.zip", "--receipt", "evidence/review.json")[0], 2)
        self.assertFalse((self.root / "dist/review.zip").exists())
        self.assertFalse((self.root / "evidence/review.json").exists())

    def test_unsupported_zip_compression_is_safe_failure(self):
        self.fixture()
        files = collect(self.root, load(self.root))
        data = bytearray(archive_bytes(files))
        for signature, method_offset in ((b"PK\x03\x04", 8), (b"PK\x01\x02", 10)):
            at = data.find(signature)
            data[at + method_offset:at + method_offset + 2] = struct.pack("<H", 99)
        (self.root / "local/unsupported.zip").write_bytes(data)
        code, result = self.cli("verify", "local/unsupported.zip", "--receipt", "evidence/unsupported.json")
        self.assertEqual(code, 2)
        self.assertFalse(result["passed"])
        self.assertFalse((self.root / "evidence/unsupported.json").exists())

    def test_nul_zip_member_is_rejected(self):
        files = collect(self.root, self.fixture())
        data = archive_bytes(files).replace(b"plugins/TestSurvivor/payload.txt", b"plugins/TestSurvivor/payloa\x00.txt")
        with self.assertRaises(Invalid):
            verify_bytes(data, files)

    def test_exact_round_trip_is_deterministic(self):
        doc = self.fixture()
        files = collect(self.root, doc)
        one = archive_bytes(files)
        self.assertEqual(one, archive_bytes(files))
        entries = verify_bytes(one, files)
        self.assertEqual(entries["plugins/TestSurvivor/payload.txt"]["sha256"], digest(files["plugins/TestSurvivor/payload.txt"]))

    def test_missing_extra_wrapper_and_separator_rejected(self):
        doc = self.fixture()
        files = collect(self.root, doc)
        variants = [{k:v for k,v in files.items() if k != "README.md"},
                    {**files, "unexpected.txt":b"unexpected"},
                    {"wrapped/" + k:v for k,v in files.items()}]
        for variant in variants:
            with self.assertRaises(Invalid):
                verify_bytes(archive_bytes(variant), files)
        # ZipInfo normalizes os.sep on Windows. Mutate both stored names instead
        # so this archive actually contains the bad separator being tested.
        bad_names = archive_bytes(files).replace(b"plugins/TestSurvivor/payload.txt", b"plugins\\TestSurvivor\\payload.txt")
        with self.assertRaises(Invalid):
            verify_bytes(bad_names, files)

    def test_changed_zip_payload_is_rejected(self):
        files = collect(self.root, self.fixture())
        changed = dict(files)
        changed["README.md"] = b"x" * len(files["README.md"])
        with self.assertRaises(Invalid):
            verify_bytes(archive_bytes(changed), files)

    def test_symlink_zip_entry_rejected_without_extraction(self):
        files = collect(self.root, self.fixture())
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            for name, payload in files.items():
                entry = zipfile.ZipInfo(name)
                entry.create_system = 3
                entry.external_attr = 0o120777 << 16
                archive.writestr(entry, payload)
        with self.assertRaises(Invalid):
            verify_bytes(stream.getvalue(), files)

    def test_duplicate_zip_entry_rejected(self):
        files = collect(self.root, self.fixture())
        stream = io.BytesIO(archive_bytes(files))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(stream, "a") as archive:
                archive.writestr("README.md", files["README.md"])
        with self.assertRaises(Invalid):
            verify_bytes(stream.getvalue(), files)

    def test_package_and_verify_cli_do_not_overwrite(self):
        self.fixture()
        self.assertEqual(self.cli("package", "--output", "dist/review.zip", "--receipt", "evidence/package.json")[0], 0)
        archive = (self.root / "dist/review.zip").read_bytes()
        self.assertEqual(self.cli("verify", "dist/review.zip", "--receipt", "evidence/verify.json")[0], 0)
        self.assertEqual(self.cli("package", "--output", "dist/review.zip", "--receipt", "evidence/new.json")[0], 2)
        self.assertEqual((self.root / "dist/review.zip").read_bytes(), archive)
        self.assertFalse((self.root / "evidence/new.json").exists())
        self.assertEqual(self.cli("package", "--output", "dist/other.zip", "--receipt", "evidence/package.json")[0], 2)
        self.assertFalse((self.root / "dist/other.zip").exists())

    def test_pin_writes_candidate_without_modifying_contract(self):
        before = (self.root / "workbench.json").read_bytes()
        self.assertEqual(self.cli("pin")[0], 0)
        self.assertEqual((self.root / "workbench.json").read_bytes(), before)
        proposed = read_json(self.root / "local/workbench.pinned.json")
        self.assertTrue(all(f["sha256"] for f in proposed["files"]))
        self.assertEqual(self.cli("pin")[0], 2)


class EvidenceTests(Project):
    def test_result_is_parsed_from_the_scanned_snapshot(self):
        original = self.operator_result()
        raw = (self.root / "local/result.json").read_bytes()
        def replace_after_read(captured):
            changed = copy.deepcopy(original)
            changed["checks"][0]["observations"] = "Different later observation."
            (self.root / "local/result.json").write_bytes(json_bytes(changed))
            return parse_json(captured)
        with patch("ror2_workbench.evidence.parse_json", side_effect=replace_after_read):
            result = record(self.root, "local/result.json")
        self.assertEqual(result["checks"][0]["observations"], original["checks"][0]["observations"])
        self.assertEqual(result["result_sha256"], digest(raw))

    def test_git_observation_disables_optional_writes_and_monitor(self):
        observed = []
        class Response:
            returncode = 0
            stdout = ""
        def fake_run(args, **kwargs):
            observed.append(args)
            response = Response()
            if args[-1] == "--show-toplevel":
                response.stdout = str(self.root)
            elif args[-1] == "HEAD":
                response.stdout = "a" * 40
            return response
        with patch("ror2_workbench.evidence.subprocess.run", side_effect=fake_run):
            self.assertEqual(git_identity(self.root)["commit"], "a" * 40)
        self.assertEqual(len(observed), 3)
        for command in observed:
            self.assertIn("--no-optional-locks", command)
            self.assertIn("core.fsmonitor=false", command)

    def test_receipt_binds_current_bytes_and_preserves_level(self):
        self.operator_result()
        result = record(self.root, "local/result.json")
        self.assertEqual(result["checks"][0]["level"], "offline")
        self.assertEqual(result["runtime_compatibility"], "unverified")
        self.assertEqual(len(result["checks"][0]["log_sha256"]), 64)
        self.assertNotIn("Current semantic assertions", json.dumps(result))

    def test_incomplete_or_failed_review_cannot_be_passed(self):
        result = self.operator_result()
        for field, value in (("terminal", False), ("assertions", 0), ("exit_code", 1), ("full_log_review", "failed"), ("log", None), ("status", "waived")):
            with self.subTest(field=field):
                altered = copy.deepcopy(result)
                altered["checks"][0][field] = value
                (self.root / "local/result.json").write_bytes(json_bytes(altered))
                with self.assertRaises(Invalid):
                    record(self.root, "local/result.json")

    def test_stale_identity_rejected(self):
        self.operator_result()
        with (self.root / "mod/PluginIdentity.cs").open("a") as stream:
            stream.write("// Current code changed.\n")
        with self.assertRaises(Invalid):
            record(self.root, "local/result.json")

    def test_failed_result_saved_with_failure_exit(self):
        result = self.operator_result()
        result["checks"][0].update(status="failed", terminal=False, full_log_review="failed")
        (self.root / "local/result.json").write_bytes(json_bytes(result))
        code, value = self.cli("record", "local/result.json", "--receipt", "evidence/failed.json")
        self.assertEqual(code, 1)
        self.assertFalse(value["all_reported_checks_passed"])
        receipt = read_json(self.root / "evidence/failed.json")
        self.assertEqual(receipt["checks"][0]["status"], "failed")

    def test_secret_log_is_not_recorded_or_echoed(self):
        self.operator_result()
        secret = "sk-" + "X" * 30
        (self.root / "local/run.log").write_text(secret)
        code, value = self.cli("record", "local/result.json", "--receipt", "evidence/private.json")
        self.assertEqual(code, 2)
        self.assertNotIn(secret, json.dumps(value))
        self.assertFalse((self.root / "evidence/private.json").exists())


if __name__ == "__main__":
    unittest.main()
