"""Workflow to obtain and save the data"""

from get_info_nl import get_coronavirus_info_nl_v2, save_info_nl_v2, RIVM_INFO_PAGE
from utils import agg_covid19_info_city, agg_covid19_info_province

if __name__ == "__main__":

    # As the layout of the page is changed, the previous workflow
    # doesn't work anymore (Noticed at 2020-03-12)
    #################################################
    #################################################
    # csv_link, csv_update_date = get_coronavirus_info_nl(
    #     RIVM_INFO_PAGE
    #     + "/onderwerp/infectieziekten/regionaal-internationaal/coronavirus-covid-19#!node-coronavirus-covid-19-meldingen"
    # )

    # save_info_nl(csv_link, csv_update_date)
    #################################################
    #################################################

    csv_str = get_coronavirus_info_nl_v2(
        RIVM_INFO_PAGE
        + "/onderwerp/infectieziekten/regionaal-internationaal/coronavirus-covid-19#!node-coronavirus-covid-19-meldingen"
    )
    save_info_nl_v2(csv_str)

    agg_covid19_info_city()
    agg_covid19_info_province()
