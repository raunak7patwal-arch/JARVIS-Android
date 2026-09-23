import json
import os
import time
import urllib.error
import urllib.request

from jarvis.central.personality.controller import JarvisPersonality


class GeminiEngine:

    def __init__(self):
        self.api_key = self._load_key()

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

        self.url = (
            "https://generativelanguage.googleapis.com"
            f"/v1beta/models/{self.model}:generateContent"
        )

        # Retry settings
        self.max_retries = 3
        self.timeout = 30

    def _load_key(self):

        key = os.getenv("GEMINI_API_KEY")

        if key:
            return key.strip()

        env_file = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ),
            "config",
            "api.env"
        )

        if os.path.exists(env_file):

            try:
                with open(
                    env_file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    for line in f:

                        line = line.strip()

                        if line.startswith(
                            "GEMINI_API_KEY="
                        ):
                            return line.split(
                                "=",
                                1
                            )[1].strip()

            except Exception:
                pass

        return None

    def _build_request(
        self,
        data
    ):
        request = urllib.request.Request(
            self.url,
            data=data,
            method="POST"
        )

        request.add_header(
            "Content-Type",
            "application/json"
        )

        request.add_header(
            "x-goog-api-key",
            self.api_key
        )

        return request

    def _extract_answer(
        self,
        result
    ):
        candidates = result.get(
            "candidates",
            []
        )

        if not candidates:
            return None

        content = candidates[0].get(
            "content",
            {}
        )

        parts = content.get(
            "parts",
            []
        )

        answer_parts = []

        for part in parts:

            text = part.get("text")

            if text:
                answer_parts.append(text)

        answer = "\n".join(
            answer_parts
        ).strip()

        return answer or None

    def ask(
        self,
        question,
        context=""
    ):

        if not self.api_key:

            return (
                "सर, Gemini API key configured नहीं है।"
            )

        prompt = JarvisPersonality.prompt(
            question,
            context
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 500
            }
        }

        data = json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")

        last_error = None

        for attempt in range(
            self.max_retries + 1
        ):

            try:

                request = self._build_request(
                    data
                )

                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout
                ) as response:

                    raw = response.read()

                result = json.loads(
                    raw.decode("utf-8")
                )

                answer = self._extract_answer(
                    result
                )

                if answer:
                    return answer

                return (
                    "सर, Gemini ने कोई उत्तर नहीं दिया।"
                )

            except urllib.error.HTTPError as e:

                last_error = e

                try:
                    error_body = e.read().decode(
                        "utf-8",
                        errors="replace"
                    )
                except Exception:
                    error_body = ""

                print(
                    f"GEMINI HTTP ERROR "
                    f"{e.code} "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries + 1}): "
                    f"{error_body}"
                )

                # 503 = temporary unavailable
                # 429 = rate limit
                # Retry both.
                if e.code in (429, 500, 502, 503, 504):

                    if attempt < self.max_retries:

                        wait_time = 2 ** attempt

                        print(
                            "Gemini retry in "
                            f"{wait_time}s..."
                        )

                        time.sleep(
                            wait_time
                        )

                        continue

                break

            except urllib.error.URLError as e:

                last_error = e

                print(
                    f"GEMINI NETWORK ERROR "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries + 1}):",
                    repr(e)
                )

                if attempt < self.max_retries:

                    wait_time = 2 ** attempt

                    print(
                        "Gemini network retry in "
                        f"{wait_time}s..."
                    )

                    time.sleep(
                        wait_time
                    )

                    continue

                break

            except TimeoutError as e:

                last_error = e

                print(
                    f"GEMINI TIMEOUT "
                    f"(attempt {attempt + 1}/"
                    f"{self.max_retries + 1})"
                )

                if attempt < self.max_retries:

                    wait_time = 2 ** attempt

                    print(
                        "Gemini timeout retry in "
                        f"{wait_time}s..."
                    )

                    time.sleep(
                        wait_time
                    )

                    continue

                break

            except Exception as e:

                last_error = e

                print(
                    "GEMINI ERROR:",
                    repr(e)
                )

                break

        if isinstance(
            last_error,
            urllib.error.HTTPError
        ):

            if last_error.code == 503:

                return (
                    "सर, Gemini service अभी "
                    "temporarily unavailable है। "
                    "थोड़ी देर बाद फिर कोशिश करें।"
                )

            if last_error.code == 429:

                return (
                    "सर, Gemini की request limit "
                    "अभी पूरी हो गई है। थोड़ी देर "
                    "बाद फिर कोशिश करें।"
                )

            return (
                "सर, Gemini API request असफल हुई।"
            )

        if isinstance(
            last_error,
            urllib.error.URLError
        ):

            return (
                "सर, Gemini server से connection "
                "नहीं हो पाया।"
            )

        if isinstance(
            last_error,
            TimeoutError
        ):

            return (
                "सर, Gemini response में बहुत "
                "समय लग रहा है।"
            )

        return (
            "सर, Gemini से response लेते समय "
            "समस्या आई।"
        )
