from scraper import InstagramScraper
from dotenv import load_dotenv
import time

if __name__ == "__main__":
    load_dotenv()
    driver = InstagramScraper()
    driver.home_page()
    driver.login()
    time.sleep(30)  # TODO FOR DEBUGGING
    print(driver.current_url)  # TODO FOR DEBUGGING
    # driver.home_page()
    # driver.decline_notifs()

    driver.close()