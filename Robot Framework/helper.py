import os
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_table_from_report(file_path, output_csv="table.csv"):
    """
    Extracts table from HTML report.
    Returns list of dicts: [{'Facility Type': ..., 'Visit Date': ..., 'Average Time Spent': ...}]
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(f"file:///{os.path.abspath(file_path)}")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".js-plotly-plot"))
        )

        headers = driver.execute_script("""
            const plot = document.querySelector('.js-plotly-plot');
            return plot._fullData[0].header.values;
        """)
        columns = driver.execute_script("""
            const plot = document.querySelector('.js-plotly-plot');
            return plot._fullData[0].cells.values;
        """)

        rows = []
        for i in range(len(columns[0])):
            row = {headers[j]: columns[j][i] for j in range(len(headers))}
            rows.append(row)

        # Зберігаємо CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        return rows  # повертаємо список словників для Robot Framework

    finally:
        driver.quit()


def filter_by_date(rows, date):
    """
    Filters rows by Visit Date == date (YYYY-MM-DD).
    """
    return [row for row in rows if row.get("Visit Date") == date]


def read_parquet_data(parquet_folder, filter_date):
    """
    Reads facility_type_avg_time_spent_per_visit_date parquet,
    filters by visit_date == filter_date (YYYY-MM-DD).
    Returns list of dicts: [{'Facility Type': ..., 'Visit Date': ..., 'Average Time Spent': ...}]
    """
    parquet_path = os.path.join(
        parquet_folder,
        "facility_type_avg_time_spent_per_visit_date"
    )

    df = pd.read_parquet(parquet_path)

    # Filter by data
    df["visit_date"] = pd.to_datetime(df["visit_date"]).dt.strftime("%Y-%m-%d")
    filtered = df[df["visit_date"] == filter_date].copy()

    # Rename columns according to HTML report
    filtered = filtered.rename(columns={
        "facility_type": "Facility Type",
        "visit_date":    "Visit Date",
        "avg_time_spent": "Average Time Spent"
    })

    # Get only necessary columns
    filtered = filtered[["Facility Type", "Visit Date", "Average Time Spent"]]

    return filtered.to_dict(orient="records")


def compare_report_and_parquet(html_rows, parquet_rows):
    """
    Compares HTML report rows with Parquet rows.
    Returns dict with comparison results.
    """
    # Both lists sorting
    html_sorted = sorted(html_rows, key=lambda x: x["Facility Type"])
    parquet_sorted = sorted(parquet_rows, key=lambda x: x["Facility Type"])

    mismatches = []

    # Count comparison
    if len(html_sorted) != len(parquet_sorted):
        return {
            "match": False,
            "error": f"Row count mismatch: HTML={len(html_sorted)}, Parquet={len(parquet_sorted)}",
            "mismatches": []
        }

    # Rows comparison
    for html_row, parquet_row in zip(html_sorted, parquet_sorted):
        if html_row["Facility Type"] != parquet_row["Facility Type"]:
            mismatches.append({
                "field": "Facility Type",
                "html": html_row["Facility Type"],
                "parquet": parquet_row["Facility Type"]
            })

        if html_row["Visit Date"] != parquet_row["Visit Date"]:
            mismatches.append({
                "field": "Visit Date",
                "html": html_row["Visit Date"],
                "parquet": parquet_row["Visit Date"]
            })

        # Data comparison (2 digits after comma)
        html_avg = round(float(html_row["Average Time Spent"]), 2)
        parquet_avg = round(float(parquet_row["Average Time Spent"]), 2)
        if html_avg != parquet_avg:
            mismatches.append({
                "field": "Average Time Spent",
                "html": html_avg,
                "parquet": parquet_avg
            })

    return {
        "match": len(mismatches) == 0,
        "mismatches": mismatches
    }