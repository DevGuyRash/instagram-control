from sessions import InstagramSession
from bs4 import BeautifulSoup


class InstagramBot:

    def __init__(self):
        self.session = InstagramSession()
        self.session.login()

    def get_test_link(self):
        response = self.session.get("https://www.instagram.com/explore/tags/realestatephotography/")
        # response = self.session.get("https://www.instagram.com/")
        return [response, BeautifulSoup(response.text, "html.parser")]


if __name__ == "__main__":
    drive = InstagramBot()
    ret, soup = drive.get_test_link()
    # for item in soup.find_all("link"):
    #     print(item.prettify())
    #     print()

    with open("temp_file.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print(soup.prettify())
    # print(ret.url)