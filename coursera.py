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


def get_course_urls_from_xml(xml_string, courses_amount=20):
    courses_tree = etree.ElementTree(etree.fromstring(xml_string))
    course_urls = [
        element.text
        for element in courses_tree.iter(
            r"{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
        )
    ]
    return course_urls[:courses_amount]


def get_course_info_from_html(html_string, course_url):
    soup = BeautifulSoup(html_string, features="lxml")

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

    for course_info in course_infos:
        excel_worksheet.append(course_info)

    excel_workbook.save(filepath)


def load_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath", default="courses.xlsx")
    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    filepath = load_arguments().filepath
    xml_feed_url = "https://www.coursera.org/sitemap~www~courses.xml"
    try:
        xml_courses = requests.get(xml_feed_url).content
        course_urls = get_course_urls_from_xml(xml_courses)
        course_infos = [
            get_course_info_from_html(
                requests.get(course_url).content, course_url
            )
            for course_url in course_urls
        ]
        output_courses_info_to_xlsx(course_infos, filepath)
    except requests.exceptions.RequestException:
        sys.exit("Connection error")
    except FileNotFoundError:
        sys.exit("Directory does not exist")
