import json
import logging
import re
import time
from collections import defaultdict

from nltk.tokenize import TweetTokenizer

from analyzer.utils import (
                                Chain,
                                load_json_file,
                                load_model,
                                config_setup,
                                append_to_csv
                            )

# ==================== Text analyis steps ====================
PATTERNS_BY_CASE = {
    "URL": r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
    "USER": r"@([a-z0-9_]+)",
    "HASHTAG": r"\B(\#[a-zA-Z]+\b)",
    "NUMBER": r"\d+(\.\d+)?",
    "SMILE": r"\:\-?\)",
    "LOL": r"\:\-?D",
    "NEUTRAL": r"\:\|",
    "SADFACE": r"\:\("
}


PLACEHOLDERS_BY_CASE = {
    "URL": "<url>",
    "USER": "<user>",
    "HASHTAG": "<hashtag>",
    "NUMBER": "<number>",
    "SMILE": "<smileface>",
    "LOL": "<lolface>",
    "NEUTRAL": "<neutralface>",
    "SADFACE": "<sadface>"
}


def cleanup(sample):
    """ Given a string clean should:
        1. pick substrings featuring a special pattern
        2. replace those strings with the predefined placeholder

    :param str sample:The piece of text to clean up
    :rtype: string
    :returns: the cleaned up string
    """
    clean_up_pipeline = Chain(logging.exception)

    def apply(case): return lambda text: re.sub(
                PATTERNS_BY_CASE[case],
                PLACEHOLDERS_BY_CASE[case],
                text)

    for case in PATTERNS_BY_CASE:
        clean_case = apply(case)
        clean_up_pipeline.append(
            clean_case
        )
    return clean_up_pipeline.run(sample)


def tokenize(sample):
    """ Tokenizes any text sample

    :param str sample: Te string to tokenize

    :returns: a list of the exporetd tokens
    :rtype: list
    """
    tknzr = TweetTokenizer(preserve_case=False)
    return tknzr.tokenize(sample)


@config_setup("score_and_pad_tokens")
def score_and_pad_tokens(token_list,
                         score_map_path,
                         unknown,
                         pad,
                         model_input_len):
    """ The function is highly related to the file under SCORE_MAP_PATH

    :param list token_list: the list of the tokenized string terms
    :param string score_map_path: the map of the score mapping file
    :param string unknown: the key of the value of an unknown string
                    in score_map
    :param string pad: the key of the pading symbol in score_map
    :param int model_input_len: the length of the input model

    :returns: a list of integers featuring model_input_len
    :rtype: list
    """
    # low level optimization using static and default dict
    if not hasattr(score_and_pad_tokens, "score_map"):
        score_and_pad_tokens.score_map = load_json_file(score_map_path)
        score_and_pad_tokens.score_map = defaultdict(
                    lambda: score_and_pad_tokens.score_map[
                        unknown
                    ],
                    score_and_pad_tokens.score_map
                )
    score_list = [score_and_pad_tokens.score_map[i] for i in token_list]
    for i in range(0, model_input_len-len(score_list)):
        score_list.insert(0, score_and_pad_tokens.score_map[pad])
    return score_list


@config_setup("predict_sentiment")
def predict_sentiment(mapped_token_list, model_path):
    """ Invokes a keras model to predict sentiment analysis of a scored token

    :param list mapped_token_list: the scored and padded tokens
    :param string model_path: the path to load the model h5 keras model
    :rtype: int
    :returns: the model prediction for the specific sentiment
    """
    if not hasattr(predict_sentiment, "model"):
        predict_sentiment.model = load_model(model_path)

    #  the double zeros in the end are a way of deflation ....
    return predict_sentiment.model.predict([mapped_token_list])[0][0]


# ==================== Twit analyis steps ====================
def analyze_and_format_twit(deserialized_twit):
    """ Performs the wit analysis

    :rtype: list
    :retrunsL a list-entry ready to be stored tp the csv
    """
    sentiment_pipeline = Chain(
                                logging.exception
                          ).append(
                                cleanup
                          ).append(
                               tokenize
                          ).append(
                              score_and_pad_tokens
                          ).append(
                              predict_sentiment
                          )

    return [
            time.strftime("%d-%m-%Y %H:%M:%S"),
            deserialized_twit["id"],
            deserialized_twit["text"],
            sentiment_pipeline.run(deserialized_twit["text"])
           ]


def deflate_twit(serialized_twit):
    return json.loads(serialized_twit)["data"]


# ==================== Twit analyis steps ====================
@config_setup("store_to_csv")
def store_to_csv(entry,
                 file_path,
                 headers,
                 delimeter,
                 newline,
                 quote_mark,
                 log_on_append=None):
    """ Stores the results of the twitter analysis to a csv

    A wrapper of the corresponding utility function to increase performance
    and flexibility.

    :param list entry: a new entry line to store into the csv
    :param string file_path: the path to the output csv file
    :param string headers: the header of that file
    :param string delimeter: delimeter to use while writting csv
    :param string newline: new line symbol
    :param string quote_mark: csv entry quotations
    :param bool log_on_append: True to append extra to the new files

    :rtype: func evaluation
    """
    if not hasattr(store_to_csv, "intialized_file"):
        # set file headers
        append_to_csv(
                    entry=headers,
                    file_path=file_path,
                    delimeter=delimeter,
                )
        store_to_csv.intialized_file = True

    return append_to_csv(
                    entry=entry,
                    file_path=file_path,
                    newline=newline,
                    delimeter=delimeter,
                    quotechar=quote_mark,
                    log=log_on_append
                )


# ==================== Pipeline Interface ====================
def make_pipeline():
    """ Constrcts the final pipeline to analyze and store any twit

    :rtype Chain object:
    """
    return Chain(logging.exception).append(
                                                deflate_twit
                                            ).append(
                                                analyze_and_format_twit
                                            ).append(
                                                store_to_csv
                                            )