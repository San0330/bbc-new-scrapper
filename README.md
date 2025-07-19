# BBC Nepali News Scraper

This project scrapes news articles from [bbc.com/nepali](https://www.bbc.com/nepali) and saves them into a structured CSV file. It also provides a utility to fix datetime issues in the scraped data.

## Features
- Scrapes articles from multiple categories (नेपाल, विश्व, स्वास्थ्य, विज्ञान तथा प्रविधि)
- Extracts article ID, URL, category, date, title, summary, and full text
- Avoids duplicate articles and updates categories for existing articles
- Handles edge cases in summary and text extraction
- Saves all data to a CSV file (`scraped_articles.csv`)
- Provides a script to fix malformed datetime values by re-fetching the correct datetime from the article page

## Requirements
- Python 3.7+
- The following Python packages:
  - `requests`
  - `beautifulsoup4`
  - `pandas`

Install dependencies with:
```bash
pip install pandas requests beautifulsoup4
```

## Setup
1. Clone or download this repository.
2. Ensure you have the required dependencies installed (see above).

## Usage

### 1. Scrape Articles
Run the main scraper to collect articles and save them to `scraped_articles.csv`:
```bash
python scrapper.py
```
- The script will crawl all configured categories and pages, extract article data, and save it to the CSV file.
- It will skip already-scraped articles and update categories if an article appears in multiple sections.

### 2. Fix Datetime Issues
Previously some articles had issues with datetime value, which is now fixed in modern scraper script and existing data.
If some rows in `scraped_articles.csv` have a `date` value starting with `PT` (malformed), you can fix them by running:
```bash
python fixdatetime.py
```
- This script will:
  - Find all rows where the `date` starts with `PT`
  - Visit each article URL and extract the correct datetime (from a `<time>` tag not inside a `<figure>`)
  - Update the DataFrame and save the corrected data back to `scraped_articles.csv`

## Output
- The main output is `scraped_articles.csv`, containing columns:
  - `id`, `url`, `category`, `date`, `title`, `summary`, `text`
- The file can be opened in Excel, LibreOffice, or processed with pandas for further analysis.

## Notes
- Be respectful to the BBC servers: the scraper includes a delay between requests, but avoid running it too frequently.
- If you encounter connection issues or changes in the BBC website structure, you may need to update the scraping logic.
- The scripts are designed for research and educational purposes only.

