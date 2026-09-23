from __future__ import annotations

import json
import os
import platform
import re
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen


class SecurityLabConnector:

    SAFE_COMMANDS = {
        "system_info",
        "network_info",
        "list_listening_services",
        "github_repo_audit",
    }

    def system_info(self) -> dict:
        return {
            "ok": True,
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "distribution": self._distribution(),
        }

    def _distribution(self) -> str:
        try:
            data = Path(
                "/etc/os-release"
            ).read_text(
                encoding="utf-8",
                errors="ignore"
            )

            for line in data.splitlines():
                if line.startswith("PRETTY_NAME="):
                    return line.split(
                        "=",
                        1
                    )[1].strip().strip('"')

        except Exception:
            pass

        return "Unknown"

    def network_info(self) -> dict:
        commands = [
            ["ip", "addr"],
            ["ip", "route"],
        ]

        output = {}

        for name, command in (
            ("addresses", commands[0]),
            ("routes", commands[1]),
        ):
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )

                output[name] = result.stdout[:12000]

            except Exception as e:
                output[name] = f"Unavailable: {e}"

        return {
            "ok": True,
            **output,
        }

    def list_listening_services(self) -> dict:
        try:
            result = subprocess.run(
                ["ss", "-lntup"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )

            return {
                "ok": result.returncode == 0,
                "output": result.stdout[:16000],
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
            }

    def github_repo_audit(
        self,
        repo_path: str
    ) -> dict:
        root = Path(repo_path).expanduser().resolve()

        if not root.exists() or not root.is_dir():
            return {
                "ok": False,
                "error": "Repository directory not found.",
            }

        git_dir = root / ".git"

        if not git_dir.exists():
            return {
                "ok": False,
                "error": "Not a Git repository.",
            }

        findings = []

        secret_patterns = {
            "private_key": re.compile(
                r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
            ),
            "api_key_assignment": re.compile(
                r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token)"
                r"\s*[:=]\s*['\"][^'\"]{12,}['\"]"
            ),
            "password_assignment": re.compile(
                r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]{8,}['\"]"
            ),
        }

        ignored = {
            ".git",
            "build",
            ".gradle",
            "__pycache__",
            "node_modules",
        }

        scanned = 0

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if any(
                part in ignored
                for part in path.parts
            ):
                continue

            try:
                if path.stat().st_size > 2_000_000:
                    continue

                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except Exception:
                continue

            scanned += 1

            for name, pattern in secret_patterns.items():
                if pattern.search(text):
                    findings.append({
                        "type": name,
                        "file": str(
                            path.relative_to(root)
                        ),
                    })

        return {
            "ok": True,
            "repository": str(root),
            "files_scanned": scanned,
            "potential_secret_findings": findings,
            "warning": (
                "Pattern matches require manual verification; "
                "this audit does not extract or transmit secrets."
            ),
        }

    def github_public_repo_info(
        self,
        owner: str,
        repo: str
    ) -> dict:
        owner = str(owner).strip()
        repo = str(repo).strip()

        if not re.fullmatch(
            r"[A-Za-z0-9_.-]+",
            owner
        ):
            return {
                "ok": False,
                "error": "Invalid owner."
            }

        if not re.fullmatch(
            r"[A-Za-z0-9_.-]+",
            repo
        ):
            return {
                "ok": False,
                "error": "Invalid repository."
            }

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}"
        )

        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "JARVIS-Security-Audit"
                }
            )

            with urlopen(
                request,
                timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            return {
                "ok": True,
                "name": data.get("full_name"),
                "private": data.get("private"),
                "default_branch": data.get(
                    "default_branch"
                ),
                "stars": data.get(
                    "stargazers_count"
                ),
                "open_issues": data.get(
                    "open_issues_count"
                ),
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
            }

    def run(
        self,
        action: str,
        **kwargs
    ) -> dict:
        action = str(action).strip()

        if action not in self.SAFE_COMMANDS:
            return {
                "ok": False,
                "error": "Action not allowed."
            }

        if action == "system_info":
            return self.system_info()

        if action == "network_info":
            return self.network_info()

        if action == "list_listening_services":
            return self.list_listening_services()

        if action == "github_repo_audit":
            return self.github_repo_audit(
                kwargs.get(
                    "repo_path",
                    "."
                )
            )

        return {
            "ok": False,
            "error": "Unsupported action."
        }
