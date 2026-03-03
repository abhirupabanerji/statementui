import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from categorizer import categorize, get_txn_prefix, categorize_by_description
import time

st.set_page_config(layout="wide", page_icon='💳', page_title='Bank Statement Analyzer')

st.markdown("""
<style>
.head {
    text-align: center;
}
.head h1 {
    color: #06B6D4;
    font-size: 48px;
            
}
.head p {
    color: #a0a0a0;
    font-size: 17px;
}
.insight-card {
    background: #06B6D41A;
    border: 1px solid #7C3AED4D;
    border-radius: 14px;
    padding: 18px 22px;
    color: #000000;
    font-size: 15px;
}
.insight-card.warning {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.3);
    color: #fde68a;
}
.insight-card.danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: #fca5a5;
}
.insight-card.success {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.3);
    color: #6ee7b7;
}
.section-title {
    font-size:20px;
    font-weight: 700;
    color: #000000;
    border-bottom: 2px solid #06B6D45A;
    margin-bottom: 8px;
}
.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    transition: 0.3s;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 18px rgba(0,0,0,0.12);
}
.metric-title {
    font-size: 14px;
    color: #6c757d;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 38px;
    font-weight: 600;
}

div.stButton > button {
    background-color: white;
    color: #0F172A;
    border: 1.5px solid #06B6D4;
    border-radius: 10px;
    padding: 0.6em 1.4em;
    font-weight: 500;

}
div.stButton > button:hover {
    background-color: #06B6D4;
    color: white;
}

/* Active */
div.stButton > button:active {
    background-color: #0891B2;
}

</style>""",unsafe_allow_html=True)
#Upload statement
st.markdown("""
<div class="head">
    <h1>💳 Bank Statement Analyzer</h1>
    <p>Upload your bank statement and instantly understand where your money goes</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload file here:",
    type=["csv", "xlsx", "xls"])

if uploaded_file is None:
    st.markdown("""
    <div class="insight-card" style="text-align:center;">
        <strong>How to get your bank statement?</strong><br>
        Login to your net banking → Go to Account Statement → 
        Download as CSV or Excel → Upload here
    </div>
    """, unsafe_allow_html=True)

#data preview
if uploaded_file:

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.markdown('<div class="section-title">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(5), use_container_width=True)

    #create dictionary 'detected' for storing column names
    def auto_detect_columns(columns):
        detected = {}

        for col in columns:
            col_lower = col.lower()

            if "date" in col_lower:
                detected["date"] = col
            elif any(kw in col_lower for kw in ["transaction_id", "transaction id", "txn id", "txnid", "ref no", "reference"]):
                detected["transaction_id"] = col
            elif "description" in col_lower:
                detected["description"] = col
            elif "debit" in col_lower:
                detected["debit"] = col
            elif "credit" in col_lower:
                detected["credit"] = col
            elif "balance" in col_lower:
                detected["balance"] = col

        return detected
    
    st.markdown('<div class="section-title">Column Detection</div>', unsafe_allow_html=True)
    detected = auto_detect_columns(df.columns.tolist())

    #Successful detection check
    required_keys = ["date", "description", "debit", "credit"]
    missing = [key for key in required_keys if not detected.get(key)]

    if not missing:
        txn_id_found = "transaction_id" in detected
        if txn_id_found:
            st.success(f"All columns detected successfully!")
    else:
        st.error(
        "The uploaded file does not appear to be a valid bank statement.\n\n"
        "Please ensure your file contains Date, Description, Debit, and Credit columns."
    )
        st.stop()

    #Analysis
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        analyze = st.button("View Spending Analysis",use_container_width=True)
    if analyze:
        with st.spinner("Analyzing transactions..."):
            time.sleep(1)

            cols_to_select = [detected["date"], detected["description"], detected["debit"], detected["credit"]]
            col_names = ["date", "description", "debit", "credit"]

            if detected.get("transaction_id"):
                cols_to_select.insert(1, detected["transaction_id"])
                col_names.insert(1, "transaction_id")

            df_clean = df[cols_to_select].copy()
            df_clean.columns = col_names

            df_clean["debit"]  = pd.to_numeric(df_clean["debit"],  errors="coerce").fillna(0)
            df_clean["credit"] = pd.to_numeric(df_clean["credit"], errors="coerce").fillna(0)
            df_clean["date"]   = pd.to_datetime(df_clean["date"],  errors="coerce")

            # categorising columns if transaction id present, if not only description used
            if "transaction_id" in df_clean.columns:
                df_clean["category"] = df_clean.apply(
                    lambda row: categorize(row["transaction_id"], row["description"]), axis=1
                )
                df_clean["payment_method"] = df_clean["transaction_id"].apply(get_txn_prefix)
            else:
                df_clean["category"] = df_clean["description"].apply(categorize_by_description)

            total_income  = df_clean["credit"].sum()
            total_expense = df_clean["debit"].sum()
            net_savings   = total_income - total_expense
            savings_pct   = (net_savings / total_income * 100) if total_income > 0 else 0

        #KPI Cards
        st.markdown('<div class="section-title">KPI Metrics</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Total Income</div>
                        <div class="metric-value blue">{total_income:,.0f}</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Total Expense</div>
                        <div class="metric-value blue">{total_expense:,.0f}</div></div>""",unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Net Savings</div>
                        <div class="metric-value blue">{net_savings:,.0f}</div></div>""",unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Savings Rate</div>
                        <div class="metric-value blue">{savings_pct:,.1f}%</div></div>""",unsafe_allow_html=True)
        st.markdown("")

        #Charts
        expenses_df = df_clean[df_clean["debit"] > 0].copy()
        category_summary = expenses_df.groupby("category")["debit"].sum().reset_index()

        st.markdown('<div class="section-title">Expenses Distribution</div>', unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)
        with ch1:
            fig1 = px.pie(category_summary, values="debit", names="category",title="Expenditure chart", hole=0.40)
            st.plotly_chart(fig1, use_container_width=True)

        with ch2:
            fig2 = px.bar(category_summary, x="debit", y="category", orientation="h", text="debit", title="Expenses by Category", color="category")
            fig2.update_xaxes(showgrid=True)
            fig2.update_yaxes(showgrid=True)
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

        if "payment_method" in df_clean.columns:
            st.markdown('<div class="section-title">Payment Method Usage Distribution</div>', unsafe_allow_html=True)
            pm_summary = expenses_df.copy()
            pm_summary["payment_method"] = df_clean.loc[expenses_df.index, "payment_method"]
            pm_group = pm_summary.groupby("payment_method")["debit"].sum().reset_index()
            pm_group.columns = ["Payment Method", "Amount"]

            ch3, ch4 = st.columns(2)
            with ch3:
                fig3 = px.pie(pm_group, values="Amount", names="Payment Method",
                              title="How are you paying?", hole=0.40)
                st.plotly_chart(fig3, use_container_width=True)

            with ch4:
                fig4 = px.bar(pm_group, x="Payment Method", y="Amount",
                              title="Payment Method used most",
                              color="Payment Method", text="Amount")
                fig4.update_xaxes(showgrid=True)
                fig4.update_yaxes(showgrid=True)
                fig4.update_traces(textposition="outside")
                st.plotly_chart(fig4, use_container_width=True)
