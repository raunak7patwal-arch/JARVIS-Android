import time


class RequestGuard:

    MAX_TEXT_LENGTH = 4000
    MAX_PARAMETER_LENGTH = 2000

    def validate_question(self, text):
        if text is None:
            return False, "Empty request"

        text = str(text).strip()

        if not text:
            return False, "Empty request"

        if len(text) > self.MAX_TEXT_LENGTH:
            return False, "Request too long"

        return True, "OK"

    def validate_parameters(self, parameters):
        if parameters is None:
            return True, "OK"

        if not isinstance(parameters, dict):
            return False, "Invalid parameters"

        for key, value in parameters.items():
            if len(str(key)) > 200:
                return False, "Parameter name too long"

            if len(str(value)) > self.MAX_PARAMETER_LENGTH:
                return False, "Parameter value too long"

        return True, "OK"

    def timestamp(self):
        return time.time()
