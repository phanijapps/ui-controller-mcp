from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class SafetyCheckResult:
    allowed: bool
    reason: str | None = None


class SafetyGuard:
    """Simple guard against obviously destructive inputs."""

    banned_patterns: tuple[re.Pattern[str], ...] = (
        re.compile(r"rm\s+-rf", re.IGNORECASE),
        re.compile(r"shutdown", re.IGNORECASE),
        re.compile(r"mkfs", re.IGNORECASE),
        re.compile(r"format\s+c:", re.IGNORECASE),
    )

    def __init__(self, allowed_launch_targets: Iterable[str] | None = None) -> None:
        self.allowed_launch_targets = {target.lower() for target in (allowed_launch_targets or [])}

    def validate_launch_target(self, target: str) -> SafetyCheckResult:
        normalized = target.strip().lower()
        for pattern in self.banned_patterns:
            if pattern.search(normalized):
                return SafetyCheckResult(False, f"Launch target failed safety check: pattern '{pattern.pattern}' disallowed")

        if self.allowed_launch_targets and normalized not in self.allowed_launch_targets:
            return SafetyCheckResult(False, "Launch target is not on the allow list")

        return SafetyCheckResult(True)

    def validate_text(self, text: str) -> SafetyCheckResult:
        normalized = text.strip().lower()
        for pattern in self.banned_patterns:
            if pattern.search(normalized):
                return SafetyCheckResult(False, "Text input failed safety check")
        return SafetyCheckResult(True)
