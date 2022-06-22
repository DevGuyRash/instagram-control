from scraper import InstagramScraper
from dotenv import load_dotenv
import time

if __name__ == "__main__":
    load_dotenv()
    driver = InstagramScraper()
    driver.home_page()
    driver.login()
    driver.home_page()

    driver.close()