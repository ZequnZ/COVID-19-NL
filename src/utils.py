""" Utils function """
import os
import re
import pandas as pd


def agg_covid19_info_city(path=f"./data"):
    """
    Aggregate the data based on each city
    """

    # Get all daily info csv files
    # and Extract the date of each file
    csv_dict = {}
    with os.scandir(path) as files:
        for f in files:
            if f.name.startswith("NL") and f.name.endswith(".csv"):
                csv_dict[re.findall(r"[0-9]{8}", f.name)[0]] = f.name

    # We can see that newer info contains more cities as the virus keeps spreading
    # Therefore we need to sort the dictionary
    res = ""
    for key in sorted(csv_dict, reverse=True):
        if type(res) == str:
            res = pd.read_csv(f"./data/{csv_dict[key]}")
            # Only use the useful columns
            res = res[["City", "Number"]]
            # Rename the column with the date
            res.rename(
                columns={"Number": key}, inplace=True,
            )
        else:
            df = pd.read_csv(f"./data/{csv_dict[key]}")
            # Only use the useful columns
            df = df[["City", "Number"]]
            # Rename the column with the date
            df.rename(
                columns={"Number": key}, inplace=True,
            )
            # Merge the dataframe
            res = res.merge(df, on="City", how="left")
    # We hope to see the info from the past to now
    res = res.reindex(columns=["City"] + sorted(csv_dict))
    res = res.fillna(0)

    res.to_csv(f".data/NL_COVID19_info_city.csv", index=False)
    print(f"Successfully update and aggregate the city level data")


def agg_covid19_info_province(path=f"./data"):
    """
    Aggregate the data based on each city
    """

    # Get all daily info csv files
    # and Extract the date of each file
    csv_dict = {}
    with os.scandir(path) as files:
        for f in files:
            if f.name.startswith("NL") and f.name.endswith(".csv"):
                csv_dict[re.findall(r"[0-9]{8}", f.name)[0]] = f.name

    # We can see that newer info contains more cities as the virus keeps spreading
    # Therefore we need to sort the dictionary
    res = ""
    for key in sorted(csv_dict, reverse=True):
        if type(res) == str:
            res = pd.read_csv(f"./data/{csv_dict[key]}")
            # Only use the useful columns
            res = res[["Province", "Number"]]
            # Rename the column with the date
            res.rename(
                columns={"Number": key}, inplace=True,
            )
            # Aggregate the info to get the sum of each province
            res = res.groupby("Province").sum()
            res.reset_index(inplace=True)
        else:
            df = pd.read_csv(f"./data/{csv_dict[key]}")
            # Only use the useful columns
            df = df[["Province", "Number"]]
            # Rename the column with the date
            df.rename(
                columns={"Number": key}, inplace=True,
            )
            df = df.groupby("Province").sum()
            df.reset_index(inplace=True)

            # Merge the dataframe
            res = res.merge(df, on="Province", how="left")
    # We hope to see the info from the past to now
    res = res.reindex(columns=["Province"] + sorted(csv_dict))
    res = res.fillna(0)

    # Put the row "SUM" as the last row
    res = res.reindex(
        [col for col in res.index if col != res[res.Province == "SUM"].index]
        + [res[res.Province == "SUM"].index[0]]
    )

    res.to_csv(f".data/NL_COVID19_info_province.csv", index=False)
    print(f"Successfully update and aggregate the province level data")
