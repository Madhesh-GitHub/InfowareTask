"""
This Python script uses Selenium to scrape product details from multiple Amazon bestseller categories. 
The extracted details include product names, prices, ratings, links, seller information, discounts, and product image URLs. 
Each category's data is saved to a separate CSV file.

Work Flow:
1. Opens Each Category Link: Visits URLs provided in the `category_links` list.
2. Extracts Data: Scrapes product names, prices, ratings, links, and additional details like shipping info, seller, discounts, and image URLs by navigating individual product pages.
3. Handles Errors: Skips missing data without stopping the program.
4. Saves to CSV: Stores all scraped details for each category in separate CSV files.
5. Automates Browser Actions: Uses Selenium's WebDriver to interact with the webpage.

Therefore, It efficiently collects and organizes e-commerce data in an automated way.

"""


import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Initialize Chrome options and set the browser to remain open after execution
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Create the WebDriver instance with the specified options
driver = webdriver.Chrome(options=chrome_options)

# List of category links for scraping. You can add more as needed.
category_links = [
    "https://www.amazon.in/gp/bestsellers/watches/ref=zg_bs_watches_sm",
    "https://www.amazon.in/gp/bestsellers/home-improvement/ref=zg_bs_home-improvement_sm",
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_kitchen_sm",
    "https://www.amazon.in/gp/bestsellers/apparel/ref=zg_bs_apparel_sm",
    "https://www.amazon.in/gp/bestsellers/luggage/ref=zg_bs_luggage_sm",
    "https://www.amazon.in/gp/bestsellers/beauty/ref=zg_bs_beauty_sm",
    "https://www.amazon.in/gp/bestsellers/sports/ref=zg_bs_sports_sm",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_electronics_sm",
    "https://www.amazon.in/gp/bestsellers/hpc/ref=zg_bs_hpc_sm",
    "https://amazon.in/gp/bestsellers/office/ref=zg_bs_office_sm"
]

# Iterate through each category link for data scraping
for category_link in category_links:
    driver.get(category_link)  # Navigate to the category page
    time.sleep(3)  # Wait for the page to load

    # Initialize lists to store product details
    product_names = []
    product_prices = []
    product_ratings = []
    product_links = []
    ships_from_list = []
    sold_by_list = []
    discount_list = []
    image_links = []

    try:
        # Extract product names and their links
        products = driver.find_elements(By.CLASS_NAME, value="_cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
        prices = driver.find_elements(By.CLASS_NAME, value="_cDEzb_p13n-sc-price_3mJ9Z")
        ratings = driver.find_elements(By.CLASS_NAME, "a-link-normal")

        for product in products:
            # Retrieve parent anchor tag for the product link
            parent_link = product.find_element(By.XPATH, "./ancestor::a")
            link = parent_link.get_attribute("href")
            product_links.append(link)
            # Clean and store the product name
            name = "".join(product.text.split(',')[0])
            product_names.append(name)

        # Store product prices
        for price in prices:
            product_prices.append(price.text)

        # Store product ratings and review counts
        for rating in ratings:
            title = rating.get_attribute("title")
            if title and "out of 5 stars" in title:
                rating_value = title.split(",")[0]
                review_count = title.split(",")[1].strip()
                product_ratings.append((rating_value, review_count))

        # Extract additional details for each product link
        for link in product_links:
            try:
                driver.get(link)
                time.sleep(3)  # Wait for the product page to load

                # Extract "Ships from" information
                try:
                    ships_from = driver.find_element(By.XPATH, "//div[@class='tabular-buybox-text']//span[@class='a-size-small tabular-buybox-text-message']").text
                except Exception:
                    ships_from = "Amazon"  # Default value if not found

                # Extract "Sold by" information
                try:
                    sold_by = driver.find_element(By.XPATH, "//a[@id='sellerProfileTriggerId']").text
                except Exception:
                    sold_by = "Not Available"

                # Extract discount percentage
                try:
                    discount = driver.find_element(By.XPATH, "//span[@class='a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage']").text
                except Exception:
                    discount = "Not Available"

                # Extract product image URL
                try:
                    image_url = driver.find_element(By.XPATH, "//div[@id='imgTagWrapperId']//img[@id='landingImage']").get_attribute('src')
                except Exception:
                    image_url = "Not Available"

                # Append extracted details to the respective lists
                image_links.append(image_url)
                ships_from_list.append(ships_from)
                sold_by_list.append(sold_by)
                discount_list.append(discount)

            except Exception as e:
                print(f"Error processing link {link}: {e}")

    except Exception as e:
        print(f"Error loading category page {category_link}: {e}")

    # Save extracted data to a CSV file for the current category
    category_name = category_link.split("/")[-2]  # Extract category name from the link
    filename = f"{category_name}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Define the CSV column headers
        fieldnames = ['Category', 'Product Name', 'Price', 'Rating', 'Link', 'Ships From', 'Sold By', 'Discount', 'Image URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write headers to the CSV file
        writer.writeheader()
        # Write product details row by row
        for i in range(len(product_names)):
            writer.writerow({
                'Category': f"{category_name}",
                'Product Name': product_names[i],
                'Price': product_prices[i],
                'Rating': product_ratings[i] if i < len(product_ratings) else 'Not Available',
                'Link': product_links[i],
                'Ships From': ships_from_list[i] if i < len(ships_from_list) else 'Amazon',  # Default to Amazon
                'Sold By': sold_by_list[i] if i < len(sold_by_list) else 'Not Available',
                'Discount': discount_list[i] if i < len(discount_list) else 'Not Available',
                'Image URL': image_links[i] if i < len(image_links) else 'Not Available'
            })

    print(f"Data for category '{category_name}' saved successfully!")

# Close the WebDriver instance
driver.quit()

print("All category data extraction completed successfully!")



#  login code
# try:
#     # Step 1: Open Amazon's login page
#     driver.get("https://www.amazon.in/ap/signin")
#     driver.maximize_window()
#     time.sleep(2)  # Wait for the page to load

#     # Step 2: Enter your email or phone number
#     email_input = driver.find_element(By.ID, "ap_email")
#     email_input.send_keys("your_email@example.com")  # Replace with your email
#     email_input.send_keys(Keys.RETURN)
#     time.sleep(2)

#     # Step 3: Enter your password
#     password_input = driver.find_element(By.ID, "ap_password")
#     password_input.send_keys("your_password")  # Replace with your password
#     password_input.send_keys(Keys.RETURN)
#     time.sleep(3)

#     # Step 4: Confirm login
#     print("Login successful! Check the browser window.")
# except Exception as e:
#     print(f"Error occurred: {e}")
