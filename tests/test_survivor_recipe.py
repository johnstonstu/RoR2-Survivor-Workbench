"""Recipe safety/lock checks; these do not compile or certify native behavior."""

import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


class SurvivorRecipeTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1] / "examples/first-survivor"

    def test_no_deployment_target_and_exact_locked_references(self):
        project = ET.parse(self.root / "Mod/FirstSurvivor.csproj").getroot()
        self.assertFalse(project.findall("Target"))
        self.assertEqual(project.findtext("PropertyGroup/CopyLocalLockFileAssemblies"), "false")
        lock = json.loads((self.root / "Mod/packages.lock.json").read_bytes())
        graph = next(iter(lock["dependencies"].values()))
        for reference in project.findall("ItemGroup/PackageReference"):
            spec = reference.attrib["Version"]
            self.assertTrue(spec.startswith("[") and spec.endswith("]"))
            self.assertEqual(reference.attrib["PrivateAssets"], "all")
            self.assertEqual(graph[reference.attrib["Include"]]["resolved"], spec[1:-1])

    def test_package_allowlist_has_only_owned_plugin_binary(self):
        contract = json.loads((self.root / "workbench.json").read_bytes())
        binaries = [entry for entry in contract["files"] if entry["destination"].endswith(".dll")]
        self.assertEqual([entry["destination"] for entry in binaries], ["plugins/WorkbenchRecruit/WorkbenchRecruit.dll"])
        self.assertIn("Mod/packages.lock.json", contract["inputs"])
        self.assertIn("AGENTS.md", contract["inputs"])

    def test_first_slice_keeps_native_input_and_has_no_custom_state(self):
        source = (self.root / "Mod/RecruitContent.cs").read_text()
        self.assertIn("IContentPackProvider", source)
        self.assertIn("PrefabAPI.InstantiateClone", source)
        for forbidden in ("Input.GetKey", "KeyCode.", "Input.GetAxis", "RegisterNetworkPrefab", "AssetBundle.Load", "Camera.main", "NetworkServer.Spawn"):
            self.assertNotIn(forbidden, source)
