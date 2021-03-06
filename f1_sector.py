import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import argparse
import os
import matplotlib.pyplot as plt
from assets.f1colors import f1colors

# Setup argument parser
# since site does not allow webscraping (403) just copy html to file
# http://en.mclarenf-1.com/index.php?page=results&gp=1047&s=7992&p=3
parser = argparse.ArgumentParser(
    description="creates a dataframe given a path to html of a circuit from mclarenf-1.com (http://en.mclarenf-1.com/index.php?page=results&gp=1047&s=7992&p=3)"
)
parser.add_argument("--circuit", type=str,
                    help="folder name of circuit", default="mugello")

args = parser.parse_args()

# setup df
cols = ["Position", "Driver no.", "Driver",
        "First Sector", "Second Sector", "Third Sector", "Lap Time"]
df = pd.DataFrame(columns=cols)

# Setup path
circuit = args.circuit
path = os.path.join("circuits/" + circuit + ".html")

html_file = open(path, 'r')
html = html_file.read()
# get soup
soup = BeautifulSoup(html, 'html.parser')
# get sum of results
sumResults = soup.find({"div"}, id="tabs-0")
# find table with results
results = sumResults.find({"table"}, id="results")
# get table
table = results.find("tbody", {"role": "alert"})
# get all rows
tablerows = table.findAll("tr")

# times are labeled with position "time [x]"", remove brackets and only get time.


def removeBrackets(s_times):
    return(list(map(lambda time: time.split(" ", 1)[0], s_times)))

# Gets relevant data from row


def getSectorTimes(row):
    tableData = row.findAll("td")
    tableDataList = list(map(lambda td: td.text, tableData))
    position, number, name, s_one, s_two, s_three, total = tableDataList[:7]
    s_one, s_two, s_three = removeBrackets([s_one, s_two, s_three])

    dictionary = {"Position": position, "Driver no.": number, "Driver": name,
                  "First Sector": s_one, "Second Sector": s_two, "Third Sector": s_three, "Lap Time": total}

    return pd.DataFrame(data=dictionary, index=[0])


def getDataFrames(tablerows):
    return list(map(lambda row: getSectorTimes(row), tablerows))


listOfDataFrames = getDataFrames(tablerows)
df = pd.concat(listOfDataFrames).reset_index(drop=True)
print(df.to_markdown(index=False))


participants = df.shape[0]

### Setup relative placement at different sections
y = np.arange(1, participants+1, 1)
df = df.sort_values(by="First Sector", ascending=True)
df["relative1"] = y

df = df.sort_values(by="Second Sector", ascending=True)
df["relative2"] = y

df = df.sort_values(by="Third Sector", ascending=True)
df["relative3"] = y


_, ax = plt.subplots()
for _idx, row in df.iterrows():
    driverNmbr = row["Driver no."]
    col = f1colors[driverNmbr]
    r1= -row["relative1"]
    r2= -row["relative2"]
    r3= -row["relative3"]
    plt.plot([1, 2,
              3], [r1, r2, r3], marker='o', linestyle='-', c=col)
    plt.text(0.85, r1 - 0.25, s=driverNmbr, c=col)



### MATPLOTLIB CONFIGURATION
# remove yticks
plt.tick_params(
    axis='y',          
    which='both',      
    left=False,             
    labelleft=False)

plt.xlim(0.8,3.2)
plt.xticks([1,2,3], ["First Sector", "Second Sector", "Third Sector"])

plt.title("Sector placements for " + circuit.capitalize())

# remove framing
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.show()