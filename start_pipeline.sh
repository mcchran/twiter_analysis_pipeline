#!/bin/bash
echo " -- Let's setup the stream processing pipeline"
# should check the setup also
echo " -- First things first we should perform some testing"
python -m unittest discover -v tests/
docker-compose up -d
sleep 8
cd analyzer
faust -A processing_worker worker -l info
sleep 4
echo " -- Wiping containers out"
docker-compose stop
sleep 4
docker-compose rm
