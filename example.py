from googletrends_scraper import GoogleTrendsScraper

scraper = GoogleTrendsScraper(headless=True)
try:
    scraper.scrape_all_categories()
    scraper.save_to_excel("trending_keywords.xlsx")
finally:
    scraper.close()
