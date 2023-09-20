from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Function to scrape products using Selenium
def scrape_products(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
    options.add_argument("--disable-gpu")  # Disable GPU acceleration

    # Initialize Chrome WebDriver with options
    driver = webdriver.Chrome(options=options)

    # Set an implicit wait to wait for elements to load
    driver.implicitly_wait(10)

    # Open the URL in the WebDriver
    driver.get(url)

    # Scroll down to load more content (you can adjust the number of scrolls)
    num_scrolls = 20
    for _ in range(num_scrolls):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(1)  # Adjust sleep duration as needed

    # Wait for the product elements to be present on the page
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "Label-sc-15v1nk5-0"))
    )

    # Get the page source after scrolling
    page_source = driver.page_source

    # Close the WebDriver
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find and return the product cards
    product_cards = soup.find_all("li", class_=["PaginateItems___StyledLi-sc-1yrbjdr-0", "PaginateItems___StyledLi2-sc-1yrbjdr-1 kUiNOF"])

    return product_cards

# Example usage:
bigbasket_url = 'https://www.bigbasket.com/pc/fruits-vegetables/fresh-vegetables/?nc=ct-fa'
product_cards = scrape_products(bigbasket_url)
print(len(product_cards))
