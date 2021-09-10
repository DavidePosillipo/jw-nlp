#!/bin/bash

createdb -U admin jwnlp

psql -U admin -d jwnlp -f ./db/db_schema.sql 
