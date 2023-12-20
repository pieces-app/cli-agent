from codedetection.api_requestor import APIRequestor


class TLP(APIRequestor):
    @classmethod
    def create(cls, inputs: list) -> dict:
        """
        create function gives the overview about given list of strings.

        :param inputs: list of strings of natural language or code snippets.
        :return: list of dictionaries including overview data about given strings.
        """

        response = cls._make_request(inputs)

        return response
