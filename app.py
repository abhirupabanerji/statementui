import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from categorizer import categorize, get_txn_prefix, categorize_by_description
import time
from database import create_connection, create_table
from auth import login_user, register_user

st.set_page_config(layout="wide", page_icon='💳', page_title='Bank Statement Analyzer')

create_table()

# SESSION STATES
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "home"


# ==============================
# STYLE
# ==============================

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


# ================= LANDING LOGIN PAGE =================

if not st.session_state.logged_in:

    st.markdown("""
    <style>

   .left-panel {
    background: linear-gradient(135deg,#0F172A,#134E4A);
    padding:70px;
    border-radius:20px;
    color:white;
    height:520px;

    display:flex;
    flex-direction:column;
    justify-content:center;  /* vertical center */
}

.left-title {
    font-size:38px;
    font-weight:700;
    margin-bottom:18px;
}

.left-desc {
    font-size:17px;
    opacity:0.85;
    line-height:1.6;
    max-width:500px;
}

    .stat-card {
        background:rgba(255,255,255,0.08);
        padding:20px;
        border-radius:12px;
        text-align:center;
    }

    .stat-number {
        font-size:28px;
        font-weight:600;
    }

    .login-card {
    background:white;
    padding:40px;
    border-radius:18px;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    margin-top:30px;
}

.login-title{
    font-size:28px;
    font-weight:600;
}

.login-sub{
    color:#64748B;
    margin-bottom:25px;
}

    </style>
    """, unsafe_allow_html=True)


    left, right = st.columns([1.2,1])

    # -------- LEFT SIDE --------
    with left:

        st.markdown("""
        <div class="left-panel">

        <div class="left-title">
        💳 Smart Bank Statement Insights
        </div>

        <div class="left-desc">
        Upload your bank statements and instantly understand
        spending patterns, payment habits and savings trends.
        Get powerful financial insights in seconds.
        </div>

        </div>
        """, unsafe_allow_html=True)


    # -------- RIGHT SIDE (LOGIN) --------
    with right:

        st.markdown("""
                    <style>

    .tab-title{
        font-size:26px;
        font-weight:600;
        margin-bottom:5px;
    }

    .tab-sub{
        color:#64748B;
        margin-bottom:20px;
    }

    div.stButton > button{
        background:#06B6D4;
        color:white;
        border:none;
        border-radius:8px;
        padding:12px;
        font-weight:500;
    }

    div.stButton > button:hover{
        background:#0891B2;
    }

    </style>
    """, unsafe_allow_html=True)


        with st.container():

            st.markdown('<div>', unsafe_allow_html=True)

            login_tab, register_tab = st.tabs(["Login", "Register"])


        # ---------------- LOGIN TAB ----------------
            with login_tab:

                st.markdown('<div class="tab-title">Welcome Back</div>', unsafe_allow_html=True)
                st.markdown('<div class="tab-sub">Login to analyze your finances</div>', unsafe_allow_html=True)

                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")

                if st.button("Log In", use_container_width=True):

                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username=username
                        st.success("Login successful")
                        st.rerun()

                    else:
                        st.error("Invalid username or password")


        # ---------------- REGISTER TAB ----------------
            with register_tab:

                st.markdown('<div class="tab-title">New User?</div>', unsafe_allow_html=True)
                st.markdown('<div class="tab-sub">Register to start analyzing statements</div>', unsafe_allow_html=True)

                new_user = st.text_input("Choose Username", key="reg_user")
                new_pass = st.text_input("Choose Password", type="password", key="reg_pass")

                if st.button("Register", use_container_width=True):

                    if register_user(new_user, new_pass):
                        st.success("Account created! You can now login.")

                    else:
                        st.error("Username already exists, Log in to continue")

            st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# MAIN DASHBOARD (AFTER LOGIN)
