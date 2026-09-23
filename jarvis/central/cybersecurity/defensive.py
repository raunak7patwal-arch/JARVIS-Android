from __future__ import annotations

import hashlib
import re
import socket
import ssl
from urllib.parse import urlparse


class CyberSecurity:

    SAFE_PORTS = (
        22, 53, 80, 443, 8080, 8443
    )

    SECURITY_HEADERS = (
        "strict-transport-security",
        "content-security-policy",
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
    )

    def password_audit(self, password: str) -> dict:
        password = str(password)

        score = 0
        checks = {
            "length": len(password) >= 12,
            "uppercase": bool(re.search(r"[A-Z]", password)),
            "lowercase": bool(re.search(r"[a-z]", password)),
            "digit": bool(re.search(r"\d", password)),
            "symbol": bool(re.search(r"[^A-Za-z0-9]", password)),
        }

        score = sum(checks.values())

        if score <= 2:
            level = "weak"
        elif score <= 4:
            level = "moderate"
        else:
            level = "strong"

        return {
            "level": level,
            "score": score,
            "checks": checks,
            "stored": False,
        }

    def url_audit(self, url: str) -> dict:
        parsed = urlparse(str(url))

        if parsed.scheme not in ("http", "https"):
            return {
                "ok": False,
                "error": "Only HTTP/HTTPS URLs are supported.",
            }

        return {
            "ok": True,
            "scheme": parsed.scheme,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "https": parsed.scheme == "https",
        }

    def dns_lookup(self, hostname: str) -> dict:
        hostname = str(hostname).strip()

        if not hostname:
            return {"ok": False, "error": "Hostname required."}

        try:
            addresses = sorted({
                item[4][0]
                for item in socket.getaddrinfo(
                    hostname,
                    None
                )
            })

            return {
                "ok": True,
                "hostname": hostname,
                "addresses": addresses,
            }

        except Exception as e:
            return {
                "ok": False,
                "hostname": hostname,
                "error": str(e),
            }

    def tls_audit(self, hostname: str, port: int = 443) -> dict:
        hostname = str(hostname).strip()

        try:
            context = ssl.create_default_context()

            with socket.create_connection(
                (hostname, int(port)),
                timeout=5
            ) as sock:

                with context.wrap_socket(
                    sock,
                    server_hostname=hostname
                ) as tls:

                    cert = tls.getpeercert()

                    return {
                        "ok": True,
                        "hostname": hostname,
                        "tls_version": tls.version(),
                        "cipher": tls.cipher()[0]
                        if tls.cipher()
                        else None,
                        "certificate_present": bool(cert),
                    }

        except Exception as e:
            return {
                "ok": False,
                "hostname": hostname,
                "error": str(e),
            }

    def hash_identifier(self, value: str) -> str:
        return hashlib.sha256(
            str(value).encode("utf-8")
        ).hexdigest()

    def security_report(
        self,
        target: str,
        *,
        dns=None,
        tls=None,
        password=None
    ) -> dict:

        report = {
            "target": str(target),
            "authorized_scope": True,
            "checks": {},
        }

        report["checks"]["url"] = self.url_audit(
            target
        )

        hostname = urlparse(
            str(target)
        ).hostname

        if hostname:
            report["checks"]["dns"] = (
                dns
                if dns is not None
                else self.dns_lookup(hostname)
            )

            if urlparse(str(target)).scheme == "https":
                report["checks"]["tls"] = (
                    tls
                    if tls is not None
                    else self.tls_audit(hostname)
                )

        if password is not None:
            report["checks"]["password"] = (
                self.password_audit(password)
            )

        return report
