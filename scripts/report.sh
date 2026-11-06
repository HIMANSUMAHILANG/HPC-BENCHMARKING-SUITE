
#!/usr/bin/env python3

import csv
import html
import re
import sys
from pathlib import Path


# ==========================================================
# HPC BENCHMARK PERFORMANCE REPORT GENERATOR
# ==========================================================

if len(sys.argv) != 2:
    print("Usage: python3 generate_report.py <benchmark_run_dir>")
    sys.exit(1)

RUN_DIR = Path(sys.argv[1]).resolve()

LOG_DIR = RUN_DIR / "logs"
STATUS_FILE = RUN_DIR / "run_status.tsv"

SUMMARY_CSV = RUN_DIR / "summary.csv"
PERFORMANCE_CSV = RUN_DIR / "performance.csv"
HTML_REPORT = RUN_DIR / "report.html"

# ReFrame performance output:
# P: metric_name: 123.45 MB/s (r:0, l:None, u:None)

PERFORMANCE_PATTERN = re.compile(
    r"^\s*P:\s*([^:]+):\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    r"\s+([^\s(]+)",
    re.MULTILINE
)


# ----------------------------------------------------------
# Read benchmark execution statuses
# ----------------------------------------------------------

def read_status_file():

    records = []

    if not STATUS_FILE.exists():
        raise FileNotFoundError(
            f"Status file not found: {STATUS_FILE}"
        )

    with STATUS_FILE.open(newline="") as file:

        reader = csv.DictReader(
            file,
            delimiter="\t"
        )

        for row in reader:
            records.append(row)

    return records


# ----------------------------------------------------------
# Extract ReFrame performance values
# ----------------------------------------------------------

def extract_performance(benchmark):

    log_file = LOG_DIR / f"{benchmark}.log"

    if not log_file.exists():
        return []

    content = log_file.read_text(
        encoding="utf-8",
        errors="replace"
    )

    results = []

    for match in PERFORMANCE_PATTERN.finditer(content):

        metric_name = match.group(1).strip()
        value = float(match.group(2))
        unit = match.group(3).strip()

        results.append({
            "metric": metric_name,
            "value": value,
            "unit": unit
        })

    return results


# ----------------------------------------------------------
# Create execution summary CSV
# ----------------------------------------------------------

def write_summary_csv(records):

    fields = [
        "benchmark",
        "status",
        "duration_seconds"
    ]

    with SUMMARY_CSV.open(
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(records)


# ----------------------------------------------------------
# Create performance CSV
# ----------------------------------------------------------

def write_performance_csv(records, metrics):

    fields = [
        "benchmark",
        "status",
        "metric",
        "value",
        "unit"
    ]

    with PERFORMANCE_CSV.open(
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for record in records:

            benchmark = record["benchmark"]
            status = record["status"]

            benchmark_metrics = metrics.get(
                benchmark, []
            )

            if not benchmark_metrics:

                writer.writerow({
                    "benchmark": benchmark,
                    "status": status,
                    "metric": "",
                    "value": "",
                    "unit": ""
                })

                continue

            for metric in benchmark_metrics:

                writer.writerow({
                    "benchmark": benchmark,
                    "status": status,
                    "metric": metric["metric"],
                    "value": metric["value"],
                    "unit": metric["unit"]
                })


# ----------------------------------------------------------
# Generate HTML report
# ----------------------------------------------------------

def write_html_report(records, metrics):

    total = len(records)

    passed = sum(
        row["status"] == "PASSED"
        for row in records
    )

    failed = sum(
        row["status"] != "PASSED"
        for row in records
    )

    summary_rows = []
    performance_rows = []

    for row in records:

        benchmark = html.escape(row["benchmark"])
        status = html.escape(row["status"])
        duration = html.escape(
            str(row["duration_seconds"])
        )

        summary_rows.append(
            f"""
            <tr>
                <td>{benchmark}</td>
                <td>{status}</td>
                <td>{duration} s</td>
                <td>
                    <a href="logs/{benchmark}.log">
                        View log
                    </a>
                </td>
            </tr>
            """
        )

        for metric in metrics.get(
            row["benchmark"], []
        ):

            metric_name = html.escape(metric["metric"])
            value = html.escape(str(metric["value"]))
            unit = html.escape(metric["unit"])

            performance_rows.append(
                f"""
                <tr>
                    <td>{benchmark}</td>
                    <td>{metric_name}</td>
                    <td>{value}</td>
                    <td>{unit}</td>
                </tr>
                """
            )

    if not performance_rows:

        performance_rows.append(
            """
            <tr>
                <td colspan="4">
                    No performance values were extracted.
                </td>
            </tr>
            """
        )

    run_id = html.escape(RUN_DIR.name)

    report = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>HPC Benchmark Performance Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 35px;
    background: #f4f6f9;
    color: #222;
}}

h1, h2 {{
    color: #17365d;
}}

.container {{
    max-width: 1100px;
    margin: auto;
}}

.cards {{
    display: flex;
    gap: 15px;
    margin: 25px 0;
    flex-wrap: wrap;
}}

.card {{
    background: white;
    padding: 20px;
    flex: 1;
    min-width: 130px;
    border-radius: 8px;
    box-shadow: 0 2px 6px #0001;
}}

.card h3 {{
    margin-top: 0;
    font-size: 14px;
    color: #555;
}}

.card p {{
    font-size: 25px;
    font-weight: bold;
    margin-bottom: 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    margin-bottom: 35px;
}}

th, td {{
    padding: 12px;
    border: 1px solid #ddd;
    text-align: left;
}}

th {{
    background: #17365d;
    color: white;
}}

tr:nth-child(even) {{
    background: #f1f4f8;
}}

a {{
    color: #1769aa;
}}

.footer {{
    margin-top: 35px;
    color: #666;
    font-size: 13px;
}}

</style>

</head>

<body>

<div class="container">

<h1>HPC Benchmark Performance Report</h1>

<p><b>Run ID:</b> {run_id}</p>

<div class="cards">

    <div class="card">
        <h3>Total Benchmarks</h3>
        <p>{total}</p>
    </div>

    <div class="card">
        <h3>Passed</h3>
        <p>{passed}</p>
    </div>

    <div class="card">
        <h3>Failed / Not Passed</h3>
        <p>{failed}</p>
    </div>

</div>

<h2>Benchmark Execution Summary</h2>

<table>

<thead>
<tr>
    <th>Benchmark</th>
    <th>Status</th>
    <th>Duration</th>
    <th>Log</th>
</tr>
</thead>

<tbody>
{''.join(summary_rows)}
</tbody>

</table>

<h2>Performance Measurements</h2>

<table>

<thead>
<tr>
    <th>Benchmark</th>
    <th>Performance Metric</th>
    <th>Measured Value</th>
    <th>Unit</th>
</tr>
</thead>

<tbody>
{''.join(performance_rows)}
</tbody>

</table>

<h2>Report Artifacts</h2>

<ul>
    <li><a href="summary.csv">Execution summary CSV</a></li>
    <li><a href="performance.csv">Performance measurements CSV</a></li>
    <li><a href="reframe/">ReFrame JSON report directory</a></li>
</ul>

<div class="footer">

Generated by the HPC ReFrame Benchmark Orchestration Framework.

</div>

</div>

</body>
</html>
"""

    HTML_REPORT.write_text(
        report,
        encoding="utf-8"
    )


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():

    records = read_status_file()

    metrics = {}

    for record in records:

        benchmark = record["benchmark"]

        metrics[benchmark] = extract_performance(
            benchmark
        )

    write_summary_csv(records)

    write_performance_csv(
        records,
        metrics
    )

    write_html_report(
        records,
        metrics
    )

    print()
    print("================================================")
    print("       HPC PERFORMANCE REPORT GENERATED")
    print("================================================")

    print(f"Summary CSV     : {SUMMARY_CSV}")
    print(f"Performance CSV : {PERFORMANCE_CSV}")
    print(f"HTML Report     : {HTML_REPORT}")

    print("================================================")


if __name__ == "__main__":
    main()
