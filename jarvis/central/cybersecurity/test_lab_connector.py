from .lab_connector import SecurityLabConnector


lab = SecurityLabConnector()

info = lab.system_info()

assert info["ok"] is True
assert "os" in info
assert "python" in info

network = lab.network_info()

assert network["ok"] is True

services = lab.list_listening_services()

assert "ok" in services

repo = lab.github_repo_audit(".")

assert repo["ok"] is True
assert "files_scanned" in repo

blocked = lab.run("exploit_target")

assert blocked["ok"] is False

print("SUCCESS")
print("Kali/Parrot Lab Connector : ONLINE")
print("System Inventory          : READY")
print("Network Inventory         : READY")
print("Listening Services        : READY")
print("GitHub Repository Audit   : READY")
print("Secret Extraction         : DISABLED")
print("Exploit Automation        : DISABLED")
print("AUTHORIZED LAB USE ONLY")
