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

### Design considerations

* Scraper pipeline seperated into three parts
   * The file downloader: Downloads a url and stores the results on disk
   * The parser: Parses a downloaded file and stores the parsed output on disk
   * The processor: Processes a parsed file currently either feeds more urls to the pipeline, or adds the movie to the index
* Each component can be extended or replaced. Multiple parsers and processors can be added
* The scraper can be resumed. This means it can recover from failures which can happen when scraping lots of files
* The movie search has two components
   * The index is based off of tf-idf and is built from processed scraper tasks
   * The search function computes results from the index
   * Both can be modified, replaced or extended

## Todo

* Extend the parser to parse other types of files (scrape all of imdb?)
* Remove in memory state and allow other processes to be run and share state
   * Replace in memory queue w/ message queue
   * Add in a real search indexer (solr)
   * Store intermediate results in an object store (s3)
   * Migrate sqllite to real db (postgres)
* Improve relevance algorithm. Define quality metrics and estimate search quality
* Add logging for analytics
* Extend the parser to parse other types of files (scrape all of imdb?)