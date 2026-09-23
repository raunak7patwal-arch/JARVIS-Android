import re
import ast
import operator


class FastAnswer:

    OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    @classmethod
    def calculate(cls, text):
        expr = text.strip()

        if not re.fullmatch(
            r"[0-9+\-*/().%\s]+",
            expr
        ):
            return None

        try:
            tree = ast.parse(
                expr,
                mode="eval"
            )

            result = cls._eval(tree.body)

            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)

            return str(result)

        except Exception:
            return None

    @classmethod
    def _eval(cls, node):

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError()

        if isinstance(node, ast.BinOp):

            operation = cls.OPS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError()

            left = cls._eval(node.left)
            right = cls._eval(node.right)

            if (
                abs(left) > 10**12
                or abs(right) > 10**12
            ):
                raise ValueError()

            return operation(
                left,
                right
            )

        if isinstance(node, ast.UnaryOp):

            value = cls._eval(
                node.operand
            )

            if isinstance(
                node.op,
                ast.USub
            ):
                return -value

            if isinstance(
                node.op,
                ast.UAdd
            ):
                return value

        raise ValueError()

    @classmethod
    def _normalize(cls, text):
        return " ".join(
            str(text)
            .strip()
            .lower()
            .split()
        )

    @classmethod
    def answer(cls, text):

        original = str(text).strip()
        lower = cls._normalize(original)
        clean = re.sub(r"[?!।,]+$", "", lower).strip()

        if not original:
            return None

        # --------------------------------------------------
        # Greetings
        # --------------------------------------------------

        greetings = {
            "hi",
            "hello",
            "hey",
            "hii",
            "नमस्ते",
            "नमस्कार",
            "हेलो",
            "हाय",
        }

        if clean in greetings:
            return "नमस्ते सर।"

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        identity = {
            "who are you",
            "what are you",
            "what is your name",
            "whats your name",
            "what's your name",
            "your name",
            "तुम कौन हो",
            "आप कौन हो",
            "तुम्हारा नाम क्या है",
            "आपका नाम क्या है",
            "नाम क्या है",
        }

        if clean in identity:
            return "मैं JARVIS हूँ, सर।"

        # --------------------------------------------------
        # Simple capability questions
        # --------------------------------------------------

        capability_questions = {
            "what can you do",
            "what can you do?",
            "तुम क्या कर सकते हो",
            "आप क्या कर सकते हो",
            "तुम क्या कर सकते हो?",
            "आप क्या कर सकते हो?",
        }

        if clean in capability_questions:
            return (
                "सर, मैं सवालों के जवाब दे सकता हूँ, "
                "जानकारी खोज सकता हूँ और authorized "
                "device commands संभाल सकता हूँ।"
            )

        # --------------------------------------------------
        # Simple status
        # --------------------------------------------------

        status_questions = {
            "are you there",
            "are you online",
            "jarvis are you there",
            "jarvis are you online",
            "क्या तुम यहाँ हो",
            "क्या तुम ऑनलाइन हो",
            "जार्विस क्या तुम यहाँ हो",
            "जार्विस ऑनलाइन हो",
        }

        if clean in status_questions:
            return "जी सर। JARVIS online है।"

        # --------------------------------------------------
        # Simple acknowledgement
        # --------------------------------------------------

        acknowledgements = {
            "thanks",
            "thank you",
            "thanks jarvis",
            "thank you jarvis",
            "धन्यवाद",
            "शुक्रिया",
            "थैंक यू",
        }

        if clean in acknowledgements:
            return "स्वागत है, सर।"

        # --------------------------------------------------
        # Simple calculator
        # --------------------------------------------------

        math_text = original

        # Common punctuation हटाओ
        math_text = re.sub(r"[?!।,]+$", "", math_text).strip()

        replacements = {
            "×": "*",
            "÷": "/",
            "−": "-",
        }

        for old, new in replacements.items():
            math_text = math_text.replace(
                old,
                new
            )

        math_text = re.sub(
            r"(?i)\b("
            r"what is|calculate|solve|"
            r"equals|equal to|"
            r"how much is"
            r")\b",
            "",
            math_text
        )

        math_text = re.sub(
            r"("
            r"कितना है|"
            r"निकालो|"
            r"गणना करो|"
            r"हल करो|"
            r"का जवाब|"
            r"कितना होगा"
            r")",
            "",
            math_text
        ).strip()

        result = cls.calculate(
            math_text
        )

        if result is not None:
            return f"{result}, सर।"

        # --------------------------------------------------
        # No instant answer
        # --------------------------------------------------

        return None
