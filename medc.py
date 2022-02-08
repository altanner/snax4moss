
#~ Imports
import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
import pandas as pd
import re

#~ Local file imports
import creds

page = 1

#~ Make the output dataframe
df = pd.DataFrame(columns=[
    "Isotope", "Source", "Source T", "Absorber", "A Temp",
    "Isomer Shift", "Quad Split", "Comments", "Refcode"])

while page <= 3:
    #~ we'll be paginating on {page}, 1 - 3300
    url = f"http://159.226.238.174:44333/datasearch.php?page={page}&sql=%20AND%20isocode=%20%27fe7%27"

    response = requests.get(url,
        headers=creds.user_agent,
        cookies=creds.cookies,
        auth=HTTPBasicAuth(creds.uname, creds.passw))

    #~ get the page
    soup = BeautifulSoup(response.text, "html.parser")

    #~ get the 2nd table (1st is the left panel)
    hit_table = soup.find_all("table")[1]

    #~ a tr is a row, a td is a cell (ignore header line)
    for tr in hit_table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        this_row = []
        for cell in tds: #? why can I never get BS to strip tags?
            #? seriously, tried everything. all links purple. ffs regexing. I know.
            cell = re.sub("<.?td>", "", str(cell))
            this_row.append(cell)

        df.loc[len(df.index)] = this_row

    page = page + 1

print(df)
