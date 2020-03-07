"""Workflow to obtain and save the data"""

from get_info_nl import get_coronavirus_info_nl, save_info_nl, RIVM_INFO_PAGE

if __name__ == "__main__":
    csv_link, csv_update_date = get_coronavirus_info_nl(
        RIVM_INFO_PAGE
        + "/onderwerp/infectieziekten/regionaal-internationaal/coronavirus-covid-19#!node-coronavirus-covid-19-meldingen"
    )

    save_info_nl(csv_link, csv_update_date)

