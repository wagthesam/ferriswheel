# IMDB Search

A web crawler and search interface.

## Getting Started

### Installing & Running

To run the application, we need to install the required python packages. After that is done, just run run.py.

```
pip install -r requirements.txt
python run.py
```

### Running a search query

```
app.search('harrison ford')
```

### Simplifying assumptions

* A first stab approach at tf-idf was used for search relevance. Document size is small so don't need to be too precise w/ ranking
* We only use movie titles, director, stars, actors, and characters for the text per document. We did not include descriptions to simplify the task
* We only return movie titles, and have a command line UI 

### Design considerations

* Scraper pipeline seperated into three parts
   * The file downloader: Downloads a url and stores the results on disk
   * The parser: Parses a downloaded file and stores the parsed output on disk
   * The processor: Processes a parsed file currently either feeds more urls to the pipeline, or adds the movie to the index
* We persist scraper results to disk so that we don't have to run the scraper every time
* Each component can be extended or replaced. Multiple parsers and processors can be added
* The scraper can be resumed. This means it can recover from failures which can happen when scraping lots of files
* The movie search has two components
   * The index is based off of tf-idf and is built from processed scraper tasks
   * The search function computes results from the index
   * Both can be modified, replaced or extended

## Todo

* Allow this to be run as a service by exposing REST or SOAP api endpoints, so that it can be plugged into another system
* Extend the parser to parse other types of files (scrape all of imdb?), to increase docs that users can search
* Scale horizontally by removing in memory state and allow other processes to be run and share state, so that this can support many users
   * Replace in memory queue w/ message queue
   * Add in a real search indexer (solr)
   * Store intermediate results in an object store (s3)
   * Migrate sqllite to real db (postgres)
* Improve output, right now we are just returning movie titles
* Improve relevance algorithm
* Add logging for analytics
* Add unit and functional tests to make changes safer