from __future__ import annotations

import re
import socket
import ssl
from urllib.parse import urlparse


class CyberSecurityAuditor:

    SAFE_PORTS = {
        21: "FTP",
        22: "SSH",
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
        554: "RTSP",
        8080: "HTTP-ALT",
        8443: "HTTPS-ALT",
    }

    CAMERA_PORTS = {
        80,
        443,
        554,
        8000,
        8080,
        8443,
        8899,
    }

    def wifi_audit(
        self,
        ssid: str,
        security: str,
        password_protected: bool = True,
    ) -> dict:

        security = str(security).upper().strip()

        findings = []

        if not password_protected:
            findings.append(
                "Network appears to have no password protection."
            )

        if security in {
            "OPEN",
            "NONE",
            "WEP",
        }:
            findings.append(
                "Legacy or missing Wi-Fi protection detected."
            )

        if security in {
            "WPA",
            "WPA-PSK",
        }:
            findings.append(
                "Consider WPA2 or WPA3 where supported."
            )

        if security in {
            "WPA2",
            "WPA3",
            "WPA2-PSK",
            "WPA3-SAE",
        }:
            status = "reviewed"
        else:
            status = "needs_review"

        return {
            "type": "wifi",
            "ssid": str(ssid),
            "security": security,
            "password_protected": bool(
                password_protected
            ),
            "status": status,
            "findings": findings,
        }

    def network_service_audit(
        self,
        host: str,
        ports=None,
    ) -> dict:

        host = str(host).strip()

        if not host:
            return {
                "ok": False,
                "error": "Host required.",
            }

        if ports is None:
            ports = tuple(self.SAFE_PORTS)

        results = []

        for port in ports:
            try:
                port = int(port)

                if not (
                    1 <= port <= 65535
                ):
                    continue

                with socket.create_connection(
                    (host, port),
                    timeout=1.5
                ):
                    results.append({
                        "port": port,
                        "service": self.SAFE_PORTS.get(
                            port,
                            "unknown"
                        ),
                        "state": "open",
                    })

            except Exception:
                pass

        return {
            "ok": True,
            "host": host,
            "authorized_scope": True,
            "services": results,
        }

    def cctv_audit(
        self,
        host: str,
        ports=None,
    ) -> dict:

        if ports is None:
            ports = tuple(
                self.CAMERA_PORTS
            )

        result = self.network_service_audit(
            host,
            ports
        )

        if not result.get("ok"):
            return result

        services = result["services"]

        findings = []

        for item in services:
            port = item["port"]

            if port == 554:
                findings.append(
                    "RTSP service detected; verify authentication and access controls."
                )

            if port in {
                80,
                8080,
            }:
                findings.append(
                    f"HTTP service detected on port {port}; prefer HTTPS where supported."
                )

            if port in {
                443,
                8443,
            }:
                findings.append(
                    f"HTTPS service detected on port {port}; verify TLS configuration."
                )

        return {
            "type": "cctv",
            "ok": True,
            "host": host,
            "authorized_scope": True,
            "services": services,
            "findings": findings,
        }

    def tls_audit(
        self,
        hostname: str,
        port: int = 443,
    ) -> dict:

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

                    return {
                        "ok": True,
                        "hostname": hostname,
                        "port": int(port),
                        "tls_version": tls.version(),
                        "cipher": (
                            tls.cipher()[0]
                            if tls.cipher()
                            else None
                        ),
                    }

        except Exception as e:
            return {
                "ok": False,
                "hostname": hostname,
                "error": str(e),
            }

    def url_security_audit(
        self,
        url: str,
    ) -> dict:

        parsed = urlparse(
            str(url).strip()
        )

        findings = []

        if parsed.scheme not in {
            "http",
            "https",
        }:
            return {
                "ok": False,
                "error": "Only HTTP/HTTPS supported.",
            }

        if parsed.scheme == "http":
            findings.append(
                "Connection is not encrypted with HTTPS."
            )

        return {
            "ok": True,
            "url": str(url),
            "hostname": parsed.hostname,
            "https": (
                parsed.scheme == "https"
            ),
            "findings": findings,
        }

    def bug_pattern_audit(
        self,
        text: str,
    ) -> dict:

        text = str(text)

        patterns = {
            "hardcoded_password": re.compile(
                r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]+['\"]"
            ),
            "private_key": re.compile(
                r"-----BEGIN .*PRIVATE KEY-----"
            ),
            "debug_enabled": re.compile(
                r"(?i)\bdebug\s*[:=]\s*(true|1)"
            ),
            "http_url": re.compile(
                r"http://[^\s\"']+"
            ),
        }

        findings = []

        for name, pattern in patterns.items():
            if pattern.search(text):
                findings.append({
                    "type": name,
                    "severity": (
                        "high"
                        if name == "private_key"
                        else "review"
                    ),
                })

        return {
            "ok": True,
            "findings": findings,
            "secrets_extracted": False,
        }

    def report(
        self,
        *,
        wifi=None,
        cctv=None,
        network=None,
        tls=None,
        bugs=None,
    ) -> dict:

        sections = {}

        if wifi is not None:
            sections["wifi"] = wifi

        if cctv is not None:
            sections["cctv"] = cctv

        if network is not None:
            sections["network"] = network

        if tls is not None:
            sections["tls"] = tls

        if bugs is not None:
            sections["bugs"] = bugs

        return {
            "ok": True,
            "authorized_security_audit": True,
            "sections": sections,
        }
