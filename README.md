# Overview

Simple logo scraper.

# Usage

Start a nix environment with:

```
nix-shell default.nix
```

or install the following libraries: `beautifulsoup4`, `requests`.

To scrape the websites in `websites.csv`, run with 10 cores, and put the
results in the `results/` directory:

```
python py/logocrawler/driver.py -w websites.csv -c 16 -o results/
```

This will generate two files: `results/results.txt` and `results/candidates.txt`,
`results.txt` has one web resource per line, corresponding to the websites in
`websites.csv`. `candidates.txt` might have multiple web resources per line,
each of which is a different candidate to be the logo.
