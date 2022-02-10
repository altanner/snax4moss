"""
~ http://www.medc.dicp.ac.cn/
~ http://159.226.238.174:44333/refsearch.php
~ REFERENCE scraper. You'll need login details, and grab a session
~ cookie to get this to work.
~ Gets all table details for a particular isocode, paginating through
~ all result pages.
~ Saves output as a .csv in ./medc_output
"""

#~ Imports
import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import pickle
from alive_progress import alive_bar

#~ Local file imports
import creds

if not os.path.exists(os.getcwd() + "/medc_output/"):
    print("Making output folder...")
    os.mkdir(os.getcwd() + "/medc_output/")

#~ bring refcode file into list
with open("refcodes2", "r") as infile:
    refcode_list = [line.rstrip() for line in infile]

#~ init the output dataframe
df = pd.DataFrame(columns=["Refcode", "Reference"])

try:
    with alive_bar(len(refcode_list), title="Scraping MEDC refcodes...") as bar:
        for refcode in refcode_list:

            url = f"http://159.226.238.174:44333/refsearch.php?&sql=%20refcode=%20%27{refcode}%27%20"

            #~ get the page
            response = requests.get(url,
                headers=creds.user_agent,
                cookies=creds.cookies,
                auth=HTTPBasicAuth(creds.uname, creds.passw))

            #~ soup the page up
            soup = BeautifulSoup(response.text, "html.parser")

            #~ get the reference
            reference = soup.find("div", {"id": "data"}).text
            reference = re.sub("\r.*?[ ]", "", str(reference)) #~ remove invisible \r

            df.loc[len(df.index)] = [refcode, reference]

            bar()
except Exception as e:
    df.to_csv("./medc_output/medc_refs.csv")
    print(f"Something broke: {e}")

df.to_csv("./medc_output/medc_refs.csv")

print("OK, done, saved to ./medc_outpt/medc_refs.csv")
