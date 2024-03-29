from __future__ import annotations

import enum
import os
import uuid
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from pdm.core import Core
    from pdm.models.candidates import Candidate
    from pdm.project import Project


class Sign(enum.Enum):
    NEW = ":heavy_plus_sign:"
    UPDATE = ":arrow_up:"
    REMOVE = ":heavy_minus_sign:"


class SummaryRow(NamedTuple):
    sign: Sign
    name: str
    before: str | None
    after: str | None


def set_multiline_output(name, value):
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)


class UpdateSummarizer:
    before_candidates: dict[str, Candidate]

    def __init__(self, core: Core) -> None:
        from pdm.signals import post_lock, pre_lock

        pre_lock.connect(self.before_lock, weak=False)
        post_lock.connect(self.post_lock, weak=False)

    @staticmethod
    def pre(s: str | None) -> str:
        if not s:
            return ""
        return f"`{s}`"

    def before_lock(self, project: Project, **_kwds: Any) -> None:
        """Hook before locking the project."""
        self.before_candidates = project.locked_repository.all_candidates

    def get_update_summary(self, project: Project) -> str:
        """Get the update summary message."""
        after_candidates = project.locked_repository.all_candidates
        before_candidates = self.before_candidates
        rows: list[SummaryRow] = []

        for name, after in after_candidates.items():
            before = before_candidates.pop(name, None)
            if before is None:
                rows.append(
                    SummaryRow(
                        Sign.NEW, name, None, after.version or after.link.redacted
                    )
                )
            else:
                before_version = before.version or before.link.redacted
                after_version = after.version or after.link.redacted
                if before_version != after_version:
                    rows.append(
                        SummaryRow(Sign.UPDATE, name, before_version, after_version)
                    )

        for name, before in before_candidates.items():
            rows.append(
                SummaryRow(
                    Sign.REMOVE, name, before.version or before.link.redacted, None
                )
            )

        texts = [
            f"There are {len(rows)} updates:\n",
            "| | Package | From | To |",
            "| --- | --- | --- | --- |",
        ]

        for row in rows:
            texts.append(
                f"| {row.sign.value} | [{row.name}](https://pypi.org/project/{row.name}) "
                f"| {self.pre(row.before)} | {self.pre(row.after)} |"
            )

        return "\n".join(texts)

    def post_lock(self, project: Project, **_kwds: Any) -> None:
        """Hook after locking the project."""
        summary = self.get_update_summary(project)

        print("Update Summary")
        print("==============")
        print(summary)

        assert "GITHUB_OUTPUT" in os.environ, "This action should only run in GitHub"
        set_multiline_output("SUMMARY", summary)
