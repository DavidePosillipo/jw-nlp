#!/bin/bash

# Insert all the JSON files present in the FOLDER field (and subfolders)
# into the destination database
#TODO arg for destination db
#TODO arg for destination table

FOLDER="${1}"

find "${FOLDER}" -type f -name "*.json" | while read file
do
  echo $file
  # Double quotes and single quotes needed to convert the json into a string, for postgres 
  json_file="'$( jq '.' "${file}" )'"
  psql -c "INSERT INTO watchtowers_articles(data) VALUES($json_file);" -d jwnlp -U admin
done 


