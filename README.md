# Google Trends Scraper

This is a Python-based scraper that collects trending search data from [Google Trends](https://trends.google.com) using Selenium, undetected-chromedriver, and BeautifulSoup. The scraper supports all available categories for any country by modifying the `geo` parameter (e.g., `TR` for Turkey, `US` for United States(editable inside code)).

## 🚀 Features

- Extracts trending keywords for all 24-hour categories(editable inside code)
- Collects trend title, search volume, change direction and percentage, start time, breakdown keywords, and category
- Supports pagination (next pages)
- Headless Chrome scraping via `undetected-chromedriver`
- Exports results to Excel (`.xlsx`)

## 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
undetected-chromedriver==3.5.5
selenium==4.20.0
beautifulsoup4==4.12.3
pandas==2.2.2
openpyxl==3.1.2
```

> ✅ Compatible with Python 3.8–3.11

## 🔧 How to Use

### Run for all categories (default is TR - Turkey):

```python
from trends_scraper import GoogleTrendsScraper

scraper = GoogleTrendsScraper(headless=True)

try:
    scraper.scrape_all_categories()
    scraper.save_to_excel("trending_keywords.xlsx")
finally:
    scraper.close()
```

### Run for a specific category:

```python
scraper = GoogleTrendsScraper()
scraper.scrape_category([7])  # Example: Sports
scraper.save_to_excel("sports_trending.xlsx")
scraper.close()
```

## 📝 Output

The script saves the results to an Excel file containing:

- `Trend`
- `Search Volume`
- `Change` (`+` or `-`)
- `Change Value` (percentage)
- `Started` and `Started Extra`
- `Breakdown Keywords` (related terms)
- `Category`

## 📁 File Structure

```
.
├── trends_scraper.py       # Core scraper class
├── example.py              # Sample usage script
├── requirements.txt
└── README.md
```

## 📄 License

This project is licensed under the MIT License. You are free to use, modify, and distribute it.

## 👨‍💻 Author

Developed by [Barış Uyumaz](https://github.com/barisuyumaz)
