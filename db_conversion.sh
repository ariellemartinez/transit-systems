#!/bin/bash
# ^The above forces our cron process to run this with bash

# We navigate to our scripts folder
cd /www/scripts/transit-systems

# We activate our environment
source env/bin/activate

# To be safe, we run pip install requirements
pip install -r requirements.txt

# We run the scraper, specifying python3 to be safe
python3 app.py

# For each csv file in the folder, we:
# - Add it into a "Transportation.db" in our current working directory. We're
#   doing this for double checking purposes.
# - We do an upload-and-replace the manual way by dropping currently existing tables
#   in our Datasette/Insights platform, and then inserting these tables again
for f in csv/*; do
  echo $(echo $f | sed -e "s/^csv\///" -e 's/\.csv$//'); 
  sqlite-utils insert Transportation.db $(echo $f | sed -e "s/^csv\///" -e 's/\.csv$//') $f --csv
  sqlite-utils drop-table /www/datasette-environment/'Transportation.db' $(echo $f | sed -e "s/^csv\///" -e 's/\.csv$//') --ignore
  sqlite-utils insert /www/datasette-environment/'Transportation.db' $(echo $f | sed -e "s/^csv\///" -e 's/\.csv$//') $f --csv
done