# ==============================
if st.session_state.logged_in:
    st.sidebar.title(f"Welcome, {st.session_state.username} ")
    if st.sidebar.button("logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.rerun()
    st.markdown("""
    <div class="head">
    <h1>💳 Bank Statement Analyzer</h1>
    <p>Upload your bank statement and instantly understand where your money goes</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload file here:",
        type=["csv","xlsx","xls"]
    )

    if uploaded_file is None:
        st.markdown("""<div class="insight-card" style="text-align:center;"><strong>How to get your bank statement?</strong><br>Login to your net banking → Go to Account Statement → Download as CSV or Excel → Upload here</div>""", unsafe_allow_html=True)
# ==============================
# DATA PREVIEW
# ==============================

    if uploaded_file:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.markdown('<div class="section-title">Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(5), use_container_width=True)


# ==============================
# COLUMN DETECTION
# ==============================

        def auto_detect_columns(columns):

            detected = {}

            for col in columns:

                col_lower = col.lower()

                if "date" in col_lower:
                    detected["date"] = col

                elif "description" in col_lower:
                    detected["description"] = col

                elif "debit" in col_lower:
                    detected["debit"] = col

                elif "credit" in col_lower:
                    detected["credit"] = col

                elif "transaction" in col_lower:
                    detected["transaction_id"] = col

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
            st.error("The uploaded file does not appear to be a valid bank statement.\n\n"
        "Please ensure your file contains Date, Description, Debit, and Credit columns.")
            st.stop()
       


# ==============================
# ANALYSIS BUTTON
# ==============================

       
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            analyze = st.button("View Spending Analysis",use_container_width=True)
        if analyze:
            with st.spinner("Analyzing transactions..."):
                time.sleep(1)

                cols = [detected["date"],detected["description"],detected["debit"],detected["credit"]]
                names = ["date","description","debit","credit"]

                if "transaction_id" in detected:
                    cols.insert(1,detected["transaction_id"])
                    names.insert(1,"transaction_id")

                df_clean = df[cols].copy()
                df_clean.columns = names

                df_clean["debit"] = pd.to_numeric(df_clean["debit"], errors="coerce").fillna(0)
                df_clean["credit"] = pd.to_numeric(df_clean["credit"], errors="coerce").fillna(0)


# ==============================
# CATEGORIZATION
# ==============================

                if "transaction_id" in df_clean.columns:
                    df_clean["category"] = df_clean.apply(
                        lambda row: categorize(row["transaction_id"], row["description"]), axis=1
                    )

                    df_clean["payment_method"] = df_clean["transaction_id"].apply(get_txn_prefix)

                else:
                    df_clean["category"] = df_clean["description"].apply(categorize_by_description)



#KPI Cards
                total_income  = df_clean["credit"].sum()
                total_expense = df_clean["debit"].sum()
                net_savings   = total_income - total_expense
                savings_pct   = (net_savings / total_income * 100) if total_income > 0 else 0
                st.markdown('<div class="section-title">KPI Metrics</div>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Total Income</div>
                        <div class="metric-value ">{total_income:,.0f}</div></div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Total Expense</div>
                        <div class="metric-value ">{total_expense:,.0f}</div></div>""",unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Net Savings</div>
                        <div class="metric-value ">{net_savings:,.0f}</div></div>""",unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-title">Savings Rate</div>
                        <div class="metric-value ">{savings_pct:,.1f}%</div></div>""",unsafe_allow_html=True)
                st.markdown("")

# ==============================
# CHARTS
# ==============================

                expenses_df = df_clean[df_clean["debit"]>0]

                category_summary = expenses_df.groupby("category")["debit"].sum().reset_index()

                col1,col2 = st.columns(2)

                with col1:
                    fig1 = px.pie(category_summary,values="debit",names="category")
                    st.plotly_chart(fig1,use_container_width=True)

                with col2:
                    fig2 = px.bar(category_summary,x="debit",y="category",orientation="h",text='debit')
                    fig2.update_xaxes(showgrid=True)
                    fig2.update_yaxes(showgrid=True)
                    fig2.update_traces(textposition="outside")
                    st.plotly_chart(fig2,use_container_width=True)


            
                    # Payment Method chart — only shown if transaction_id column was found
                if "payment_method" in df_clean.columns:
                    st.markdown('<div class="section-title">Payment Method Breakdown</div>', unsafe_allow_html=True)
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
                        fig4 = px.bar(pm_group, x="Payment Method", y="Amount", title="Spending by Payment Method (₹)", color="Payment Method", text="Amount")
                        fig4.update_xaxes(showgrid=True)
                        fig4.update_yaxes(showgrid=True)
                        fig4.update_traces(textposition="outside")
                        st.plotly_chart(fig4, use_container_width=True)