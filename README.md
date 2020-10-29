A twitter analysis pipeline
============================

THis twit sentiment analysis pipeline should perform as it follows:


1. Fetch twits over the Twitter API v2 in real-time streaming mode.
2. Analyze the fetch twits in real time to extract the sentiment of the twitter (the actor of twitting)
3. Stores those twits into a particular csv file

How to setup
------------

First thing first there are a couple of action required by you dear reader:

1. Installing docker
2. Featuring python 3.7+
3. Feel free to use some kind of virtual environments to avoid spoiling your local setup 

Once you have setup the working environment of yours, you should be able to prepare the app:

3. Install all python requirements by running the following command to the root repo directory:

    ```bash
    $ pip install -r requirements.txt
    ```

4. Install the app itself (it is not already already released -- let's intall that locally in an editable mode)
   Plese proceed once again in the root directory of the repo:
   ```bash
   $ pip install -e .
   ```
   We choose this way to deal with python imports instead of any funny import mess workarounds.
   (In case of any better way please feel free to inform us).

In case of these four steps success you should be able to run the pipeline on your local setup.
FYI in the near future we may provide a complete dockerized version with no installation prerequisites 
but docker and only.

How to use
----------

1. Create a twitter application ... and do fetch the required bearer token. For that you should visit
   the corresponding developer page on [twitter](https://developer.twitter.com/en).
2. Export the token to the `BEARER_TOKEN` environmental variable
   ```bash
   export BEARER_TOKEN=the_provided_token>
   ```
   This is going to be the only environmental variable that the whole system consumes. We prefer that
   way to ensure security either locally or in any cloud provisioned infrastructure.
3. Feel free to explore the config.yaml file. 
  ```yaml
     # env.yml

   # This is the configuration file of the entire pipeline
   # please update all and only the <placeholders> # bellow, 
   # Renaming any variable will cause start up issues ... 

   conf:
       name: twit-sentiment-analysis

       kafka:
           topic: process

   func:
       score_and_pad_tokens:
           score_map_path: ../files/w2i.json
           unknown: "*#*UNK*#*"
           pad: "*#*PAD*#*"
           model_input_len: 20
       
       predict_sentiment:
           model_path: ../files/model.h5

       store_to_csv:
           file_path: ../files/output.csv
           headers:
               - created_at
               - twit_id
               - actual_text
               - sentiment
           delimeter: "|"
           newline: ""
           quote_mark: "'"
           log_on_append: True
  ```

   The file consists of two major components the `conf` which responsible for the overall 
   system configuration and the `func` which sets up all function that constitute the processing
   pipline. At the moment we need to set the:
   output_path:
   ```yaml
    file_path: <relative_path_from_app_root_dir/to_output.csv> 
   ```
   model path:
   ``` yaml
   model_path: <relative_path_from_app_root_dir/to_h5_model.h5>
   ```
   and the w2i mapping path:
   ```yaml
   score_map_path: <relative_path_from_app_root_dir/to_output.csv> 
   ```

Alternatively instead of updating the `config.yaml` you can just create a `files` dir in the root app directory 
and move the model and the w2i files of yours.

4. Start the pipeline worker by typing:
   ```bash 
   chmod +x start_pipeline.sh &./start_pipeline.sh
   ```
5. The command above will start a zookeeper, and kafka worker connected to it, In this setting 
   the current terminal session should be displays the logs of the worker.
   You have to start another terminal re-export the `BEARER_TOKEN` environmental variable of step 1
   and then you can start the pipeline feeder as it follows:
   ```bash
   python run.py -ht "#Trump" -ht "#Biden" -ht "#elections" -ht "#trump" -ht "#biden" --limit 10
   ```
   (Hint: In case of virtual environments use the one you have already setup in the previous steps)

  After a while feel free to check the results in the corresponding output.csv file.
  Hope you enjoy... 
   


Architecture and design
=======================

Architectured to scale
----------------------
Scalability is one of the mojor concerns when considering any streaming processing pipeline.
Here we have employed [Kafka]() a serious message broking service. By using an interesting project
named [faust]() we created a worker to consume messages that have been registered to kafka.
This is the way to create kinda a buffering effect along with multiprocessing design 
(there are multiple other ways to go).
The worker loads the keras model to analyze the streamed twits. Finally it write the results 
to a csv. This sollution should be considered scalable and extensible in terms of adding multiple
workers or even deploying into specialized hardware with ease. 
Of course the code cannot work out of the box to such a deployment at the moment.

(TODO: adding shapes  ... )

Designed to be lean yet extensible
---------------------------------
Extensibility is an interesting concept in the terms or processing pipelines. Here by invoking 
two specialized abstractions the `Chain` and the `config_setup` we can build processing streams with
ease. Thinking of the mathematical notation of functions... (TODO: explantion peding ....) 