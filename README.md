# ADA Project Proposal

> Project proposal for the [ADA course](http://ada.epfl.ch/) at [EPFL](http://epfl.ch).

## Team

- Dylan Bourgeois ([@dtsbourg](https://github.com/dtsbourg))
- Simon Noetzlin ([@SimonNtz](https://github.com/SimonNtz))
- Romain Ruetschi ([@romac](https://github.com/romac))

## Proposal

We propose gathering as much data as we can about GitHub users located in Switzerland, to answer questions such as:

- What is the most popular programming language in Switzerland?
- What are the most popular open-source projects built by developers located in Switzerland?
- Who are the most profilic developers in Switzerland?
- What open-source projects are the most popular in Switzerland?
- Are there any interesting geographical clusters of developers?
- Where are developers located in Switzerland?
- And more…

From a few preliminary GitHub Search queries, we estimate the number of GitHub users who we can locate in Switzerland to be between 15'000 and 20'000. This should hopefully give us enough data to answers the questions above, and hopefully a few more that we have not thought of yet.

This project would involve quite a bit of data retrieval at first, then a fair amount of data processing and code analysis, before leaving us with a lot of visualizations to come up with, such as heat maps, graphs, charts, lists, etc.

## Timeline

We suggest dividing the project into three mostly distinct phases:

### 1. Data Retrieval

In this phase, we collect as much data as possible about GitHub users located in Switzerland. This includes:

- Any public information found in their profile
- Their recent timeline activity
- The list of their repositories
- Number of stars, open/closed issues & pull requests, number of forks, etc.

We see three (non-exclusive) ways to collect this data:

1. By querying the [GitHub API](https://developer.github.com/v3/).
2. By extracting more information from the [GitHub Archive](https://www.githubarchive.org/), which is a project that gathers every public event. Their dataset is available both as a collection of JSON files, or on [Google BigQuery](https://developers.google.com/bigquery/).
3. By scraping the [GitHub Awards](http://github-awards.com/) website, which already offers a list of developers located in Switzerland.

We currently lean on going the #1 way, so as not to rely on the work of others.

### 2. Data Analysis

In this phase, we analyze the raw data we gathered in the previous phase.

For each user, we want to:

- Geocode their location
- Compute the full list of collaborators, across repositories
- Aggregate the total number of stars, issues, etc. across repositories
- Fetch their recent Timeline activity, including opened issues, sent pull requests, code commits, repository creation, etc.

We then plan on cloning every repository, and do additional per-repository processing, such as:

- Guess which programming languages are used
- Compute code-related metrics such as the number of lines of code per language, the overall cyclomatic complexity of the code, etc.
- Extract language-specific data from the repository such as which packages the project depends on, 

It might then be interesting to compute and assign to each user various ratings, for example based on the number of stars they got, or the ratio of open to closed issues, the average cyclomatic complexity of their code, and so on.

### 3. Data Visualization

It is hard to foresee exactly all the ways we could visualize the data and the insights gathered in the previous phases, but some obvious ones come to mind already, such as:

- Map of all the developers
- Heat map of LOC/commits/stars/etc.
- Collaborators graph
- Projects dependencies graph
- List of most popular languages, projects, etc.
- List of most prolific developers
- …

## Technologies and tools

We have not settled on a tech stack yet, but the following tools might prove useful:

### Data retrieval

- Python, Scala, or Haskell

### Data storage

- [MongoDB](https://www.mongodb.com/) + [Quasar](http://quasar-analytics.org/)
- [PostgreSQL](https://www.postgresql.org/)

### Data processing

- [OpenRefine](http://openrefine.org/)
- [Pandas](http://pandas.pydata.org/)

### Code analysis

- loc/cloc
- …

### Visualization

- D3.js or equivalent framework/library
- …
