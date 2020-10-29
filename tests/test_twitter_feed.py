import json
import os
import sys
from os.path import join, dirname
from jsonschema import validate
from unittest import TestCase

# importing our own code:
root = os.path.join(os.path.dirname(__file__))
package = os.path.join(root, "..")
sys.path.insert(0, os.path.abspath(package))


from analyzer.twitter_feed import APIFeeder as TwitterFeeder


class TwitterAPIIntegration(TestCase):

    SCHEMAS_DIR = "response_schemas"

    def setUp(self):
        """  Asserts no twitter api breaking changes
        In case of any breaking changes our tests should
        fail.
        """
        bearer_token = os.environ.get("BEARER_TOKEN")
        or_list = ['#Trump', '#Biden', '#elections', '#trump', '#biden']
        self.token = os.environ.get("BEARER_TOKEN")
        self.streamer = TwitterFeeder(or_list, bearer_token)

    def _load_json_schema(self, file_name):
        """ Loads the given schema file """

        relative_path = os.path.join(
            self.SCHEMAS_DIR, file_name
        )
        absolute_path = join(dirname(__file__), relative_path)

        with open(absolute_path) as schema_file:
            return json.loads(schema_file.read())

    def assert_valid_schema(self, instance, schema):
        """ Extends the assertion functionality of the TestCase class """
        return validate(instance=instance, schema=schema)

    def test_get_rules(self):
        self.streamer._get_rules()
        self.assertEqual(self.streamer.response.status_code,200)

    def test_delete_all_rules(self):
        self.streamer._get_rules()._delete_all_rules()
        self.assertEqual(self.streamer.response.status_code, 200)

    def test_set_rules(self):
        self.streamer._get_rules()._delete_all_rules()._set_rules()
        self.assertEqual(self.streamer.response.status_code, 201)

    def test_get_stream(self):
        """ Should test the JSON response. The analysis does depend on its
        structure.
        """
        schema = self._load_json_schema(
            "twit_schema.json"
        )
        stream = self.streamer._get_rules(
                                         )._delete_all_rules(

                                         )._set_rules(

                                         )._get_stream()

        self.assertEqual(self.streamer.response.status_code,201)

        twit = next(stream)

        self.assert_valid_schema(
            instance=json.loads(twit),
            schema=schema
        )


