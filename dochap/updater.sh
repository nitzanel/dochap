#!/bin/bash
# move new read me to old readme
mv db/readme_new db/readme_old
# extract them
#echo "Extracting the files..."
#gunzip db/protein.gbk.gz -f
#echo "Deleting old database..."
#rm db/aliases.db -f
#rm db/comb.db -f
python db_creator.py
#rm db/protein.gbk -f
echo "assigning domains to exons..."
# add column to db
python domains_to_exons.py
echo "Setup complete."

