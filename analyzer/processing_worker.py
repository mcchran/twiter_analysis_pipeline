import faust
import logging
from analyzer.twit_analysis import make_pipeline
from analyzer.utils import append_to_csv, Chain, load_yaml_config

# setting up the kafka worker connection

app = faust.App(
    "stream_processor",
    broker="kafka://localhost:9092",
    value_serializer="raw",
)
process_topic = app.topic(load_yaml_config()["conf"]["kafka"]["topic"])

# the agent writes, we cannot have concurrency>1 in that case
@app.agent(process_topic, concurrency=1)
async def submit_process(samples):
    """ Gets a set of sample to apply pipeline to.
    A decorated function ready to perfrom in the faust worker context.

    :param list samples: list of serialized objects, twits in our case
    """
    # low level performance boost
    if not hasattr(submit_process, "pipeline"):
        submit_process.pipeline = make_pipeline()
    async for sample in samples:
        submit_process.pipeline.run(sample)
