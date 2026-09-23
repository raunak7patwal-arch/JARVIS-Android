class SecurityBrain:
    def analyze(self, command):
        c = command.lower().strip()

        if c in ["status", "security status"]:
            return "Security Brain online. Authorized testing mode."

        if "help" in c:
            return (
                "Security Brain केवल authorized systems की defensive "
                "testing, diagnostics और security analysis के लिए है।"
            )

        return (
            "Security command received. Unauthorized access, account "
            "theft या दूसरे devices में intrusion इस brain का हिस्सा नहीं है।"
        )
