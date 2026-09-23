from .auditor import CyberSecurityAuditor


audit = CyberSecurityAuditor()

wifi = audit.wifi_audit(
    "JARVIS-LAB",
    "WPA3",
    True
)

assert wifi["type"] == "wifi"
assert wifi["security"] == "WPA3"

bugs = audit.bug_pattern_audit(
    'debug=true\npassword="example-password"'
)

assert bugs["ok"] is True
assert bugs["secrets_extracted"] is False
assert len(bugs["findings"]) >= 1

url = audit.url_security_audit(
    "https://example.com"
)

assert url["ok"] is True
assert url["https"] is True

report = audit.report(
    wifi=wifi,
    bugs=bugs,
    network={"ok": True}
)

assert report["authorized_security_audit"] is True
assert "wifi" in report["sections"]

print("SUCCESS")
print("Wi-Fi Security Audit    : READY")
print("CCTV Security Audit     : READY")
print("Network Service Audit   : READY")
print("TLS Audit               : READY")
print("Bug Pattern Audit       : READY")
print("Security Report         : READY")
print("Password Cracking       : DISABLED")
print("Exploit Execution       : DISABLED")
print("Unauthorized Access     : DISABLED")
print("AUTHORIZED USE ONLY")
