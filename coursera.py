import argparse
import sys
from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from lxml import etree
from openpyxl import Workbook


class CourseInfo(
    namedtuple(
        "CourseInfo",
        ["title", "language", "commitment", "starts", "rating", "url"],
    )
):
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
    return course_info


def output_courses_info_to_xlsx(course_infos, filepath):
    excel_workbook = Workbook()
    excel_worksheet = excel_workbook.active

    for row, course_info in enumerate(course_infos, start=1):
        for column, attribute in enumerate(course_info, start=1):
            excel_worksheet.cell(row=row, column=column).value = attribute

    excel_workbook.save(filepath)


def load_filepath_from_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath", default="courses.xlsx")
    arguments = parser.parse_args()
    return arguments.filepath


if __name__ == "__main__":
    filepath = load_filepath_from_arguments()
    try:
        course_urls = get_course_urls()
        course_infos = [
            get_course_info(course_url) for course_url in course_urls
        ]
        output_courses_info_to_xlsx(course_infos, filepath)
    except requests.exceptions.RequestException:
        sys.exit("Connection error")
    except FileNotFoundError:
        sys.exit("Incorect filepath")
