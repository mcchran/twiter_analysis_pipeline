import os
import logging
from analyzer.processing_worker import submit_process
from analyzer.twitter_feed import APIFeeder as TwitterFeeder



def twitter_analysis_pipeline(hash_tag_list, limit):
    """ Starts the twitter to worker feed.

    :param list hash_tag_list: the list of hashtags to get twits for
            Hahstags will provide a unit filtering.
    """
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    bearer_token = os.environ.get("BEARER_TOKEN")
    streamer = TwitterFeeder(hash_tag_list, bearer_token)
    streamer.stream_async(
        submit_process.cast,
        limit=limit
    )


if __name__ == "__main__":
    twitter_analysis_pipeline(
        ["#Trump", "#Biden", "#elections", "#trump", "#biden"],
        20
    )

