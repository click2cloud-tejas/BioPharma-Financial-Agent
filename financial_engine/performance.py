
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

load_dotenv()
# ----------------------------------------------------------
# NEW API: Revenue Performance for a Single Month
# ----------------------------------------------------------

def revenue_performance_by_month(month_input):

    EXCEL_PATH = Path(r"D:\BioPharma_Tejas\Codes_new\Financial_data_example_english_col_renamed.xlsx")
    df = pd.read_excel(EXCEL_PATH)
    """
    Filters Revenue rows for the given month and determines
    overperforming vs underperforming companies.
    """

    # Convert date_str column to datetime
    df["date_str"] = pd.to_datetime(df["date_str"])

    # Convert user input month to datetime
    try:
        selected_month = pd.to_datetime(month_input)
    except:
        return {
            "status": "error",
            "message": "Invalid month format. Use 'YYYY-MM' or 'Month YYYY'."
        }

    # Extract year and month
    year = selected_month.year
    month = selected_month.month

    # Filter only Revenue metric rows
    temp = df[df["metrics"].str.lower() == "revenue"]

    # Filter for the specific month
    temp = temp[
        (temp["date_str"].dt.year == year) &
        (temp["date_str"].dt.month == month)
    ]

    if temp.empty:
        return {
            "status": "no_data",
            "message": f"No Revenue data found for {month_input}.",
            "results": []
        }

    results = []

    for idx, row in temp.iterrows():
        realization = row["realization_budget"]
        planning = row["planning_budget"]

        # Determine performance
        if realization > planning:
            performance = "overperforming"
        elif realization < planning:
            performance = "underperforming"
        else:
            performance = "met target"

        results.append({
            "company": row["company"],
            "period": str(row["date_str"].date()),
            "metric": "Revenue",
            "realization_budget": realization,
            "planning_budget": planning,
            "performance": performance
        })

    return {
        "status": "success",
        "month": month_input,
        "results": results
    }
