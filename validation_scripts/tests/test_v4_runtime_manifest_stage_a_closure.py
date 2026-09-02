from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/llm_prompts/v1/LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json"
START = "validation_scripts/stage_lineage_contract_check.py"


def module_path(module: str):
    if not isinstance(module, str) or not module.startswith("validation_scripts"):
        return None
    path = ROOT / (module.replace(".", "/") + ".py")
    return path.relative_to(ROOT).as_posix() if path.is_file() else None


def direct_deps(relative: str):
    path = ROOT / relative
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = module_path(alias.name)
                if resolved:
                    out.add(resolved)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            resolved = module_path(module)
            if resolved:
                out.add(resolved)
            if module == "validation_scripts":
                for alias in node.names:
                    resolved = module_path(f"validation_scripts.{alias.name}")
                    if resolved:
                        out.add(resolved)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "with_name"
            and node.args
        ):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.endswith(".py"):
                resolved_path = path.parent / arg.value
                if resolved_path.is_file():
                    out.add(resolved_path.relative_to(ROOT).as_posix())
    return out


def stage_a_closure():
    closure = set()
    stack = [START]
    while stack:
        relative = stack.pop()
        if relative in closure:
            continue
        if not (ROOT / relative).is_file():
            raise AssertionError(f"missing validator dependency: {relative}")
        closure.add(relative)
        stack.extend(sorted(direct_deps(relative) - closure))
    return closure


class TestV4RuntimeManifestStageAClosure(unittest.TestCase):
    def test_active_stage_a_validator_closure_is_machine_registered(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        registered = set(manifest["canonical_paths"]["validation_scripts"])
        missing = sorted(stage_a_closure() - registered)
        self.assertEqual(
            missing,
            [],
            f"unregistered active Stage A validator dependencies: {missing}",
        )


if __name__ == "__main__":
    unittest.main()
