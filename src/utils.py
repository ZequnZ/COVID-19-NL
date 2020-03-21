""" Utils function """
import os
import re
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def agg_covid19_info_city(path=f"./data"):
    """
    Aggregate the data based on each city
    """

    # Get all daily info csv files
    # and Extract the date of each file
    csv_dict = {}
    with os.scandir(path) as files:
        for f in files:
            if f.name.startswith("NL_2020") and f.name.endswith(".csv"):
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

    res.to_csv(f"./data/NL_COVID19_info_city.csv", index=False)
    print(f"Successfully update and aggregate the city level data")


def agg_covid19_info_province(path=f"./data"):
    """
    Aggregate the data based on each province
    """

    # Get all daily info csv files
    # and Extract the date of each file
    csv_dict = {}
    with os.scandir(path) as files:
        for f in files:
            if f.name.startswith("NL_2020") and f.name.endswith(".csv"):
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

    res.to_csv(f"./data/NL_COVID19_info_province.csv", index=False)
    print(f"Successfully update and aggregate the province level data")


def viz_preprocessing(df_path):
    """
    Preprocess the aggregation csv into a good format for visualization
    """
    df = pd.read_csv(df_path)
    res = df.T
    res = res.rename(columns=res.iloc[0]).drop(res.index[0])
    res = res.astype("int64")
    res.reset_index(inplace=True)
    res["index"] = res["index"].apply(
        lambda x: "{}-{}-{}".format(x[0:4], x[4:6], x[6:])
    )
    res["index"] = pd.to_datetime(res["index"])
    return res


def gen_p_graphs(df_path, threshold=200):
    """
    Generate graphs to show the number of infected in different NL provinces
    """
    df = viz_preprocessing(df_path)

    cols = list(df.columns)[1:-1]
    colors = sns.color_palette("bright", len(cols))
    plt.figure(figsize=(16, 9))
    for i, c in enumerate(cols):
        sns.lineplot(x="index", y=c, data=df, label=c, linewidth=1.5, color=colors[i])

    plt.grid(color="grey", linestyle="--", linewidth=0.5, which="both")
    plt.xlabel("Date", fontsize=16)
    plt.ylabel("Number of infected", fontsize=16)
    plt.title(
        f"Number of infected cases in different provinces of NL\n updated at {datetime.datetime.now()}",
        fontsize=20,
    )
    plt.savefig(f"./imgs/num_all_province.png")
    # plt.show()

    col2 = df.iloc[-1, 1:] < threshold
    col2 = list(col2[col2].index)
    colors = sns.color_palette("Set2", len(col2))
    plt.figure(figsize=(16, 9))
    for i, c in enumerate(col2):
        sns.lineplot(x="index", y=c, data=df, label=c, linewidth=3, color=colors[i])

    plt.grid(color="grey", linestyle="--", linewidth=0.5, which="both")
    plt.xlabel("Date", fontsize=16)
    plt.ylabel("Number of infected", fontsize=16)
    plt.title(
        f"Number of infected cases(less than {threshold}) in different provinces of NL\n updated at {datetime.datetime.now()}",
        fontsize=20,
    )
    plt.ylim(bottom=0, top=threshold)
    plt.savefig(f"./imgs/num_sub_province.png")
    # plt.show()
    print(f"Successfully generate graphs about province.")


def gen_c_graphs(df_path, top=10):
    """
    Generate graphs to show the top number of infected in NL cities.
    """
    df = viz_preprocessing(df_path)
    c = df.iloc[-1, 1:]
    cols = list(c.sort_values(ascending=False).index)[1:1 + top]
    colors = sns.color_palette("bright", len(cols))
    plt.figure(figsize=(16, 9))
    for i, c in enumerate(cols):
        sns.lineplot(x="index", y=c, data=df, label=c, linewidth=2, color=colors[i])

    plt.grid(color="grey", linestyle="--", linewidth=0.5, which="both")
    plt.xlabel("Date", fontsize=16)
    plt.ylabel("Number of infected", fontsize=16)
    plt.title(
        f"Top {top} number of infected cases in cities of NL\n updated at {datetime.datetime.now()}",
        fontsize=20,
    )
    plt.savefig(f"./imgs/num_top_cities.png")
    # plt.show()
    print(f"Successfully generate graphs about city.")
