import re


class FactExtractor:

    @staticmethod
    def _text(item):
        return " ".join(
            str(item.get(key, ""))
            for key in (
                "title",
                "description",
                "snippet"
            )
        ).strip()

    @classmethod
    def capital(cls, country, evidence):
        country = country.strip()

        patterns = [
            r"(?:capital|राजधानी)"
            r"(?:\s+(?:city|शहर))?"
            r"\s+(?:of|की|का)?"
            r".{0,80}?"
            r"(?:is|है|होती है|था|थी)"
            r"\s+([A-Z][A-Za-z .'-]{1,50})",

            r"([A-Z][A-Za-z .'-]{1,50})"
            r"\s+(?:is|है)"
            r"\s+(?:the\s+)?capital",

            r"राजधानी\s+([^\s,।.!?]+)"
        ]

        for item in evidence:
            text = cls._text(item)

            if not text:
                continue

            for pattern in patterns:
                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                if match:
                    value = match.group(1).strip(
                        " .,!?:;।"
                    )

                    if value and len(value) < 60:
                        return value

        # Known direct result:
        # if a result title explicitly describes
        # a capital city, use the title.
        for item in evidence:
            title = str(
                item.get("title", "")
            ).strip()

            description = str(
                item.get("description", "")
            ).lower()

            if (
                country.lower() in title.lower()
                and "capital" in description
            ):
                return title

        return None

    @classmethod
    def first_useful(cls, evidence):
        for item in evidence:
            if not isinstance(item, dict):
                continue

            title = item.get("title", "")
            description = item.get(
                "description",
                ""
            )
            snippet = item.get(
                "snippet",
                ""
            )

            if description:
                return (
                    f"{title}: "
                    f"{description}"
                )

            if snippet:
                text = str(
                    snippet
                ).strip()

                if len(text) > 600:
                    text = (
                        text[:600]
                        .rsplit(" ", 1)[0]
                        + "..."
                    )

                return text

        return None
