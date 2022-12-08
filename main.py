import copy
import time
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
    try:
        response = requests.get(starting_page)
        print(f"[{response.status_code}] - {starting_page}")
        response_text = response.text
        hrefs_list = get_matched_hrefs(starting_page, tag, response_text)
        spider_tree[starting_page] = hrefs_list[1:]
        spider_tree[starting_page].append(len(response_text))

        for h in hrefs_list:
            if h not in visited_pages:
                spider(h, tag)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        spider_tree[starting_page] = ["[ERROR]"]


def print_spider_tree(current_key, indent, parents):
    global spider_tree
    indent_tmp = indent
    indent_str = ""
    while indent_tmp:
        indent_str += '----'
        indent_tmp -= 1
    parents_tmp = copy.deepcopy(parents)
    parents_tmp.append(current_key)
    print(f"{indent_str}{current_key} -> {spider_tree[current_key][-1]}")
    for item in spider_tree[current_key][:-1]:
        if len(parents) > 0 and item in parents:
            print(f"{indent_str}----{item} -> {spider_tree[item][-1]} (...infinite loop...)")
        else:
            print_spider_tree(item, indent + 1, parents_tmp)


if __name__ == '__main__':
    time_n = time.time()
    spider('https://profs.info.uaic.ro/~ciortuz/', "ciortuz")
    time_spider = time.time() - time_n
    time_n = time.time()
    print_spider_tree('https://profs.info.uaic.ro/~ciortuz/', 0, [])
    time_print = time.time() - time_n
    print(f"Total time to get all links: {time_spider}")
    print(f"Total time to get the spider structure: {time_print}")
