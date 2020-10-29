import requests
import json
import asyncio
import logging


class APIFeeder():

    STREAM_URL = "https://api.twitter.com/2/tweets/search/stream"
    RULES_URL = STREAM_URL + "/rules"

    def __init__(self, or_rule_list, bearer_token):
        self.headers = {"Authorization": "Bearer {}".format(bearer_token)}
        self.rules = {}
        self.rules_to_set = self._write_rules(or_rule_list)
        self.response = None
        logging.info("Setting up twitter stream ...")
        logging.info(f"For rules: \n {self.rules_to_set}")

    @staticmethod
    def _write_rules(or_terms):
        return [
            {"value": "{} lang:en".format(term)} for term in or_terms
        ]

    @staticmethod
    def raises(message):
        logging.exception(message)
        raise Exception(message)

    def _get_rules(self):
        self.response = requests.get(
            self.RULES_URL, headers=self.headers
        )

        if self.response.status_code != 200:
            self.raises(
                "Cannot get rules (HTTP {}): {}".format(
                    self.response.status_code, self.response.text)
            )

        logging.info(json.dumps(self.response.json()))
        return self

    def _delete_all_rules(self):
        rules = self.response.json()
        if rules is None or "data" not in rules:
            return self

        rule_ids = [rule["id"] for rule in rules["data"]]
        payload = {"delete": {"ids": rule_ids}}

        self.response = requests.post(
            self.RULES_URL,
            headers=self.headers,
            json=payload
        )

        if self.response.status_code != 200:
            self.raises(
                "Cannot delete rules (HTTP {}): {}".format(
                    self.response.status_code, self.response.text
                )
            )
        logging.info(json.dumps(self.response.json()))
        return self

    def _set_rules(self):
        payload = {"add": self.rules_to_set}

        self.response = requests.post(
            self.RULES_URL,
            headers=self.headers,
            json=payload,
        )

        if self.response.status_code != 201:
            self.raises(
                "Cannot add rules (HTTP {}): {}".format(
                    self.response.status_code, self.response.text)
            )
        logging.info(json.dumps(self.response.json()))
        return self

    def _get_stream(self):
        self.response = requests.get(
            self.STREAM_URL, headers=self.headers, stream=True,
        )
        logging.info(f"Getting stream responds with {self.response.status_code}")

        if self.response.status_code != 200:
            self.raises(
                "Cannot get stream (HTTP {}): {}".format(
                    self.response.status_code, self.response.text
                )
            )

        for response_line in self.response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                yield(json.dumps(json_response, indent=4, sort_keys=True))

    @staticmethod
    async def __print(data):
        """ In case of no feed_to operation wile streaming """
        print(data)

    def stream_async(self, feed_to=None, limit=None):
        """ Connects the stream to a faust cast operation
        """
        logging.info(f"Feeding stream to the worker for {limit} items")
        feed_to = feed_to or self.__print
        loop = asyncio.get_event_loop()
        twit_count = 0
        for i in self._get_rules(
                                     )._delete_all_rules(
                                     )._set_rules(
                                     )._get_stream():
            print(f"Aggregated {twit_count} twits so far\r", end="")
            loop.run_until_complete(feed_to(i))
            twit_count += 1
            if limit:
                if twit_count > limit:
                    break