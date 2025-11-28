from flask import Flask, render_template, request, jsonify
from financial_engine.engine import process_financial_query
from financial_engine.performance import revenue_performance_by_month
from dotenv import load_dotenv
import os
from flask import send_from_directory
load_dotenv()

app = Flask(__name__, static_folder="static")

import math

def clean_json(obj):
    """Recursively convert NaN → None to make valid JSON."""
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    return obj

# ✅ ADD THIS ROUTE
@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/ask", methods=["POST"])
# def ask():
#     try:
#         data = request.json
#         user_query = data.get("query")

#         result = process_financial_query(user_query)

#         # ensure result exists
#         if not result:
#             raise Exception("process_financial_query returned None")

#         cleaned = clean_json(result.get("filtered_data", []))

#         return jsonify({
#             "answer": result.get("final_answer", "No answer generated."),
#             "understanding": result.get("llm_understanding", {}),
#             "filtered": cleaned
#         })
    
    

#     except Exception as e:
#         print("❌ ERROR IN /ask:", e)
#         return jsonify({
#             "answer": "⚠️ Sorry, something went wrong on the server.",
#             "error": str(e)
#         }), 500
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.json
        user_query = data.get("query")

        result = process_financial_query(user_query)

        if not result:
            raise Exception("process_financial_query returned None")

        cleaned = clean_json(result.get("filtered_data", []))

        chart_path = result.get("chart_path")
        chart_url = None

        # convert "generated_chart.png" → "/chart/generated_chart.png"
        if chart_path and os.path.exists(chart_path):
            filename = os.path.basename(chart_path)
            chart_url = f"/chart/{filename}"

        return jsonify({
            "answer": result.get("final_answer", "No answer generated."),
            "understanding": result.get("llm_understanding", {}),
            "filtered": cleaned,
            "chart_url": chart_url  # <---- IMPORTANT
        })

    except Exception as e:
        print("❌ ERROR IN /ask:", e)
        return jsonify({
            "answer": "⚠️ Sorry, something went wrong on the server.",
            "error": str(e)
        }), 500


@app.route("/api/revenue-performance", methods=["POST"])
def revenue_performance_month_route():
    data = request.json
    month = data.get("month")   # e.g. "2021-05" or "May 2021"

    result = revenue_performance_by_month(month)
    return jsonify(result)


@app.route("/chart/<filename>")
def get_chart(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
