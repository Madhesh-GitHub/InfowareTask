from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import os

app = Flask(__name__)

class GoogleMapsScraper:
    def __init__(self, keyword, details_cnt, thread_id):
        self.keyword = keyword
        self.details_cnt = details_cnt
        self.thread_id = thread_id
        self.SOURCE = "Google Maps"
        self.data = []
        self.processed_names = set()

    def initialize_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def find_businesses(self, max_retries=3):
        for _ in range(max_retries):
            try:
                return self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "hfpxzc")))
            except:
                time.sleep(2)
        return []

    def scroll_results(self):
        try:
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

            for _ in range(3):
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
                time.sleep(2)

                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            print(f"Thread {self.thread_id} - Scroll error: {str(e)}")

    def extract_details(self):
         # Extract details with explicit waits
        try:
            name = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf"))).text
        except:
            name = ""

        try:
            rating = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]').text
        except:
            rating = ""

        try:
            review_count = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span').text
        except:
            review_count = ""

        try:
            status = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[4]/div[1]/div[2]/div/span[1]/span/span[1]').text
        except:
            status = ""

        try:
            address = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]/div[1]').text
        except:
            address = ""

        try:
            phone = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[7]/button/div/div[2]/div[1]').text
        except:
            phone = ""

        try:
            website = self.driver.find_element(By.XPATH, "//a[@class='CsEnBe']").get_attribute("href")
        except:
            website = ""

        try:
            area_state = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[8]/button/div/div[2]/div[1]').text
        except:
            area_state = ""

        return {
            "name": name,
            "rating": rating,
            "review_count": review_count,
            "address": address,
            "phone": phone,
            "website": website,
            "status": status,
            "area_state":area_state
        }

    def scrape(self):
        try:
            self.initialize_driver()
            self.driver.get("https://www.google.com/maps")
            time.sleep(3)

            # Search for keyword
            search_box = self.driver.find_element(By.ID, "searchboxinput")
            search_box.send_keys(self.keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            while len(self.data) < self.details_cnt:
                self.scroll_results()
                business_elements = self.find_businesses()

                if not business_elements:
                    print(f"Thread {self.thread_id} - No businesses found for '{self.keyword}', retrying...")
                    time.sleep(2)
                    continue

                for business in business_elements:
                    if len(self.data) >= self.details_cnt:
                        break

                    try:
                        # Get business name and check if already processed
                        current_name = business.get_attribute("aria-label")
                        if not current_name or current_name in self.processed_names:
                            continue

                        # Click on the business
                        self.driver.execute_script("arguments[0].click();", business)
                        time.sleep(3)

                        # Extract business details
                        details = self.extract_details()
                        
                        if details["name"]:
                            self.processed_names.add(details["name"])
                            self.data.append({
                                "Keyword": self.keyword,
                                "Source": self.SOURCE,
                                **details
                            })
                            print(f"Thread {self.thread_id} - Scraped {len(self.data)} businesses for '{self.keyword}'")

                        # Go back to results
                        self.driver.execute_script("window.history.go(-1)")
                        time.sleep(2)

                    except Exception as e:
                        print(f"Error processing business: {str(e)}")
                        self.driver.execute_script("window.history.go(-1)")
                        time.sleep(2)
                        continue

        except Exception as e:
            print(f"Thread {self.thread_id} - Major error: {str(e)}")

        finally:
            self.driver.quit()
            if self.data:
                filename = f"results_{self.keyword}_{self.thread_id}.csv"
                filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
                df = pd.DataFrame(self.data)
                df.to_csv(filename, index=False)
                return filename
            return None

def merge_csv_files(file_list):
    dfs = []
    for file in file_list:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            os.remove(file)
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        output_file = "combined_results.csv"
        combined_df.to_csv(output_file, index=False)
        return output_file
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    keywords = request.form.getlist('keywords[]')
    details_counts = [int(count) for count in request.form.getlist('details_cnt[]')]
    
    # Create tasks from keyword-count pairs
    tasks = list(zip(keywords, details_counts))
    max_threads = min(len(tasks) * 2, 8)  # Maximum 2 threads per keyword, up to 8 total
    
    output_files = []
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for i, (keyword, count) in enumerate(tasks):
            scraper = GoogleMapsScraper(keyword, count, i)
            futures.append(executor.submit(scraper.scrape))
            # Collecting results from all threads
        for future in futures:
            result = future.result()
            if result:
                output_files.append(result)
    
    # Merge all CSV files if any exist
    if output_files:
        final_file = merge_csv_files(output_files)
        return render_template('download.html', file_name=final_file)
    
    return "No data was scraped", 404

@app.route('/download/<file_name>')
def download_file(file_name):
    return send_file(file_name, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)