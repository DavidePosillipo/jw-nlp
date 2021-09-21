#!/bin/bash

# Insert all the JSON files present in the FOLDER field (and subfolders)
# into the destination database

FOLDER="${1}"
DATABASE="${3}"
USER="${2}"
PASSWORD="${4}"
HOST="${5}"

find "${FOLDER}" -type f -name "*.json" | while read file
do
  echo $file
  # Double quotes and single quotes needed to convert the json into a string, for postgres 
  json_file="'$( jq '.' "${file}" )'"
  PGPASSWORD="${PASSWORD}" psql -c "INSERT INTO watchtowers_articles(data) VALUES($json_file);" -h "${HOST}" -d "${DATABASE}" -U "${USER}" 
done 
