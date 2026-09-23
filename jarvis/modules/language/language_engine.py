import re


class LanguageEngine:

    LANGUAGES = {
        "hi": "Hindi",
        "en": "English",
        "bn": "Bengali",
        "pa": "Punjabi",
        "gu": "Gujarati",
        "mr": "Marathi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "ne": "Nepali",
        "ur": "Urdu",
        "ar": "Arabic",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "tr": "Turkish",
        "id": "Indonesian",
    }

    HINGLISH = {
        "hii": "हाय",
        "hi": "हाय",
        "hello": "हेलो",

        "kya": "क्या",
        "kyaa": "क्या",

        "kese": "कैसे",
        "kaise": "कैसे",
        "kaisa": "कैसा",
        "kaisi": "कैसी",

        "ho": "हो",
        "hai": "है",
        "hain": "हैं",

        "kar": "कर",
        "karo": "करो",
        "kr": "कर",
        "krr": "कर",

        "rhe": "रहे",
        "rahe": "रहे",
        "rha": "रहा",
        "raha": "रहा",
        "rhi": "रही",
        "rahi": "रही",

        "kya": "क्या",
        "kaun": "कौन",
        "kon": "कौन",

        "kahan": "कहाँ",
        "kaha": "कहाँ",

        "kab": "कब",

        "kyun": "क्यों",
        "kyu": "क्यों",
        "kyo": "क्यों",

        "kitna": "कितना",
        "kitne": "कितने",
        "kitni": "कितनी",

        "main": "मैं",
        "mein": "में",
        "me": "में",

        "mera": "मेरा",
        "meri": "मेरी",
        "mere": "मेरे",

        "tum": "तुम",
        "aap": "आप",

        "mujhe": "मुझे",
        "mujhko": "मुझको",

        "batao": "बताओ",
        "btao": "बताओ",
        "bata": "बता",

        "karo": "करो",
        "karna": "करना",

        "kya": "क्या",

        "bharat": "भारत",
        "india": "भारत",
        "japan": "जापान",

        "rajdhani": "राजधानी",
        "capital": "राजधानी",

        "pradhanmantri": "प्रधानमंत्री",
        "pm": "प्रधानमंत्री",
        "mukhyamantri": "मुख्यमंत्री",
        "cm": "मुख्यमंत्री",

        "naam": "नाम",
        "nam": "नाम",

        "tumhara": "तुम्हारा",
        "aapka": "आपका",

        "kahan": "कहाँ",
        "kha": "कहाँ",

        "kya": "क्या",

        "kar": "कर",
        "rhe": "रहे",
        "re": "रहे",

        "ho": "हो",
    }

    def detect(self, text):

        if re.search(r'[\u0900-\u097F]', text):
            return "hi"

        if re.search(r'[\u0980-\u09FF]', text):
            return "bn"

        if re.search(r'[\u0A00-\u0A7F]', text):
            return "pa"

        if re.search(r'[\u0A80-\u0AFF]', text):
            return "gu"

        if re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"

        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"

        if re.search(r'[\u0C80-\u0CFF]', text):
            return "kn"

        if re.search(r'[\u0D00-\u0D7F]', text):
            return "ml"

        if re.search(r'[\u0600-\u06FF]', text):
            return "ar"

        if re.search(r'[\u0400-\u04FF]', text):
            return "ru"

        if re.search(r'[\u3040-\u30FF]', text):
            return "ja"

        if re.search(r'[\uAC00-\uD7AF]', text):
            return "ko"

        if re.search(r'[\u4E00-\u9FFF]', text):
            return "zh"

        # Roman script:
        # detect common Hindi/Hinglish words
        words = set(text.lower().split())

        hindi_words = sum(
            1 for word in words
            if word in self.HINGLISH
        )

        if hindi_words >= 1:
            return "hi-Latn"

        return "en"

    def normalize_hinglish(self, text):

        words = text.lower().split()
        result = []

        for word in words:

            clean = re.sub(
                r"[^a-zA-Z\u0900-\u097F]",
                "",
                word
            )

            if clean in self.HINGLISH:
                result.append(self.HINGLISH[clean])
            else:
                result.append(word)

        return " ".join(result)

    def process(self, text):

        language = self.detect(text)
        normalized = self.normalize_hinglish(text)

        return {
            "language": language,
            "language_name": self.LANGUAGES.get(
                language,
                "Hindi (Roman/Hinglish)"
                if language == "hi-Latn"
                else "Unknown"
            ),
            "normalized": normalized,
            "original": text,
        }
