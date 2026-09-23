from __future__ import annotations

import re

from jarvis.central.ai.gemini import GeminiEngine
from jarvis.central.cache.fast_cache import FastCache
from jarvis.central.memory.store import MemoryStore
from jarvis.central.memory.activity_logger import ActivityLogger
from jarvis.central.conversation.manager import ConversationManager
from jarvis.central.commands.router import CommandRouter
from jarvis.central.fast_answer import FastAnswer
from jarvis.central.knowledge.gateway import KnowledgeGateway
from jarvis.central.tools.manager import TermuxToolManager
from jarvis.central.security.memory_bridge import PersistentMemoryBridge
from jarvis.central.security.persistence import JARVISPersistence


class AIEngine:

    def __init__(self):
        self.gemini = GeminiEngine()
        self.cache = FastCache()
        self.memory = MemoryStore()
        self.activity = ActivityLogger()

        self.conversation = ConversationManager(
            max_turns=12
        )

        self.commands = CommandRouter()
        self.knowledge = KnowledgeGateway()
        self.termux_tools = TermuxToolManager()
        self.persistence = JARVISPersistence()
        self.persistent_memory = PersistentMemoryBridge()

        # Persistent lineage/state is initialized without
        # unlocking the encrypted vault.
        self.persistence.create_lineage()
        self.persistence.record_startup()

    def _log(
        self,
        event,
        *,
        question=None,
        answer=None,
        command=None,
        metadata=None
    ):
        try:
            self.activity.log(
                event,
                question=question,
                answer=answer,
                command=command,
                metadata=metadata
            )
        except Exception as e:
            print("Activity logger error:", e)

    def build_context(
        self,
        evidence=None,
        memories=None
    ):
        parts = []

        conversation = self.conversation.context()

        if conversation:
            parts.append(
                "Current conversation:\n"
                + conversation
            )

        if memories:
            memory_lines = []

            for item in memories:
                text = item.get("text", "")
                category = item.get(
                    "category",
                    "general"
                )

                if text:
                    memory_lines.append(
                        f"- [{category}] {text}"
                    )

            if memory_lines:
                parts.append(
                    "Relevant JARVIS memory:\n"
                    + "\n".join(memory_lines)
                )

        if evidence:
            evidence_lines = []

            for item in evidence[:15]:
                if not isinstance(item, dict):
                    continue

                entity = item.get(
                    "entity",
                    ""
                )

                description = item.get(
                    "description",
                    ""
                )

                title = item.get(
                    "title",
                    ""
                )

                snippet = item.get(
                    "snippet",
                    ""
                )

                if entity or description:
                    evidence_lines.append(
                        f"Entity: {entity}\n"
                        f"Description: {description}"
                    )

                if title or snippet:
                    evidence_lines.append(
                        f"Source: {title}\n"
                        f"Information: {snippet}"
                    )

            if evidence_lines:
                parts.append(
                    "External knowledge:\n"
                    + "\n\n".join(evidence_lines)
                )

        if not parts:
            return (
                "No additional context is "
                "currently available."
            )

        return "\n\n".join(parts)

    # ======================================================
    # Persistent JARVIS state
    # ======================================================

    def persistence_status(self):
        return self.persistence.status()

    def unlock_persistent_memory(self, password):
        return self.persistent_memory.unlock(
            password
        )

    def lock_persistent_memory(self):
        self.persistent_memory.lock()

    def _record_persistent_activity(
        self,
        question,
        answer,
        action=None,
    ):
        try:
            if not self.persistent_memory.unlocked:
                return

            self.persistent_memory.remember_conversation(
                "user",
                question,
            )

            self.persistent_memory.remember_conversation(
                "assistant",
                answer,
            )

            self.persistent_memory.add_activity(
                "ai_answer",
                {
                    "question": question,
                    "action": action,
                },
            )

        except Exception as exc:
            self._log(
                "persistence_error",
                metadata={
                    "error": str(exc),
                },
            )

    def _record_runtime_state(self):
        try:
            self.persistence.save_runtime_state(
                central_brain="ONLINE",
                ai_engine="ONLINE",
                memory_system="ONLINE",
                conversation="ONLINE",
                termux_tools="ONLINE",
                persistent=True,
            )
        except Exception as exc:
            self._log(
                "persistence_error",
                metadata={
                    "error": str(exc),
                },
            )

    def answer(
        self,
        question,
        evidence=None,
        language="en"
    ):
        question = str(question).strip()

        # Runtime state is persistent even when the
        # encrypted memory vault remains locked.
        self._record_runtime_state()

        if not question:
            answer = (
                "सर, मुझे कोई सवाल "
                "नहीं मिला।"
            )

            self._log(
                "error",
                answer=answer,
                metadata={
                    "reason": "empty_question"
                }
            )

            return {
                "answer": answer,
                "cached": False,
                "command": None,
                "evidence_count": 0
            }

        # --------------------------------------------------
        # 0. Termux tool inventory
        # --------------------------------------------------

        if self._termux_tools_request(question):
            self.conversation.add_user(question)

            answer = self._termux_tools_response()

            self.conversation.add_assistant(answer)

            self._record_persistent_activity(
                question,
                answer,
                "termux_tools",
            )

            self._log(
                "command",
                question=question,
                answer=answer,
                command={
                    "action": "termux_tools",
                    "parameters": {}
                }
            )

            return {
                "answer": answer,
                "cached": False,
                "command": {
                    "is_command": True,
                    "action": "termux_tools",
                    "parameters": {}
                },
                "evidence_count": 0
            }

        # --------------------------------------------------
        # 1. Device / app commands
        # --------------------------------------------------

        command = self.commands.route(
            question
        )

        if command.get(
            "is_command",
            False
        ):
            action = command.get(
                "action"
            )

            parameters = command.get(
                "parameters",
                {}
            )

            self.conversation.add_user(
                question
            )

            answer = self._command_response(
                action,
                parameters
            )

            self.conversation.add_assistant(
                answer
            )

            self._record_persistent_activity(
                question,
                answer,
                action,
            )

            self._log(
                "command",
                question=question,
                answer=answer,
                command={
                    "action": action,
                    "parameters": parameters
                }
            )

            return {
                "answer": answer,
                "cached": False,
                "command": command,
                "evidence_count": 0
            }

        # --------------------------------------------------
        # 2. Instant local answers
        # --------------------------------------------------

        instant = FastAnswer.answer(
            question
        )

        if instant is not None:
            self.conversation.add_user(
                question
            )

            self.conversation.add_assistant(
                instant
            )

            self._record_persistent_activity(
                question,
                instant,
                "fast_answer",
            )

            self._log(
                "answer",
                question=question,
                answer=instant,
                metadata={
                    "source": "fast_answer"
                }
            )

            return {
                "answer": instant,
                "cached": False,
                "command": command,
                "evidence_count": 0
            }

        # --------------------------------------------------
        # 3. Conversation + memory
        # --------------------------------------------------

        self.conversation.add_user(
            question
        )

        memories = self.memory.search(
            question,
            limit=5
        )

        use_cache = (
            self.conversation.size() <= 1
        )

        if use_cache:
            cached = self.cache.get(
                question
            )

            if cached:
                self.conversation.add_assistant(
                    cached
                )

                self._log(
                    "answer",
                    question=question,
                    answer=cached,
                    metadata={
                        "source": "cache",
                        "cached": True
                    }
                )

                return {
                    "answer": cached,
                    "cached": True,
                    "command": command,
                    "evidence_count": 0
                }

        # --------------------------------------------------
        # 4. Knowledge Gateway
        # --------------------------------------------------

        knowledge = (
            evidence
            if evidence
            else []
        )

        if not knowledge:
            try:
                knowledge = self.knowledge.search(
                    question,
                    language
                )

            except Exception as e:
                print(
                    "Knowledge gateway error:",
                    e
                )

                self._log(
                    "error",
                    question=question,
                    metadata={
                        "source": "knowledge_gateway",
                        "error": str(e)[:500]
                    }
                )

                knowledge = []

        if knowledge:
            self._log(
                "search",
                question=question,
                metadata={
                    "source": "knowledge_gateway",
                    "evidence_count": len(knowledge)
                }
            )

        # --------------------------------------------------
        # 5. Try Gemini
        # --------------------------------------------------

        context = self.build_context(
            knowledge,
            memories
        )

        answer = None

        try:
            answer = self.gemini.ask(
                question,
                context
            )

        except Exception as e:
            print(
                "Gemini engine error:",
                e
            )

            self._log(
                "error",
                question=question,
                metadata={
                    "source": "gemini",
                    "error": str(e)[:500]
                }
            )

        # --------------------------------------------------
        # 6. Knowledge fallback
        # --------------------------------------------------

        if not answer:
            answer = self._knowledge_fallback(
                question,
                knowledge,
                language
            )

            if answer:
                self._log(
                    "answer",
                    question=question,
                    answer=answer,
                    metadata={
                        "source": "knowledge_fallback"
                    }
                )

        # --------------------------------------------------
        # 7. Final fallback
        # --------------------------------------------------

        if not answer:
            answer = (
                "सर, इस समय मुझे इसका "
                "विश्वसनीय उत्तर नहीं मिल पाया।"
            )

            self._log(
                "error",
                question=question,
                answer=answer,
                metadata={
                    "reason": "no_answer"
                }
            )

        else:
            self._log(
                "answer",
                question=question,
                answer=answer,
                metadata={
                    "source": "gemini"
                }
            )

        self.conversation.add_assistant(
            answer
        )

        # --------------------------------------------------
        # 8. Cache only successful answers
        # --------------------------------------------------

        if (
            use_cache
            and answer
            and not answer.startswith(
                "सर, इस समय"
            )
            and not answer.startswith(
                "सर, Gemini"
            )
        ):
            self.cache.set(
                question,
                answer
            )

        return {
            "answer": answer,
            "cached": False,
            "command": command,
            "evidence_count": len(
                knowledge
            )
        }

    # ======================================================
    # Termux tools
    # ======================================================

    def _termux_tools_request(self, question):
        text = str(question).strip().lower()

        patterns = (
            "termux tools",
            "termux में कौन-कौन से tools",
            "termux में कौन कौन से tools",
            "मेरे termux में कौन-कौन से tools",
            "मेरे termux में कौन कौन से tools",
            "termux में कौन से tools",
            "termux के tools",
            "installed tools",
            "installed termux tools",
            "टर्मक्स टूल्स",
            "टर्मक्स के टूल्स",
        )

        return any(pattern in text for pattern in patterns)

    def _termux_tools_response(self):
        return self.termux_tools.summary()

    # ======================================================
    # Knowledge fallback
    # ======================================================

    @staticmethod
    def _knowledge_fallback(
        question,
        knowledge,
        language="en"
    ):
        if not knowledge:
            return None

        question_lower = (
            question.lower()
        )

        # ----------------------------------------------
        # Capital questions
        # ----------------------------------------------

        capital_words = (
            "capital",
            "राजधानी"
        )

        if any(
            word in question_lower
            for word in capital_words
        ):
            country = (
                AIEngine._extract_country(
                    question
                )
            )

            if country:
                capital = (
                    AIEngine._find_capital(
                        country,
                        knowledge
                    )
                )

                if capital:
                    if language == "hi":
                        return (
                            f"{country} की "
                            f"राजधानी {capital} है, सर।"
                        )

                    return (
                        f"The capital of "
                        f"{country} is "
                        f"{capital}, सर।"
                    )

        # ----------------------------------------------
        # Generic knowledge fallback
        # ----------------------------------------------

        first = knowledge[0]

        if not isinstance(
            first,
            dict
        ):
            return None

        title = first.get(
            "title",
            ""
        )

        description = first.get(
            "description",
            ""
        )

        snippet = first.get(
            "snippet",
            ""
        )

        if description:
            return (
                f"{title}: "
                f"{description}"
            )

        if snippet:
            text = (
                snippet
                .replace(
                    "\n",
                    " "
                )
                .strip()
            )

            if len(text) > 500:
                text = (
                    text[:500]
                    .rsplit(" ", 1)[0]
                    + "..."
                )

            return text

        return None

    @staticmethod
    def _extract_country(
        question
    ):
        text = question.strip()

        patterns = [
            r"(.+?)\s+की\s+राजधानी",
            r"capital\s+of\s+(.+?)\??$",
            r"capital\s+of\s+(.+?)\s+is",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(
                    1
                ).strip()

        return None

    @staticmethod
    def _find_capital(
        country,
        knowledge
    ):
        country_lower = (
            country.lower()
        )

        for item in knowledge:
            if not isinstance(
                item,
                dict
            ):
                continue

            text = " ".join(
                str(
                    item.get(
                        key,
                        ""
                    )
                )
                for key in (
                    "title",
                    "description",
                    "snippet"
                )
            )

            lower = text.lower()

            if (
                country_lower not in lower
                and item.get(
                    "title",
                    ""
                ).lower() != country_lower
            ):
                continue

            # English:
            # "capital ... is Tokyo"
            match = re.search(
                r"capital(?:\s+city)?"
                r"\s+(?:of\s+[^.]+?\s+)?"
                r"(?:is|was)\s+"
                r"([A-Z][A-Za-z .'-]+)",
                text,
                re.IGNORECASE
            )

            if match:
                value = match.group(
                    1
                ).strip(
                    " .,!?:;"
                )

                if value:
                    return value

            # Hindi:
            # "राजधानी ... टोक्यो है"
            match = re.search(
                r"राजधानी"
                r".{0,80}?"
                r"(?:है|था|थी)"
                r"\s*"
                r"([^\s,।.!?]+)",
                text
            )

            if match:
                return match.group(
                    1
                ).strip(
                    " .,!?:;।"
                )

        return None

    # ======================================================
    # Command responses
    # ======================================================

    def _command_response(
        self,
        action,
        parameters
    ):
        responses = {
            "ping": (
                "Connection verified, सर।"
            ),
            "open_app": (
                self._open_app_response(
                    parameters
                )
            ),
            "open_url": (
                self._open_url_response(
                    parameters
                )
            ),
            "device_info": (
                "Device information "
                "command तैयार है, सर।"
            ),
            "notification": (
                "Notification command "
                "तैयार है, सर।"
            ),
        }

        return responses.get(
            action,
            "Command प्राप्त हुई, सर।"
        )

    @staticmethod
    def _open_app_response(
        parameters
    ):
        app = parameters.get(
            "app"
        )

        if app:
            return (
                f"{app} खोलने की "
                "command तैयार है, सर।"
            )

        return (
            "सर, कौन-सा app खोलना है "
            "यह नहीं मिला।"
        )

    @staticmethod
    def _open_url_response(
        parameters
    ):
        url = parameters.get(
            "url"
        )

        if url:
            return (
                "Website खोलने की "
                "command तैयार है, सर।"
            )

        return (
            "सर, URL नहीं मिला।"
        )
