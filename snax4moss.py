
#~ Standard library imports
import sys
import os
import time
import datetime
import re
import argparse
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


def args_setup():

    parser = argparse.ArgumentParser(
        description = "Mt Holyoke Mossbauer Spectra Scraper",
        epilog = "Example: python snax4moss.py --fetch")
    parser.add_argument(
        "--fetch", action = "store_true",
        help = "Get the URLs from target site..")
    parser.add_argument(
        "--local", action = "store_true",
        help = "Use the locally stored list of URLs in dl_URLs")

    args = parser.parse_args()

    return parser, args


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

    parser, args = args_setup()

    if not any([args.fetch, args.local]):
        print("Should I fetch or use a local file [dl_URLs]?")
        sys.exit(0)

    if not os.path.exists(os.getcwd() + "/output/"):
        print("Making output folder...")
        os.mkdir(os.getcwd() + "/output/")

    try:
        start_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        start_counter = time.perf_counter()

        print(
            f"\n.oO Starting snax4moss @ {start_time} - target base URL is {targets.baseurl}")

        if args.fetch:
            sample_URLs = []
            dl_URLs = []

            #~ build a list of all the sample URLs, for each category
            with alive_bar(
                len(targets.categories),
                title="Scraping categories for samples...") as bar:
                for category in targets.categories:
                    sample_URLs = sample_URLs + get_samples_from_category(
                        category, targets.baseurl)
                    bar()
            print(f".oO {len(sample_URLs)} URLs to scrape...")

            #~ then get the downloads for each sample
            with alive_bar(len(sample_URLs),
                title="Getting and cleaning URLs...",
                title_length=34) as bar:
                for url in sample_URLs:
                    #~ spaces and hashes in URLs need reformatting
                    url = re.sub(" ", "%20", url)
                    url = re.sub("#", "%23", url)
                    dl_URLs = dl_URLs + get_dl_links_from_urls(url)
                    bar()

            with alive_bar(len(dl_URLs),
                title="Writing URLs to file...",
                title_length=34) as bar:
                with open("dl_URLs", "w") as DL_file:
                    for thing in dl_URLs:
                        DL_file.writelines(thing + "\n")
                        bar()

        if args.local:
            with open("dl_URLs", "r") as urls:
                dl_URLs = urls.readlines()
                dl_URLs = [x.strip() for x in dl_URLs]

        #~ finally, download the actual files
        hits = 0
        misses = 0

        with alive_bar(len(dl_URLs),
            title="Requesting files...",
            title_length=34) as bar:

            outfile = os.getcwd() + "/output/temp"
            for dl in dl_URLs:
                #~ get the file
                try:
                    incoming = requests.get(dl)
                    if incoming.status_code == 200:
                        with open(outfile, "w") as savefile:
                            savefile.write(incoming.text)
                        hits += 1
                    else:
                        misses += 1
                        continue
                        bar()
                except Exception as e:
                    print(e)
                    continue
                    bar()

                #~ but rename to the first line of the file
                with open(outfile, "r") as f:
                    firstline = f.readline().strip()
                    firstline = re.sub(" ", "_", firstline)
                    firstline = re.sub(r"[^a-zA-Z0-9_]", "", firstline)
                    filetype = re.sub("/", "_", dl) # append datafile or textfile?
                    filetype = re.sub("https:__mossbauer.mtholyoke.edu", "", filetype)
                    new_name = os.getcwd() + "/output/" + firstline + filetype
                os.rename(outfile, new_name)
                bar()

        end_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        end_counter = time.perf_counter()
        elapsed = datetime.timedelta(seconds=(end_counter - start_counter))

        print(f"\n\n.oO OK, finished scrape @ {end_time}, taking {elapsed}")
        print(f".oO {hits} successes, {misses} fails.")

    except KeyboardInterrupt:
        print("\n.oO OK, dropping.")
        sys.exit(0)


if __name__ == "__main__":

    main()
