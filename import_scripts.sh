#!/bin/bash

for file in /data/scripts/*.json; do
  mongoimport --host mongodb --db youtube_ai --collection scripts --file "$file" --username admin --password password --authenticationDatabase admin
done