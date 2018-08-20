Version 0.1

Design decisions
- Extendible design
    - Can add extra parsers per fetched page
    - Can modify / add more fields from details page to store, and 
      change how it impacts searches
- Resumable scrapes makes larger fetches more resilient to failures

Todo
- Allow this application to run on many machines
    - Replace queue w/ message queue
    - Replace in memory search index w/ one stored in a database
    - Set up s3 instead of using local disc to store intermediate results

Run guide
- pip install -r requirements.txt
- python run.py