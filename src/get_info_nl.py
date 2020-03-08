"""Define functions"""

import re
import pandas as pd
import numpy as np
from io import StringIO
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup


RIVM_INFO_PAGE = "https://www.volksgezondheidenzorg.info"


def get_coronavirus_info_nl(info_link):
    """
    Get the coronavirus information from RIVM website.
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
