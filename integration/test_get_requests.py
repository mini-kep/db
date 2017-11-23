import requests


lists_of_name_by_freq = {
    'a': [
          "CPI_ALCOHOL_rog",
          "CPI_FOOD_rog",
          "CPI_NONFOOD_rog",
          "CPI_rog",
          "CPI_SERVICES_rog",
          "EXPORT_GOODS_bln_usd",
          "GDP_bln_rub",
          "GDP_yoy",
          "GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub",
          "GOV_EXPENSE_ACCUM_FEDERAL_bln_rub",
          "GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub",
          "GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub",
          "GOV_REVENUE_ACCUM_FEDERAL_bln_rub",
          "GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub",
          "GOV_SURPLUS_ACCUM_FEDERAL_bln_rub",
          "GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub",
          "IMPORT_GOODS_bln_usd",
          "INDPRO_yoy",
          "INVESTMENT_bln_rub",
          "INVESTMENT_yoy",
          "RETAIL_SALES_bln_rub",
          "RETAIL_SALES_FOOD_bln_rub",
          "RETAIL_SALES_FOOD_yoy",
          "RETAIL_SALES_NONFOOD_bln_rub",
          "RETAIL_SALES_NONFOOD_yoy",
          "RETAIL_SALES_yoy",
          "TRANSPORT_FREIGHT_bln_tkm",
          "UNEMPL_pct",
          "WAGE_NOMINAL_rub",
          "WAGE_REAL_yoy"
    ],
    'q': [
      "CPI_ALCOHOL_rog",
      "CPI_FOOD_rog",
      "CPI_NONFOOD_rog",
      "CPI_rog",
      "CPI_SERVICES_rog",
      "EXPORT_GOODS_bln_usd",
      "GDP_bln_rub",
      "GDP_yoy",
      "GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub",
      "GOV_EXPENSE_ACCUM_FEDERAL_bln_rub",
      "GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub",
      "GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub",
      "GOV_REVENUE_ACCUM_FEDERAL_bln_rub",
      "GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub",
      "GOV_SURPLUS_ACCUM_FEDERAL_bln_rub",
      "GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub",
      "IMPORT_GOODS_bln_usd",
      "INDPRO_rog",
      "INDPRO_yoy",
      "INVESTMENT_bln_rub",
      "INVESTMENT_rog",
      "INVESTMENT_yoy",
      "RETAIL_SALES_bln_rub",
      "RETAIL_SALES_FOOD_bln_rub",
      "RETAIL_SALES_FOOD_rog",
      "RETAIL_SALES_FOOD_yoy",
      "RETAIL_SALES_NONFOOD_bln_rub",
      "RETAIL_SALES_NONFOOD_rog",
      "RETAIL_SALES_NONFOOD_yoy",
      "RETAIL_SALES_rog",
      "RETAIL_SALES_yoy",
      "TRANSPORT_FREIGHT_bln_tkm",
      "UNEMPL_pct",
      "WAGE_NOMINAL_rub",
      "WAGE_REAL_rog",
      "WAGE_REAL_yoy"
    ],
    'm': [
      "CPI_ALCOHOL_rog",
      "CPI_FOOD_rog",
      "CPI_NONFOOD_rog",
      "CPI_rog",
      "CPI_SERVICES_rog",
      "EXPORT_GOODS_bln_usd",
      "GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub",
      "GOV_EXPENSE_ACCUM_FEDERAL_bln_rub",
      "GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub",
      "GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub",
      "GOV_REVENUE_ACCUM_FEDERAL_bln_rub",
      "GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub",
      "GOV_SURPLUS_ACCUM_FEDERAL_bln_rub",
      "GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub",
      "IMPORT_GOODS_bln_usd",
      "INDPRO_rog",
      "INDPRO_yoy",
      "INVESTMENT_bln_rub",
      "INVESTMENT_rog",
      "INVESTMENT_yoy",
      "RETAIL_SALES_bln_rub",
      "RETAIL_SALES_FOOD_bln_rub",
      "RETAIL_SALES_FOOD_rog",
      "RETAIL_SALES_FOOD_yoy",
      "RETAIL_SALES_NONFOOD_bln_rub",
      "RETAIL_SALES_NONFOOD_rog",
      "RETAIL_SALES_NONFOOD_yoy",
      "RETAIL_SALES_rog",
      "RETAIL_SALES_yoy",
      "TRANSPORT_FREIGHT_bln_tkm",
      "UNEMPL_pct",
      "WAGE_NOMINAL_rub",
      "WAGE_REAL_rog",
      "WAGE_REAL_yoy"
    ],
    'd': [
      "BRENT",
      "USDRUR_CB",
      "UST_10YEAR",
      "UST_1MONTH",
      "UST_1YEAR",
      "UST_20YEAR",
      "UST_2YEAR",
      "UST_30YEAR",
      "UST_3MONTH",
      "UST_3YEAR",
      "UST_5YEAR",
      "UST_6MONTH",
      "UST_7YEAR"
    ]
}

freqs = {'a', 'q', 'm', 'd'}


def test_user_can_get_allowed_frequencies():

    url = f'https://minikep-db.herokuapp.com/api/freq'

    data = requests.get(url).json()

    assert set(data) == freqs


def test_user_can_get_names_by_frequency():

    for freq in freqs:
        url = f'https://minikep-db.herokuapp.com/api/names/{freq}'

        data = requests.get(url).json()

        assert data == lists_of_name_by_freq[freq]

if __name__ == "__main__":
    test_user_can_get_allowed_frequencies()
    test_user_can_get_names_by_frequency()