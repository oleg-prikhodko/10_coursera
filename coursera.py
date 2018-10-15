import sys

import requests
from bs4 import BeautifulSoup
from lxml import etree


class CourseInfo:
    def __init__(self, title, language, commitment, starts, rating, url):
        self.title = title
        self.language = language
        self.commitment = commitment
        self.starts = starts
        self.rating = rating
        self.url = url

    def __repr__(self):
        return """{}
        Lang: {}
        Comitment: {}
        When: {}
        Rating: {}
        URL: {}
        """.format(
            self.title,
            self.language,
            self.commitment,
            self.starts,
            self.rating,
            self.url,
        )


def get_course_urls(courses_amount=20):
    url = "https://www.coursera.org/sitemap~www~courses.xml"
    response = requests.get(url)
    courses_tree = etree.ElementTree(etree.fromstring(response.content))
    course_urls = [
        element.text
        for element in courses_tree.iter(
            r"{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
        )
    ]
    return course_urls[:courses_amount]


def get_course_info(course_url):
    response = requests.get(course_url)
    soup = BeautifulSoup(response.content, features="lxml")

    title = soup.select_one("h1.title").text
    language = getattr(soup.select_one(".rc-Language"), "text", None)
    commitment = soup.select_one(".cif-clock")
    commitment = (
        commitment.parent.next_sibling.text if commitment is not None else None
    )
    starts = getattr(soup.select_one("#start-date-string"), "text", None)
    rating = getattr(soup.select_one(".ratings-text"), "text", None)

    course_info = CourseInfo(
        title, language, commitment, starts, rating, course_url
    )
    print(course_info)
    return course_info


def output_courses_info_to_xlsx(filepath):
    pass


if __name__ == "__main__":
    try:
        course_urls = get_course_urls()
        course_infos = [
            get_course_info(course_url) for course_url in course_urls
        ]
    except requests.exceptions.RequestException:
        sys.exit("Connection error")
