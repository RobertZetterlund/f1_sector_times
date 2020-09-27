import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import time
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

# since site does not allow webscraping (403) just copy html to file
# http://en.mclarenf-1.com/index.php?page=results&gp=1047&s=7992&p=3

html_file = open('page.html', 'r')
html = html_file.read()

soup = BeautifulSoup(html, 'html.parser')
results = soup.find(id="results")
tbody = results.find("tbody", {"role": "alert"})
content = tbody.findAll("tr")

cols = ["Position", "Driver no.", "Driver",
        "First Sector", "Second Sector", "Third Sector", "Lap Time"]

df = pd.DataFrame(columns=cols)

# only interested in lap time
def removeBrackets(s_times):
    return(list(map(lambda time: time.split(" ", 1)[0], s_times)))

def getSectorTimes(row):
    first = row.findAll("td")
    mylist = list(map(lambda td: td.text, first))
    position, number, name, s_one, s_two, s_three, total = mylist[:7]
    s_one, s_two, s_three = removeBrackets([s_one, s_two, s_three])

    dictionary = {"Position": position, "Driver no.": number, "Driver": name,
                  "First Sector": s_one, "Second Sector": s_two, "Third Sector": s_three, "Lap Time": total}

    df_row = pd.DataFrame(data=dictionary, index=[0])
    
    return df_row


def getDataFrame(content):
    return list(map(lambda tr: getSectorTimes(tr), content))

df_list = getDataFrame(content)

df = pd.concat(df_list).reset_index()

print(df)

