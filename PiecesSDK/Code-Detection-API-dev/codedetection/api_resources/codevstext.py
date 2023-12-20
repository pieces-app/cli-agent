from codedetection.api_requestor import APIRequestor


class CodeVsText(APIRequestor):

    @classmethod
    def evaluate(cls, inputs: list) -> list:
        """
        evaluate function checks if a given strings are code snippets or natural language.

        :param inputs: list of strings of natural language or code snippets.
        :return: list of dictionaries including boolean value if string is natural language and likelihood.
        """

        response = cls._make_request(inputs)

        return [
            {
                "naturalLanguage": record["naturalLanguage"]["result"],
                "likelihood": record["naturalLanguage"]["likelihood"]
            } for record in response["iterable"]
        ]
