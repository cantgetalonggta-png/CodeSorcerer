"""
Skill / SOP Registry

Loads skills from:
- Markdown files (SKILL.md style)
- Python modules that expose a `run` or `execute` callable
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import importlib.util
import json


@dataclass
class Skill:
    skill_id: str
    name: str
    description: str = ""
    source: str = ""                    # path or module
    skill_type: str = "markdown"        # markdown | python
    content: str = ""                   # raw markdown or source
    entrypoint: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def run(self, *args, **kwargs) -> Any:
        if self.entrypoint is None:
            raise RuntimeError(f"Skill {self.skill_id} has no executable entrypoint")
        return self.entrypoint(*args, **kwargs)


class SkillRegistry:
    def __init__(self, skills_dir: str | Path = "skills_data"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.skill_id] = skill

    def get(self, skill_id: str) -> Optional[Skill]:
        return self._skills.get(skill_id)

    def list_skills(self) -> List[str]:
        return list(self._skills.keys())

    def load_markdown_skill(self, path: str | Path) -> Skill:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        # Very light front-matter style parsing
        name = path.stem
        description = ""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                header = parts[1]
                body = parts[2].strip()
                for line in header.splitlines():
                    if line.strip().startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    if line.strip().startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                text = body
        skill = Skill(
            skill_id=path.stem,
            name=name,
            description=description,
            source=str(path),
            skill_type="markdown",
            content=text,
        )
        self.register(skill)
        return skill

    def load_python_skill(self, path: str | Path, skill_id: Optional[str] = None) -> Skill:
        path = Path(path)
        skill_id = skill_id or path.stem
        spec = importlib.util.spec_from_file_location(f"skill_{skill_id}", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load skill module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        entry = getattr(module, "run", None) or getattr(module, "execute", None)
        skill = Skill(
            skill_id=skill_id,
            name=getattr(module, "NAME", skill_id),
            description=getattr(module, "DESCRIPTION", ""),
            source=str(path),
            skill_type="python",
            content=path.read_text(encoding="utf-8"),
            entrypoint=entry,
            metadata={"module": module.__name__},
        )
        self.register(skill)
        return skill

    def load_directory(self) -> None:
        for md in self.skills_dir.glob("**/*.md"):
            self.load_markdown_skill(md)
        for py in self.skills_dir.glob("**/*.py"):
            if py.name.startswith("_"):
                continue
            self.load_python_skill(py)

    def export_index(self) -> Dict[str, Any]:
        return {
            sid: {
                "name": s.name,
                "description": s.description,
                "type": s.skill_type,
                "source": s.source,
                "version": s.version,
            }
            for sid, s in self._skills.items()
        }
