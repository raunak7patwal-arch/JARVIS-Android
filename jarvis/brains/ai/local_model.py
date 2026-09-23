import subprocess


class LocalAI:
    def __init__(self):
        self.model_repo = "bartowski/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M"

    def ask(self, prompt):
        command = [
            "llama-cli",
            "-hf", self.model_repo,
            "-c", "4096",
            "-t", "4",
            "-n", "128",
            "-p", prompt
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                return "Local AI में समस्या आ गई।"

            output = result.stdout.strip()

            # llama-cli के extra status text को हटाने की कोशिश
            if "[ Prompt:" in output:
                output = output.split("[ Prompt:")[0].strip()

            return output or "मुझे कोई उत्तर नहीं मिला।"

        except subprocess.TimeoutExpired:
            return "AI ने समय पर जवाब नहीं दिया।"

        except Exception as e:
            return f"AI error: {e}"
