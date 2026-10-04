"""Independent review repros converted to bounded negative fixtures."""

import io
import json
import zipfile
from test_workbench import Project
from ror2_workbench.contract import load, metadata
from ror2_workbench.core import Invalid, json_bytes, scan
from ror2_workbench.release import archive_bytes, collect


class ReviewRegressions(Project):
    def test_game_language_token_fields_are_not_credentials(self):
        scan(b'body.baseNameToken = "WORKBENCH_RECRUIT_NAME";', "code.cs")
        with self.assertRaises(Invalid):
            scan(json_bytes({"api_key":"X" * 30}), "metadata.json")

    def test_json_escaping_does_not_hide_personal_path_or_key(self):
        path = "C:" + chr(92) + "Users" + chr(92) + "fictional" + chr(92) + "private"
        for data in (json_bytes({"path":path}), json_bytes({"nested":[{"key":"sk-" + "X" * 30}]}), json.dumps({"path":path}).encode().replace(b"C", b"\\u0043")):
            with self.assertRaises(Invalid):
                scan(data, "synthetic-json")

    def test_private_json_manifest_never_packages(self):
        self.fixture()
        manifest = json.loads((self.root / "package/manifest.json").read_bytes())
        manifest["description"] = "C:" + chr(92) + "Users" + chr(92) + "fictional" + chr(92) + "private"
        (self.root / "package/manifest.json").write_bytes(json_bytes(manifest))
        self.pin()
        self.assertEqual(self.cli("check", "--release")[0], 2)
        self.assertEqual(self.cli("package", "--output", "dist/private.zip", "--receipt", "evidence/private.json")[0], 2)
        self.assertFalse((self.root / "dist/private.zip").exists())

    def test_json_scan_fails_closed_on_malformed_or_duplicate_keys(self):
        for data in (b'{"name":', b'{"a":1,"a":2}'):
            with self.assertRaises(Invalid):
                scan(data, "metadata.json")

    def test_archive_comment_trailer_prefix_and_entry_metadata_rejected(self):
        self.fixture()
        canonical = archive_bytes(collect(self.root, load(self.root)))
        secret = ("sk-" + "X" * 30).encode()
        stream = io.BytesIO(canonical)
        with zipfile.ZipFile(stream, "a") as archive:
            archive.comment = secret
        variants = (stream.getvalue(), canonical + secret, secret + canonical)
        for index, data in enumerate(variants):
            (self.root / "local/noncanonical.zip").write_bytes(data)
            self.assertEqual(self.cli("verify", "local/noncanonical.zip", "--receipt", "evidence/rejected-" + str(index) + ".json")[0], 2)

    def test_trimmed_unreviewed_license_and_provenance_rejected(self):
        self.fixture()
        original = load(self.root)
        for field, value in (("license", " unknown "), ("provenance", " TODO "), ("license", " UnReViEwEd\t")):
            import copy
            doc = copy.deepcopy(original)
            doc["files"][0][field] = value
            self.write_doc(doc)
            self.assertEqual(self.cli("check", "--release")[0], 2)

    def test_version_lexer_ignores_strings_and_comments(self):
        doc = load(self.root)
        prefix = 'namespace TestSurvivor { class Identity { '
        valid = 'const string Url = "https://example.invalid"; public const string Version = "0.1.0";'
        source = self.root / "mod/PluginIdentity.cs"
        for text in (valid, 'const string Note = @"fake ""const string Version = """"1.0.0"""";"""; const string Version = @"0.1.0";', 'const string Note = """const string Version = "9.9.9";"""; const string Version = "0.1.0";', '/* const string Version = "9.9.9"; */\nconst string Version = "0.1.0"; // other declaration ignored'):
            source.write_text(prefix + text + ' } }')
            metadata(self.root, doc)
        for text in ('const string Note = """const string Version = "0.1.0";""";', 'const string Note = @"const string Version = ""0.1.0"";";', 'const string Note = "const string Version = \\"0.1.0\\";";', '/* const string Version = "0.1.0"; */'):
            source.write_text(prefix + text + ' } }')
            with self.assertRaises(Invalid):
                metadata(self.root, doc)

    def test_unsupported_conditional_interpolation_fails_closed(self):
        for text in ('const string Note = $"value {1}"; const string Version = "0.1.0";', '#if false\nconst string Version = "0.1.0";\n#endif'):
            (self.root / "mod/PluginIdentity.cs").write_text(text)
            with self.assertRaises(Invalid):
                metadata(self.root, load(self.root))

    def test_instruction_and_dependency_lock_changes_invalidate_packet(self):
        _, prior = self.cli("packet")
        for name in ("AGENTS.md", "CLAUDE.md", "local/dependencies.lock.json"):
            with (self.root / name).open("a") as stream:
                stream.write("\n")
            code, changed = self.cli("packet")
            self.assertEqual(code, 0)
            self.assertNotEqual(prior["context_fingerprint"], changed["context_fingerprint"])
            prior = changed
