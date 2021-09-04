meilisearch --http-payload-size-limit=314572800

python jwnlp/search_engine/prepare_files_for_index.py -d data/parsed/

python jwnlp/search_engine/build_index.py -f data/parsed/array_of_docs_to_index.pkl -i "english" -k "article_id"
