from codedetection.api_requestor import APIRequestor


class Tokenizer(APIRequestor):

    @classmethod
    def tokenize(cls, inputs: list) -> list:
        """
        tokenize function does tokenization of given list of strings.

        :param inputs: list of strings (batched code snippets or natural language text).
        :return: list of dictionaries including tokenized text.
        """

        response = cls._make_request(inputs)

        return [
            {
                "tokens": record["naturalLanguage"]["tokens"],
            } for record in response["iterable"]
        ]
