"""Define functions"""

import re
import pandas as pd
import numpy as np
import json
from io import StringIO
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup


RIVM_INFO_PAGE = "https://www.volksgezondheidenzorg.info"
DUTCH_MONTH = {
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12",
}
YEAR = "2020"


def get_coronavirus_info_nl(info_link):
    """
    Get the coronavirus information from RIVM website.
    @return:
    csv_link: str, The csv download link
    csv_update_date: str, The date at which csv is updated
    """
    coronavirus_info_page = urlopen(info_link).read().decode("utf-8")
    soup_pattern = soup(coronavirus_info_page, features="lxml")

    # Find out this pattern by reading the source code of the page
    csv_download_class = soup_pattern.find("a", {"class": "csv-export detail-data"})

    # Get the csv link
    csv_link = RIVM_INFO_PAGE + csv_download_class.get("href")

    # Get the update date from the link
    csv_update_date = re.search(r"([0-9]{8})", csv_link)[0]
    csv_update_date = csv_update_date[4:] + csv_update_date[2:4] + csv_update_date[0:2]

    # Get the current time to get this information
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")

    # Print the result
    print(f"csv link:{csv_link}")
    print(f"csv update date:{csv_update_date}")

    return csv_link, csv_update_date


def save_info_nl(csv_link, csv_update_date):
    """
    Preprocess the data and save it as a csv file.
    """

    info_str = urlopen(csv_link).read().decode("utf-8")

    # Load the string into dataframe
    info_df = pd.read_csv(StringIO(info_str), sep=";")

    # Preprocess the dataframe
    info_df.dropna(inplace=True)
    info_df.reset_index(drop=True, inplace=True)
    KEEP_COLs = ["id", "Gemeente", "Aantal"]
    info_df = info_df[KEEP_COLs]

    # Make it consistent with the info of Dutch municipalities
    info_df.rename(
        columns={"Aantal": "Number", "id": "City_code", "Gemeente": "City"},
        inplace=True,
    )

    # if this column is string then transform it into integer
    if info_df["City_code"].dtype != np.dtype("int64"):
        info_df["City_code"] = info_df["City_code"].apply(
            lambda x: x if "," not in x else x.split(",")[0]
        )

    # Add the Province column
    dutch_info = pd.read_csv("./data/Dutch_municipalities_2020.csv")
    KEEP = ["Province", "City"]
    dutch_info = dutch_info[KEEP]
    info_df = info_df.merge(dutch_info, on="City", how="inner")

    info_df = info_df.reindex(
        columns=[col for col in info_df.columns if col != "Number"] + ["Number"]
    )

    # Add a row listing the total number
    info_df = info_df.append(
        pd.DataFrame(
            [["", "SUM", "SUM", sum(info_df["Number"])]], columns=list(info_df.columns)
        )
    )
    info_df.reset_index(drop=True, inplace=True)

    # Save the csv
    info_df.to_csv(f"./data/NL_{csv_update_date}.csv", index=False)


# Updated at 2020-03-13


def get_coronavirus_info_nl_v2(info_link):
    """
    Get the coronavirus information from RIVM website version 2
    Due to the fact that the info page is updated
    @return:
    csv_str: str, The csv info string
    """

    coronavirus_info_page = urlopen(info_link).read().decode("utf-8")
    soup_pattern = soup(coronavirus_info_page, features="lxml")

    csv_info_class = soup_pattern.find("div", {"id": "csvData"})
    csv_raw_str = csv_info_class.string

    # There is one extra column in the string
    # The usage for now is unknown
    # Before understanding it, just discard it
    csv_str = ""
    for line in csv_raw_str.split("\n"):
        csv_str += ";".join(line.split(";")[0:3]) + "\n"
    return csv_str


def save_info_nl_v2(csv_str):
    """
    Preprocess the data and save it as a csv file version 2
    """

    info_df = pd.read_csv(StringIO(csv_str), sep=";")

    # Rename the df
    info_df.rename(
        columns={"Aantal": "Number", "Gemeente": "City", "Gemnr": "City_code"},
        inplace=True,
    )

    # Get the update date
    date_string = info_df[info_df["City_code"] == -2]["City"].values[0]
    time_info = date_string.split(" ")
    month = DUTCH_MONTH.get(time_info[2])
    day = time_info[1]
    csv_update_date = YEAR + month + day
    print(f"csv update date:{csv_update_date}")

    # Translate the row about the number of patient with missing postcode or living abroad
    # into English
    inx = info_df[info_df["City_code"] == -1].index
    info_df.loc[inx, "City"] = "missing postcode and abroad"
    info_df.loc[inx, "City_code"] = ""

    # Delete useless info
    info_df.dropna(axis=0, inplace=True)

    # Change the order of columns
    info_df = info_df.reindex(
        columns=["City_code"] + [col for col in info_df.columns if col != "City_code"]
    )

    # Add the Province column
    dutch_info = pd.read_csv("./data/Dutch_municipalities_2020.csv")
    KEEP = ["Province", "City_code"]
    dutch_info = dutch_info[KEEP]
    info_df = info_df.merge(dutch_info, on="City_code", how="left")

    # Fill up the column province for the aggreration
    inx = info_df[info_df["City"] == "missing postcode and abroad"].index
    info_df.loc[inx, "Province"] = "missing postcode and abroad"

    # Change the order of columns
    info_df = info_df.reindex(
        columns=[col for col in info_df.columns if col != "Number"] + ["Number"]
    )
    info_df = info_df.fillna("")

    # Add a row listing the total number
    info_df = info_df.append(
        pd.DataFrame(
            [["", "SUM", "SUM", sum(info_df["Number"])]], columns=list(info_df.columns)
        )
    )
    info_df.reset_index(drop=True, inplace=True)

    # Save the csv
    info_df.to_csv(f"./data/NL_{csv_update_date}.csv", index=False)


