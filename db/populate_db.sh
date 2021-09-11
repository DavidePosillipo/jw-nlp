#!/bin/bash

# Insert all the JSON files present in the FOLDER field (and subfolders)
# into the destination database

FOLDER="${folder}"
DATABASE="${database:-jwnlp}"
USER="${user:-admin}"

find "${FOLDER}" -type f -name "*.json" | while read file
do
  echo $file
  # Double quotes and single quotes needed to convert the json into a string, for postgres 
  json_file="'$( jq '.' "${file}" )'"
  psql -c "INSERT INTO watchtowers_articles(data) VALUES($json_file);" -d "${DATABASE}" -U "${USER}" 
done 

# Update the publications table
psql -c """
        UPDATE publications
        SET
            is_batch_downloaded = true,
            last_update = CURRENT_DATE
        WHERE
            name = 'Watchtower'
        ;
        """ -d "${DATABASE}" -U "${USER}" 

