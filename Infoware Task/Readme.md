# Amazon web scraper

This is my internship selection project at Infoware India company.

This project's Python script uses Selenium to scrape product details from multiple Amazon bestseller categories. 
The extracted details include product names, prices, ratings, links, seller information, discounts, and product image URLs. 
Each category's data is saved to a separate CSV file.

**Work Flow:**
1. Opens Each Category Link: Visits URLs provided in the `category_links` list.
2. Extracts Data: Scrapes product names, prices, ratings, links, and additional details like shipping info, seller, discounts, and image URLs by navigating individual product pages.
3. Handles Errors: Skips missing data without stopping the program.
4. Saves to CSV: Stores all scraped details for each category in separate CSV files.
5. Automates Browser Actions: Uses Selenium's WebDriver to interact with the webpage.

Therefore, It efficiently collects and organizes e-commerce data in an automated way.
