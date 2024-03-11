#!/bin/bash
# Last release is 2022-06-02
VERSION=2022-06-02
# Possible names are: metadata.csv | document_parses.tar.gz | cord_19_embeddings.tar.gz
FILE_NAME=metadata.csv
mkdir -p data/raw/$VERSION
wget --directory-prefix data/raw/$VERSION https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/$VERSION/$FILE_NAME

# Full releases have this format: https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_2022-06-02.tar.gz
# Changelogs have this format: https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2022-06-02/changelog