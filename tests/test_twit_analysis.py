import os
import sys
import json
import numpy
from mock import patch, MagicMock
from unittest import TestCase

# # importing our own code:
# root = os.path.join(os.path.dirname(__file__))
# package = os.path.join(root, "..")
# sys.path.insert(0, os.path.abspath(package))

from analyzer.twit_analysis import (
                                        cleanup,
                                        tokenize,
                                        deflate_twit,
                                        score_and_pad_tokens,
                                        analyze_and_format_twit,
                                        predict_sentiment
                                    )

from analyzer.utils import load_json_file, load_yaml_config


class TextAnalysisSteps(TestCase):

    def test_cleanup(self):
        string = "300 @user of www.url.com are :) or :-) 100 are :| 1.1% are :(, #cloud :-D :D"  # noqa
        expected = "<number> <user> of <url> are <smileface> or <smileface> <number> are <neutralface> <number>% are <sadface>, <hashtag> <lolface> <lolface>"  # noqa
        clean = cleanup(string)
        self.assertEqual(clean, expected)

    @patch("analyzer.twit_analysis.TweetTokenizer")
    def test_tokenize(self, mocked_class):
        mocked_instance = MagicMock()
        mocked_class.return_value = mocked_instance
        string = "Dummy things here"
        tokenize(string)
        mocked_class.assert_called_once_with(preserve_case=False)
        mocked_instance.tokenize.assert_called_once_with(string)

    def test_score_tokens(self):
        tokenized = ["this", "is", "a", "test", "89090932"]
        config = load_yaml_config()['func']['score_and_pad_tokens']
        score_mapping = load_json_file(config['score_map_path'])
        model_input_len = config['model_input_len']
        scored = score_and_pad_tokens(tokenized)
        expected = [score_mapping[config['pad']]
                    for i in range(0, model_input_len-len(tokenized))]
        for i in tokenized:
            if i in score_mapping:
                expected.append(score_mapping[i])
            else:
                expected.append(score_mapping[config['unknown']])

        for i,j in zip(expected, scored):
            self.assertEqual(expected, scored)

    def test_get_sentiment(self):
        # confirm that we have a proper prediction type
        res = predict_sentiment([1,2,3])
        self.assertEqual(type(res), numpy.float32)


class TwitProcessingOps(TestCase):

    @patch("analyzer.twit_analysis.time")
    @patch("analyzer.twit_analysis.Chain")
    def test_analyze_and_format(
        self,
        mocked_chain_class,
        mocked_time
    ):
        mocked_pipeline = MagicMock()
        mocked_pipeline.append.return_value = mocked_pipeline
        mocked_pipeline.run = MagicMock(return_value=0.15)
        mocked_chain_class.return_value = mocked_pipeline
        mocked_time.strftime.return_value = "Some date"
        deserialized_twit = {
            'id': 'some_id',
            'text': 'This is the text'
        }
        expected = ["Some date", 'some_id', 'This is the text', 0.15]
        res = analyze_and_format_twit(deserialized_twit)
        self.assertEqual(expected, res)

    def test_deflate_twit(self):
        twit = {
                "data": {
                    "id": "1322200047459528704",
                    "text": "RT @Yu2Fy: @dbongino HUNTER BIDEN SE\u2716\ufe0fTAPE LEAKED!!! CLICK ON LINK\n\nhttps://t.co/UqEpS1AL6Q\n\nHUNTER BIDEN = Pedophilia, Incest, Coke head,\u2026"
                },
                "matching_rules": [
                    {
                        "id": 1322200071375638539,
                        "tag": "null"
                    },
                    {
                        "id": 1322200071375638538,
                        "tag": "null"
                    }
                ]
            }
        serialized = json.dumps(twit)

        deflated = deflate_twit(serialized)
        self.assertDictEqual(deflated, twit['data'])


    def test_store_to_csv(self):
        # manually tested not need to unittest atm.
        pass