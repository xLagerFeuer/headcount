#!/usr/bin/env python3
"""Verify that every `department:name` reference resolves, in the docs and in the skills.

Prose naming specific skills or plugin-native agents rots as components are renamed or consolidated.
This repository has already consolidated once, losing six capabilities in the process. A reference
to a component that no longer exists is a broken promise to a reader, and nothing else in the tree
catches it.

Skill bodies are checked as well as the documentation, per D32. They were unchecked until then,
and four of the references inside them were already broken — including one pointing at a skill
that had never existed. Skill files are where readers follow references from most, so the
argument for checking the docs applies to them with more force, not less.

Only tokens whose prefix is a real department directory are checked, so ordinary prose with a
colon in it is ignored rather than guessed at. A resolved token may name either a skill or a
plugin-native agent; both use the plugin-scoped `department:name` addressing form.
"""
import glob
import os
import re
import sys

DOCS = (
    ["README.md", "CONTRIBUTING.md"]
    + sorted(glob.glob("docs/**/*.md", recursive=True))
    + sorted(glob.glob("plugins/**/SKILL.md", recursive=True))
)
# `dept:name` inside backticks — the convention this repository uses for plugin-scoped components.
REF = re.compile(r"`([a-z][a-z0-9-]*):([a-z][a-z0-9-]*)`")


def main():
    departments = {
        os.path.basename(os.path.dirname(os.path.dirname(m)))
        for m in glob.glob("plugins/*/.claude-plugin/plugin.json")
    }
    if not departments:
        print("  no departments found — run from the repository root")
        return 1

    problems = []
    checked = 0
    for path in DOCS:
        if not os.path.exists(path):
            continue
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            for dept, name in REF.findall(line):
                if dept not in departments:
                    continue  # not a plugin-scoped reference, just prose with a colon
                checked += 1
                skill = f"plugins/{dept}/skills/{name}/SKILL.md"
                agent = f"plugins/{dept}/agents/{name}.md"
                if not (os.path.exists(skill) or os.path.exists(agent)):
                    problems.append(f"{path}:{n}: `{dept}:{name}` does not exist")

    for p in problems:
        print(f"  {p}")
    print(f"plugin references: {checked} checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
