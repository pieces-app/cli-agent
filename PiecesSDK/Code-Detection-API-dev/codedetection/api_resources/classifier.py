from codedetection.api_requestor import APIRequestor


class Classifier(APIRequestor):

    @classmethod
    def classify(cls, inputs: list) -> list:
        """
        classify function does classification of batched code snippets.

        :param inputs: list of strings (batched code snippets).
        :return: list of dictionaries including classified programming language and predictions.
        """

        response = cls._make_request(inputs)

        return [
            {
                "language": record["codeClassification"]["result"]["current"],
                "predictions": [
                    {x["current"]: x["likelihood"]} for x in record["codeClassification"]["rankings"]["iterable"]
                ]
            } for record in response["iterable"]
        ]