# Updated at 2020-03-17


def get_coronavirus_info_nl_v3(info_link):
    """
    Get the coronavirus information from RIVM website version 3
    Due to the fact that the info page is updated
    @return:
    csv_str: str, The csv info string
    """

    coronavirus_info_page = urlopen(info_link).read().decode("utf-8")
    soup_pattern = soup(coronavirus_info_page, features="lxml")

    date_string = soup_pattern.find("p").string
    date_string = date_string.replace("\xa0", " ")
    time_info = date_string.split(" ")
    year = time_info[4]
    month = DUTCH_MONTH.get(time_info[3])
    day = time_info[2]
    csv_update_date = year + month + day

    csv_info_class = soup_pattern.find("div", {"id": "csvData"})
    csv_str = csv_info_class.string
    print(f"csv update date:{csv_update_date}")

    return csv_str, csv_update_date


def save_info_nl_v3(csv_str, csv_update_date):
    """
    Preprocess the data and save it as a csv file version 3
    The info from the website is updated at 2020-03-16, which contains 5 columns.
    For now I just keep the format consistent.
    I will think about to change it later.
    """

    KEEP_COL = ["Gemnr", "Gemeente", "Aantal"]
    info_df = pd.read_csv(StringIO(csv_str), sep=";")
    info_df = info_df[KEEP_COL]

    # Rename the df
    info_df.rename(
        columns={"Aantal": "Number", "Gemeente": "City", "Gemnr": "City_code"},
        inplace=True,
    )

    # Translate the row about the number of patient with missing postcode or living abroad
    # into English
    inx = info_df[info_df["City_code"] == -1].index
    info_df.loc[inx, "City"] = "missing postcode and abroad"
    info_df.loc[inx, "City_code"] = ""

    # Delete useless info
    info_df.dropna(axis=0, inplace=True)

    # Change the order of columns
    info_df = info_df.reindex(
        columns=["City_code"] + [col for col in info_df.columns if col != "City_code"]
    )

    # Add the Province column
    dutch_info = pd.read_csv("./data/Dutch_municipalities_2020.csv")
    KEEP = ["Province", "City_code"]
    dutch_info = dutch_info[KEEP]
    info_df = info_df.merge(dutch_info, on="City_code", how="left")

    # Fill up the column province for the aggreration
    inx = info_df[info_df["City"] == "missing postcode and abroad"].index
    info_df.loc[inx, "Province"] = "missing postcode and abroad"

    # Change the order of columns
    info_df = info_df.reindex(
        columns=[col for col in info_df.columns if col != "Number"] + ["Number"]
    )
    info_df = info_df.fillna("")

    # Add a row listing the total number
    info_df = info_df.append(
        pd.DataFrame(
            [["", "SUM", "SUM", sum(info_df["Number"])]], columns=list(info_df.columns)
        )
    )
    info_df.reset_index(drop=True, inplace=True)

    # Save the csv
    info_df.to_csv(f"./data/NL_{csv_update_date}.csv", index=False)


def get_coronavirus_info_nl_v4(info_link):
    """
    Get the coronavirus information from RIVM website version 3
    Due to the fact that the info page is updated
    @return:
    csv_str: str, The csv info string
    """

    coronavirus_info_page = urlopen(info_link).read().decode("utf-8")
    soup_pattern = soup(coronavirus_info_page, features="lxml")

    date_link = soup_pattern.find("div", {"id": "mapTitles"}).string
    decoder = json.JSONDecoder()
    date_string = decoder.decode(s=date_link)
    date_string = date_string["nl"]["mapSubtitle"]
    #     print(date_string)

    time_info = date_string.split(" ")[-1]
    day, month, year = time_info.split("-")
    month = month if len(month) != 1 else "0" + month
    csv_update_date = year + month + day

    csv_info_class = soup_pattern.find("div", {"id": "csvData"})
    csv_str = csv_info_class.string
    print(f"csv update date:{csv_update_date}")

    return csv_str, csv_update_date
