import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc


class GoogleTrendsScraper:
    def __init__(self, headless=True):
        self.options = uc.ChromeOptions()
        if headless:
            self.options.headless = True
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.driver = uc.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 5)
        self.data = []

    def _wait_for_content(self):
        def condition(driver):
            elems1 = driver.find_elements(By.CSS_SELECTOR, "div.mZ3RIc")
            elems2 = driver.find_elements(By.CSS_SELECTOR, "div.ufsDkb")
            return elems1 if elems1 else elems2 if elems2 else False

        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.wait.until(condition)

    def _scroll_to_row(self, scrollable_div, tr_index, max_scroll, total_rows):
        if max_scroll > 600:
            scroll_pos = tr_index * (max_scroll // total_rows)
            self.driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_div, scroll_pos)
            time.sleep(0.15)

    def _extract_category(self, soup):
        tags = soup.find_all("span", {"class": "AeBiU-vQzf8d", "jsname": "V67aGc"})
        return tags[2].text.replace("\u25be", "").replace("\xa0", "") if len(tags) > 2 else None

    def _click_more_button(self, current_tr):
        try:
            more_button = current_tr.find_element(By.CSS_SELECTOR, "span.Gwdjic")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
            time.sleep(0.2)
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.Gwdjic")))
            self.driver.execute_script("arguments[0].click();", more_button)
            time.sleep(0.3)
            return True
        except Exception:
            return False

    def _extract_trend_data(self, tr, current_tr, category):
        tds = tr.find_all("td", recursive=False)
        trend = tds[1].find("div", class_="mZ3RIc").get_text(strip=True)
        search_vol = tds[2].find("div", class_="lqv0Cb").get_text(strip=True)

        extras = tds[2].find("div", class_="wqrjjc")
        situation = extras.find("i").get_text(strip=True).replace("arrow_upward", "+").replace("arrow_downward", "-") if extras else None
        change_val = extras.find("div").get_text(strip=True) if extras else None

        started = tds[3].find("div").get_text(strip=True)
        started_extra = tds[3].find("div", class_="UQMqQd").find("div").find("div").get_text(strip=True)

        breakdown = []
        trend_tag = tds[4].find("div", class_="k36WW")
        if trend_tag:
            breakdown += [x.find("span", {"jsname": "V67aGc"}).get_text(strip=True) for x in trend_tag.find_all("div", recursive=False)]

            if self._click_more_button(current_tr):
                try:
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jsaction="JIbuQc:VTVhdd"]')))
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, 'span.GDLTpd[jsname="GG0bEb"]').click()
                        time.sleep(1)
                    except NoSuchElementException:
                        pass
                    spans = self.driver.find_elements(By.CSS_SELECTOR, 'span[jsname="V67aGc"].mUIrbf-vQzf8d')
                    breakdown = [el.text.strip() for el in spans if el.text.strip()][3:]
                    self.driver.find_element(By.CSS_SELECTOR, 'div[jsaction="JIbuQc:TvD9Pc"]').click()
                except TimeoutException:
                    pass
        return {
            "Trend": trend,
            "Search Volume": search_vol,
            "Change": situation,
            "Change Value": change_val,
            "Started": started,
            "Started Extra": started_extra,
            "Breakdown Keywords": breakdown or None,
            "Category": category
        }

    def scrape_category(self, category_id):
        url = f"https://trends.google.com/trending?geo=TR&category={category_id}&hours=24&sort=search-volume"
        self.driver.get(url)
        self._wait_for_content()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        if not soup.find("div", class_="mZ3RIc"):
            print(f"No keywords found for category {category_id}")
            return

        next_page = True
        while next_page:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            category = self._extract_category(soup)
            tbody = soup.find("tbody", {"jsname": "cC57zf"})
            tbody_elem = self.driver.find_element(By.CSS_SELECTOR, "tbody[jsname='cC57zf']")
            rows_elem = self.driver.find_elements(By.CSS_SELECTOR, "tbody[jsname='cC57zf'] tr[jsname='oKdM2c']")
            rows_tag = tbody.find_all("tr", {"jsname": "oKdM2c"})

            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "div[jsname='U2ZH0b']")
            max_scroll = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

            for tr_index, tr in enumerate(rows_tag):
                self._scroll_to_row(scrollable_div, tr_index, max_scroll, len(rows_tag))
                row_data = self._extract_trend_data(tr, rows_elem[tr_index], category)
                print(row_data)
                self.data.append(row_data)

            next_button = soup.select("div.enOdEe-wZVHld-gruSEe-yXBf7b span[data-is-tooltip-wrapper='true'] button")
            if next_button and next_button[2].has_attr("disabled"):
                next_page = False
            else:
                self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.CSS_SELECTOR, "button[jsname='ViaHrd']"))
                time.sleep(1)

    def scrape_all_categories(self, category_ids=None):
        category_ids = category_ids or list(range(1, 20))
        for category_id in category_ids:
            self.scrape_category(category_id)

    def save_to_excel(self, filename="trending_keywords.xlsx"):
        df = pd.DataFrame(self.data)
        df.to_excel(filename, index=False)
        print(f"Data saved to {filename}")

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    scraper = GoogleTrendsScraper(headless=True)
    try:
        scraper.scrape_all_categories()
        scraper.save_to_excel()
    finally:
        scraper.close()
