import copy

import requests
import re
from urllib.parse import urlparse
import validators
import urllib.parse


spider_tree = dict()
accessed_pages = []
visited_pages = []


def get_matched_hrefs(starting_page, tag, response_text):
    matched_hrefs = re.findall(r'<a[\n]*.*?href=["|\'](.*?)["|\'].*?>', response_text)
    hrefs_list = [starting_page]
    for match in matched_hrefs:
        if match.endswith('/'):
            match = match[:-1]
        if not validators.url(match):
            full_link = urllib.parse.urljoin(starting_page, match)
        else:
            full_link = match

        if match.count(tag) > 0 and full_link not in hrefs_list and 'mailto' not in match:
            hrefs_list.append(full_link)
    return hrefs_list


def spider(starting_page, tag):
    global spider_tree, visited_pages
    if len(starting_page) > 256:
        spider_tree[starting_page] = [0]
        return

    visited_pages.append(starting_page)
    response = requests.get(starting_page)
    print(f"[{response.status_code}] - {starting_page}")
    response_text = response.text
    hrefs_list = get_matched_hrefs(starting_page, tag, response_text)
    print(hrefs_list)
    spider_tree[starting_page] = hrefs_list[1:]
    spider_tree[starting_page].append(len(response_text))


if __name__ == '__main__':
    spider('https://profs.info.uaic.ro/~ciortuz/', "ciortuz")
