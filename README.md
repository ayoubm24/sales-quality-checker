# Sales Quality Checker

A Python and Streamlit app that audits sales CSVs for duplicate order lines, missing unit prices, and incorrect line totals. Upload a file to see how many rows need review, see a breakdown of issue types, and download the flagged rows as a CSV.

## What it checks

| Check | When a row is flagged |
| --- | --- |
| Duplicate order line | The same `order_id` and `line_id` appeared earlier in the file. |
| Missing unit price | The `unit_price` value is missing. |
| Incorrect line total | The recorded total differs from `quantity × unit_price` at two-decimal precision. This check requires all three values. |

The app counts each flagged row once in the overall total. Its Matplotlib chart counts each issue separately, so a row with two issues appears in both categories. The table previews up to 100 flagged rows. The **Download full review report (CSV)** button exports all flagged rows with their issue labels, expected totals, and differences where available.

## Run locally

From the project folder, run the following on macOS or Linux with Python 3 installed.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pandas streamlit matplotlib
python -m streamlit run app.py
```

Open [localhost:8501](http://localhost:8501) and upload a sales CSV.

## CSV format

The checker requires `order_id`, `line_id`, `item`, `quantity`, `unit_price`, and `line_total`. Headers are matched case-insensitively for the fields with mapping rules. For example, `Receipt ID` maps to `order_id`, `Qty` maps to `quantity`, and `Price Per Unit` maps to `unit_price`. It reports ambiguous matches and missing required columns.

Save this example as `sample_sales.csv` and upload it to try all three checks.

```csv
order_id,line_id,item,quantity,unit_price,line_total
1001,1,Fries,2,4.95,9.90
1001,1,Fries,2,4.95,9.90
1002,1,Salad,1,,8.75
1003,1,Burger,2,12.99,28.98
```

Expected result: **3 of 4 rows flagged**, with one duplicate order line, one missing unit price, and one incorrect total.

## Stress-test results

The checker flagged **12,500 of 100,000 rows (12.5%)** in a synthetic restaurant sales CSV.

| Issue | Flags |
| --- | ---: |
| Incorrect line totals | 6,500 |
| Missing unit prices | 5,000 |
| Duplicate order lines | 4,000 |

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface for uploading files, viewing the chart and preview, and downloading results. |
| `sales_quality_checker.py` | Header mapping, validation rules, review table creation, and command-line audit summary. |
