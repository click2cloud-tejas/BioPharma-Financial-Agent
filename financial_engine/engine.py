

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv()

# -----------------------------
# Azure OpenAI Configuration
# -----------------------------
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")

client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION
)

# -----------------------------
# Load Excel data
# -----------------------------
EXCEL_PATH = Path(r"D:\BioPharma_Tejas\Codes_new\Financial_data_example_english_col_renamed.xlsx")
df = pd.read_excel(EXCEL_PATH)
df.columns = df.columns.str.lower()

financial_metrics = sorted(df["metrics"].dropna().unique().tolist())
companies = sorted(df["company"].dropna().unique().tolist())
periods = sorted(df["date_str"].dropna().unique().tolist())


# ==================================================================
# STEP 1 — Extract query understanding
# ==================================================================
def extract_query_understanding(user_query):
    prompt = f"""
You are a STRICT financial information extraction engine.

METRICS = {financial_metrics}
COMPANIES = {companies}
PERIODS = {periods}

Return only JSON with:
- metrics
- companies
- periods
- is_comparison (true/false)
- ask_insights (true/false)

User query: "{user_query}"
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
    except:
        parsed = {"metrics": [], "companies": [], "periods": [], "is_comparison": False, "ask_insights": False}

    return parsed


# ==================================================================
# STEP 2 — Filter dataset
# ==================================================================
def filter_financial_data(parsed):
    metrics = parsed.get("metrics", [])
    companies_list = parsed.get("companies", [])

    temp = df.copy()

    if metrics:
        temp = temp[temp["metrics"].str.lower().isin([m.lower() for m in metrics])]

    if companies_list:
        temp = temp[temp["company"].str.lower().isin([c.lower() for c in companies_list])]

    return temp


# ==================================================================
# STEP 3 — Convert dataframe → JSON-like structure
# ==================================================================
def dataframe_to_sentence_list(filtered_df):
    records = []

    for _, row in filtered_df.iterrows():
        rec = {
            "company": row["company"],
            "period": str(row["date_str"]),
            "metric": row["metrics"],
            "realization_budget": row["realization_budget"],
            "planning_budget": row["planning_budget"],
            "unit": row.get("column_format", "")
        }
        records.append(rec)

    json_lines = [json.dumps(r, ensure_ascii=False) for r in records]
    return "\n".join(json_lines)


# ==================================================================
# STEP 4 — Generate Natural Language Final Answer
# ==================================================================
def generate_financial_answer(user_query, filtered_df):
    structured_text = dataframe_to_sentence_list(filtered_df)

    prompt = f"""
You are a financial analyst. SHORT answers only.

STRUCTURED DATA:
{structured_text}

USER QUESTION:
{user_query}

Rules:
- Only 1–2 sentences
- No lists, no details
- Copy numbers EXACTLY from data
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ==================================================================
# STEP 5 — Graph Selection Logic (NEW)
# ==================================================================
def detect_graph_type(user_query):
    query = user_query.lower()

    # Line chart triggers
    line_keywords = [
        "compare", "comparison", "trend", "vs", "versus",
        "q1", "q2", "q3", "q4", "quarter", "growth"
    ]

    if any(word in query for word in line_keywords):
        return "line"

    # Default → bar chart
    return "bar"


# ==================================================================
# STEP 6 — Create Graph (Line / Bar) and Save
# ==================================================================
def create_graph(filtered_df, graph_type):
    if filtered_df.empty:
        return None

    # Sort by date to ensure proper order
    filtered_df = filtered_df.sort_values("date_str")

    plt.figure(figsize=(10, 5))

    if graph_type == "line":

        # Plot each company separately
        for comp, group in filtered_df.groupby("company"):
            plt.plot(
                group["date_str"],
                group["realization_budget"],
                marker="o",
                label=comp
            )

        plt.title("Trend Comparison")
        plt.xlabel("Period")
        plt.ylabel("Realization Budget")

    else:  # BAR CHART

        # If multiple periods → bar for each period on x-axis
        if filtered_df["date_str"].nunique() > 1:

            for comp, group in filtered_df.groupby("company"):
                plt.bar(
                    group["date_str"],
                    group["realization_budget"],
                    label=comp,
                    alpha=0.8
                )

            plt.title("Period-wise Bar Chart")
            plt.xlabel("Period")
            plt.ylabel("Realization Budget")

        else:
            # Single period → one bar per company
            values = filtered_df.groupby("company")["realization_budget"].sum()

            plt.bar(values.index, values.values)
            plt.title("Company Comparison")
            plt.xlabel("Company")
            plt.ylabel("Realization Budget")

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    chart_path = "generated_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# ==================================================================
# STEP 7 — Main Handler
# ==================================================================
def process_financial_query(user_query):
    print("Processing query:", user_query)

    parsed = extract_query_understanding(user_query)
    filtered = filter_financial_data(parsed)
    final_answer = generate_financial_answer(user_query, filtered)

    # NEW — Select chart type
    graph_type = detect_graph_type(user_query)

    # NEW — Generate and save graph
    chart_path = create_graph(filtered, graph_type)

    return {
        "llm_understanding": parsed,
        "filtered_data": filtered.to_dict(orient="records"),
        "final_answer": final_answer,
        "chart_type": graph_type,
        "chart_path": chart_path  # <-- Return to frontend
    }
