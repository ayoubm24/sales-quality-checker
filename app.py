import pandas as pd
import streamlit as st

from sales_quality_checker import (
    build_review_table,
    map_sales_columns,
    run_sales_checks,
)

st.title("Sales Quality Checker")
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file is not None:
    try:
        sales = pd.read_csv(uploaded_file)
        sales = map_sales_columns(sales)
        sales, is_duplicate, is_missing_price, is_wrong_total = run_sales_checks(sales)
        review_rows = build_review_table(sales, is_duplicate, is_missing_price, is_wrong_total)
    except ValueError as error:
        st.error(str(error))
    else: st.metric("Rows needing review", f"{len(review_rows):,}")
    st.caption(f"Showing {min(100, len(review_rows)):,} of {len(review_rows):,} flagged rows.")
    st.dataframe(review_rows.head(100))