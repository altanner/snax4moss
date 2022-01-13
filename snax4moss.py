
#~ Standard library imports
import sys
import time
import datetime
import re
from random import randint

#~ 3rd party imports
import requests
from pathlib import Path
from retry import retry
import pandas as pd
from bs4 import BeautifulSoup
from alive_progress import alive_bar
import lxml      # alt to html.parser, with cchardet >> speed up
import cchardet  # character recognition

#~ Local imports
import targets       # this will be the template in published version
import scraper_meta  # things like user agents, in case we need to rotate


def get_samples_from_category(category, baseurl) -> pd.Series:

    """Get the full URL for each sample in a category

    Args: a category and baseURL from targets.py
    Rets: a pandas series of the product URLs"""

    links = []
    #~ the final section of the category URL
    category_name = category.split("/")[-1]

    #~ pull down the category page
    category_page = baseurl + category
    try:
        target = requests.get(
            category_page, headers=scraper_meta.user_agent).text
    except Exception as e:
        print(f"This request threw an error: {e}")
    #~ init BS object
    soup = BeautifulSoup(target, "lxml")

    #~ retrieve the link text element for all samples in this category
    sample_list = soup.find_all(
        "a", {"class": "sl"}, text=True)

    print(f"{len(sample_list)} links retrieved from category {category_name}")

    #~ add to a list of the href URLs
    for sample in sample_list:
        link = sample.text
        links.append(baseurl + "sample/" + link)

    #~ links is a list of all the sample URLs
    return links


def main():

    try:
        start_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        start_counter = time.perf_counter()

        print(
            f"\n.oO Starting snax4moss @ {start_time} - target base URL is {targets.baseurl}")

        full_URLs = []

        #~ make a list of all the sample URLs, for each category
        for category in targets.categories:
            full_URLs = full_URLs + get_samples_from_category(category, targets.baseurl)
            print(len(full_URLs))

        end_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        end_counter = time.perf_counter()
        elapsed = datetime.timedelta(seconds=(end_counter - start_counter))

        print(f".oO OK, finished scrape @ {end_time}, taking {elapsed}")

    except KeyboardInterrupt:
        print("\n.oO OK, dropping. That run was not saved.")
        sys.exit(0)


if __name__ == "__main__":

    main()
