
#~ Standard library imports
import sys
import os
import time
import datetime
import re
import wget
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


def get_samples_from_category(category, baseurl) -> list:

    """Get the full URL for each sample in a category"""

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

    print(f"{len(sample_list)} sample links retrieved from category {category_name}")

    #~ add to a list of the href URLs
    for sample in sample_list:
        link = sample.text
        links.append(baseurl + "sample/" + link)

    #~ links is a list of all the sample URLs
    return links


def get_dl_links_from_urls(url) -> list:

    """Each page can have one or more spectrum to DL.
    Each _should_ have a counts and a text file, but the text file
    often doesn't exist."""

    dl_links = []

    #~ pull down the category page
    try:
        target = requests.get(
            url, headers=scraper_meta.user_agent).text
    except Exception as e:
        print(f"This request threw an error: {e}")
    #~ init BS object
    soup = BeautifulSoup(target, "lxml")

    #~ retrieve the link text element for all samples in this category
    dl_list = soup.find_all(
        "a", {"class": "sample"}, text=True)

    #~ add to a list of the href URLs
    for dl in dl_list:
        dl_links.append("https://mossbauer.mtholyoke.edu" + dl["href"])

    #~ links is a list of all the sample URLs
    return dl_links


def main():

    try:
        start_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        start_counter = time.perf_counter()

        print(
            f"\n.oO Starting snax4moss @ {start_time} - target base URL is {targets.baseurl}")

        sample_URLs = []
        dl_URLs = []

        #~ build a list of all the sample URLs, for each category
        for category in targets.categories:
            sample_URLs = sample_URLs + get_samples_from_category(category, targets.baseurl)

        #~ then get the downloads for each sample
        # for url in targets.test_targets:
        for url in sample_URLs:
            url = re.sub(" ", "%20", url)
            dl_URLs = dl_URLs + get_dl_links_from_urls(url)

        #~ finally, download the actual files
        working_directory = os.getcwd()
        hits = 0
        misses = 0
        for dl in dl_URLs:
            #~ get the file
            outfile = working_directory + "/output/temp"
            try:
                wget.download(dl, outfile)
                hits += 1
            except Exception as e:
                print(dl, e)
                misses += 1
                continue

            #~ but rename to the first line of the file
            with open(outfile, "r") as f:
                firstline = f.readline().strip()
                firstline = re.sub(" ", "_", firstline)
                firstline = re.sub("/", "-", firstline)
                filetype = re.sub("https://mossbauer.mtholyoke.edu", "", dl)
                filetype = re.sub("/", "_", filetype)
                new_name = working_directory + "/output/" + firstline + filetype
            os.rename(outfile, new_name)

        end_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        end_counter = time.perf_counter()
        elapsed = datetime.timedelta(seconds=(end_counter - start_counter))

        print(f"\n\n.oO OK, finished scrape @ {end_time}, taking {elapsed}")
        print(f".oO {hits} successes, {misses} fails.")

    except KeyboardInterrupt:
        print("\n.oO OK, dropping. That run was not saved.")
        sys.exit(0)


if __name__ == "__main__":

    main()
