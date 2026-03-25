#!/usr/bin/env python3
"""Tier 1: Static validation of agent skills and guidance docs.

Checks structural correctness, cross-references, and file existence.
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

_EVAL_EXEMPT_SKILLS: frozenset[str] = frozenset({"eval-skills"})


@dataclass
class MdFile:
    path: Path

    @cached_property
    def _content(self) -> str:
        return self.path.read_text()

    @cached_property
    def make_targets(self) -> frozenset[str]:
        return frozenset(re.findall(r"`make ([a-z][a-z0-9_-]*)`", self._content))

    @cached_property
    def shell_scripts(self) -> frozenset[str]:
        # Skip lines with shell variable expansions (${...}) to avoid false positives
        lines = "\n".join(line for line in self._content.splitlines() if "${" not in line)
        return frozenset(re.findall(r"scripts/[a-z][a-z0-9_.-]*\.sh", lines))

    @cached_property
    def doc_references(self) -> frozenset[str]:
        return frozenset(re.findall(r"`(docs/[a-z][a-z0-9_/-]*\.(?:md|txt))`", self._content))

    @cached_property
    def has_top_level_heading(self) -> bool:
        return bool(re.search(r"^# ", self._content, re.MULTILINE))

    @cached_property
    def has_steps_section(self) -> bool:
        return bool(re.search(r"^## Steps|^### \d|^## .+ checklist", self._content, re.MULTILINE))

    @cached_property
    def frontmatter(self) -> dict[str, str]:
        """Parse YAML-style frontmatter between leading --- delimiters into a flat dict."""
        m = re.match(r"^---\n(.*?)\n---\n", self._content, re.DOTALL)
        if not m:
            return {}
        result: dict[str, str] = {}
        for line in m.group(1).splitlines():
            if ": " in line:
                key, _, value = line.partition(": ")
                result[key.strip()] = value.strip()
        return result


@dataclass
class ClaudeDir:
    root: Path

    @property
    def path(self) -> Path:
        return self.root / ".claude"

    @cached_property
    def skill_dirs(self) -> list[Path]:
        """Sorted list of every skill directory under .claude/skills/."""
        return [d for d in sorted((self.path / "skills").iterdir()) if d.is_dir()]

    @cached_property
    def skill_files(self) -> list[MdFile]:
        """MdFile for each SKILL.md that exists inside a skill directory."""
        return [MdFile(d / "SKILL.md") for d in self.skill_dirs if (d / "SKILL.md").is_file()]

    @cached_property
    def agent_files(self) -> list[MdFile]:
        """MdFile for each agent definition (.md) under .claude/agents/."""
        agents_dir = self.path / "agents"
        if not agents_dir.is_dir():
            return []
        return [MdFile(f) for f in sorted(agents_dir.glob("*.md"))]


# ---------- 1. SKILL.md structure ----------


def validate_skill_structure(claude: ClaudeDir) -> list[str]:
    errors = []
    for skill_dir in claude.skill_dirs:
        skill_name = skill_dir.name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.is_file():
            errors.append(f"Skill '{skill_name}' has no SKILL.md")
            continue

        md = MdFile(skill_file)

        fm = md.frontmatter
        if not fm:
            errors.append(f"{skill_name}/SKILL.md missing YAML frontmatter (--- block)")
        else:
            for field in ("name", "description"):
                if field not in fm:
                    errors.append(f"{skill_name}/SKILL.md frontmatter missing required field '{field}'")
            if fm.get("name") and fm["name"] != skill_name:
                errors.append(f"{skill_name}/SKILL.md frontmatter 'name' ({fm['name']!r}) does not match directory name")

        if not md.has_top_level_heading:
            errors.append(f"{skill_name}/SKILL.md missing top-level heading (# Title)")

        if not md.has_steps_section:
            errors.append(f"{skill_name}/SKILL.md missing '## Steps', numbered step sections, or checklist sections")

    return errors


# ---------- 2. Make target existence ----------


def _make_target_exists(target: str, makefile_content: str) -> bool:
    return bool(re.search(rf"^{re.escape(target)}:", makefile_content, re.MULTILINE))


def validate_make_targets(claude: ClaudeDir) -> list[str]:
    errors = []
    makefile = claude.root / "Makefile"
    if not makefile.is_file():
        return errors
    makefile_content = makefile.read_text()

    for md in claude.skill_files:
        skill_name = md.path.parent.name
        for target in sorted(md.make_targets):
            if not _make_target_exists(target, makefile_content):
                errors.append(f"Make target '{target}' referenced in {skill_name}/SKILL.md does not exist in Makefile")

    claude_file = claude.root / "CLAUDE.md"
    if claude_file.is_file():
        for target in sorted(MdFile(claude_file).make_targets):
            if not _make_target_exists(target, makefile_content):
                errors.append(f"Make target '{target}' referenced in CLAUDE.md does not exist in Makefile")

    return errors


# ---------- 3. Script existence ----------


def validate_scripts(claude: ClaudeDir) -> list[str]:
    errors = []
    for md in claude.skill_files:
        skill_name = md.path.parent.name
        for script in sorted(md.shell_scripts):
            script_path = claude.root / script
            if not script_path.is_file():
                errors.append(f"Script '{script}' referenced in {skill_name}/SKILL.md does not exist")
            elif not os.access(script_path, os.X_OK):
                errors.append(f"Script '{script}' referenced in {skill_name}/SKILL.md is not executable")

    return errors


# ---------- 4. Cross-doc consistency ----------


def validate_doc_references(claude: ClaudeDir) -> list[str]:
    errors = []
    claude_file = claude.root / "CLAUDE.md"
    if not claude_file.is_file():
        return errors
    for doc in sorted(MdFile(claude_file).doc_references):
        if not (claude.root / doc).is_file():
            errors.append(f"Doc '{doc}' referenced in CLAUDE.md does not exist")
    return errors


# ---------- 5. Eval files ----------


def validate_eval_files(
    claude: ClaudeDir,
    exempt_skills: frozenset[str] = _EVAL_EXEMPT_SKILLS,
) -> list[str]:
    errors = []
    for skill_dir in claude.skill_dirs:
        skill_name = skill_dir.name
        eval_file = skill_dir / "evals" / "evals.json"

        if eval_file.is_file():
            try:
                json.loads(eval_file.read_text())
            except json.JSONDecodeError as e:
                errors.append(f"{skill_name}/evals/evals.json is not valid JSON: {e}")
        elif skill_name not in exempt_skills:
            errors.append(f"Skill '{skill_name}' is missing evals/evals.json — add eval test cases")

    return errors


# ---------- Main ----------


def main() -> None:
    root = Path(__file__).parent.parent
    claude = ClaudeDir(root)
    errors = [
        *validate_skill_structure(claude),
        *validate_make_targets(claude),
        *validate_scripts(claude),
        *validate_doc_references(claude),
        *validate_eval_files(claude),
    ]
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"\nAgent guidance validation failed with {len(errors)} error(s).", file=sys.stderr)
        sys.exit(1)

    print("Agent guidance validation passed.")


if __name__ == "__main__":
    main()
