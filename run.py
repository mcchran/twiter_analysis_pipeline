# this one is to archistrate everything ....

import os
import argparse
from analyzer.main import twitter_analysis_pipeline

parser = argparse.ArgumentParser(
    description='Starts the twitter anlysis pipeline. Analysis a stream of the'
    " upcoming twitter feed. Plese consider editting futher information at"
    " env.yml file")

parser.add_argument('--hashtag','-ht', dest="hashtags",
                    metavar="#someHastag",
                    action='append', required=True,
                    help="The hashtags to get twits for. You can append as")

parser.add_argument('--limit', '-l', dest="limit", type=int,
                    default=20, required=False,
                    help="The number of the twits to aggregate")

if __name__ == "__main__":
    arguments = parser.parse_args()
    # check if we the twitter bearer token has registered to the environment
    if not os.environ.get('BEARER_TOKEN'):
        print("Consider submitting an app to twitter. \n"
              "Next you should: export BEARER_TOKEN=<the token>")
        exit(1)
    twitter_analysis_pipeline(arguments.hashtags, arguments.limit)
    exit(0)