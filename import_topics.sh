#!/bin/bash

for file in /data/topics/*.json; do
  mongoimport --host mongodb --db youtube_ai --collection topics --file "$file" --username admin --password password --authenticationDatabase admin
done