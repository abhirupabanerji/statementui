import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from categorizer import categorize, get_txn_prefix, categorize_by_description
import time
from database import create_connection, create_table
from auth import login_user, register_user
from mldetection import detect_anomalies
from sklearn.metrics import silhouette_score

st.set_page_config(layout="wide", page_icon='💳', page_title='Bank Statement Analyzer')
create_table()

def detect_recurring(df):
    df_copy = df.copy()

    # Create a single amount column
    df_copy["amount"] = df_copy["debit"] + df_copy["credit"]

    # Round amount to avoid small differences
    df_copy["amount_round"] = df_copy["amount"].round(-1)

    # Group by description + amount
    grouped = df_copy.groupby(["description", "amount_round"])

    recurring = []

    for (desc, amt), group in grouped:
        if len(group) >= 3:  # appears at least 3 times
            recurring.append({
                "description": desc,
                "amount": amt,
                "count": len(group)
            })

    return pd.DataFrame(recurring)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "home"
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
}
.insight-card.danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
}
.insight-card.success {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.3);
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


# MAIN DASHBOARD (AFTER LOGIN)
def show_analysis():    
    uploaded_file = st.session_state.get("uploaded_file")   
    # DATA PREVIEW
    if uploaded_file:
        try:
            uploaded_file.seek(0)   

            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.markdown('<div class="section-title">Data Preview</div>', unsafe_allow_html=True) 
            st.dataframe(df.head(5), use_container_width=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()
            st.markdown('<div class="section-title">Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(df.head(5), use_container_width=True)

    # COLUMN DETECTION
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
       
    # ANALYSIS BUTTON
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
                st.session_state.full_df = df_clean   # ✅ store everything

    # CATEGORIZATION
                if "transaction_id" in df_clean.columns:
                    df_clean["category"] = df_clean.apply(lambda row: categorize(row["transaction_id"], row["description"]), axis=1)

                    df_clean["payment_method"] = df_clean["transaction_id"].apply(get_txn_prefix)

                else:
                    df_clean["category"] = df_clean["description"].apply(categorize_by_description)
                
                st.session_state.anomaly_df = detect_anomalies(df_clean)
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
                if total_expense > total_income:
                    st.error("⚠️ You are overspending!")
                elif savings_pct < 20:
                    st.warning("⚠️ Low savings rate")
                else:
                    st.success("✅ Healthy financial habits")
                st.markdown("")

    # CHARTS
                with st.expander("View category wise transaction distribution"):

                    expenses_df = df_clean[df_clean["debit"] > 0]   # ✅ only for charts

                    category_summary = (expenses_df.groupby("category")["debit"].sum().reset_index())

                    recurring_df = detect_recurring(df_clean)
                    col1, col2 = st.columns(2)
                    with col1:
                        fig1 = px.pie(category_summary, values="debit", names="category")
                        st.plotly_chart(fig1, use_container_width=True)
                    with col2:
                        fig2 = px.bar(category_summary, x="debit", y="category", orientation="h", text="debit")
                        fig2.update_traces(textposition="outside")
                        st.plotly_chart(fig2, use_container_width=True)


                
    # Payment Method chart — only shown if transaction_id column was found
                with st.expander("View payment method wise transaction distribution"):
                    if "payment_method" in df_clean.columns:
                        st.markdown('<div class="section-title">Payment Method Breakdown</div>', unsafe_allow_html=True)
                        pm_summary = expenses_df.copy()
                        pm_summary["payment_method"] = df_clean.loc[expenses_df.index, "payment_method"]
                        pm_group = pm_summary.groupby("payment_method")["debit"].sum().reset_index()
                        pm_group.columns = ["Payment Method", "Amount"]
        
                        ch3, ch4 = st.columns(2)
                        with ch3:
                            fig3 = px.pie(pm_group, values="Amount", names="Payment Method",title="How are you paying?", hole=0.40)
                            st.plotly_chart(fig3, use_container_width=True)
        
                        with ch4:
                            fig4 = px.bar(pm_group, x="Payment Method", y="Amount", title="Spending by Payment Method (₹)", color="Payment Method", text="Amount")
                            fig4.update_xaxes(showgrid=True)
                            fig4.update_yaxes(showgrid=True)
                            fig4.update_traces(textposition="outside")
                            st.plotly_chart(fig4, use_container_width=True)
                        # AFTER everything is computed
                        st.session_state.expenses_df = expenses_df
                        st.session_state.category_summary = category_summary
                        st.session_state.recurring = recurring_df

def show_transactions():
    if "expenses_df" not in st.session_state:
        st.warning("Run analysis first to view transactions.")
    else:
        st.markdown('<div class="section-title">View your transactions</div>', unsafe_allow_html=True)

        df = st.session_state.full_df.copy()

        search = st.text_input("Search for transactions:")

        if search:
            search = search.strip() #removes unnecessary spaces

            df = df[df["description"]
                .astype(str)  # everything becomes string
                .str.contains(search, case=False, na=False)  #removes casing dependency or removing mmissing values
                ]

        st.dataframe(df, use_container_width=True)
def show_insights():

    if "category_summary" not in st.session_state:
        st.warning("Run analysis first to generate insights.")
        return

    category_summary = st.session_state.category_summary
    expenses_df = st.session_state.expenses_df

    st.title("Spending Insights")
    st.markdown('<div class="section-title">Get quick insights on your spendings</div>', unsafe_allow_html=True)

    top_category = category_summary.sort_values("debit", ascending=False).iloc[0]
    largest_txn = expenses_df.loc[expenses_df["debit"].idxmax()]
    avg_spend = expenses_df["debit"].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="insight-card">
        <b>Top Category</b><br>
        {top_category['debit']:.0f} spent on {top_category['category']}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="insight-card warning">
        <b>Largest Transaction</b><br>
        {largest_txn['debit']:.0f} on {largest_txn['description']}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="insight-card success">
        <b>Average Spend</b><br>
        {avg_spend:.0f} per transaction
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

     # RECURRING TRANSACTIONS
    with st.expander("Tap to view Recurring Transactions"):
        if "recurring" in st.session_state and not st.session_state.recurring.empty:
            st.markdown('<div class="section-title">🔁Recurring Transactions</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state.recurring)

def anomaly_detection():
    if "anomaly_df" not in st.session_state or st.session_state.anomaly_df is None:
        st.warning("Run analysis first or not enough data.")
        return

    st.title("Detect Unusual Patterns in Your Transaction")

    df = st.session_state.anomaly_df
    anomalies = df[df["anomaly"] == 1]

    # Anomaly rate — should ideally be 1–5% for financial data
    anomaly_rate = len(anomalies) / len(df) * 100
    st.subheader("📊 Model Evaluation Metrics")

    # --- Metrics row: adapts based on whether anomaly_score exists ---
    if "anomaly_score" in df.columns:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Anomaly Rate", f"{anomaly_rate:.2f}%", help="Healthy range: 1–5%")
        with col2:
            st.metric("Total Anomalies", len(anomalies))
        with col3:
            st.metric("Highest Anomaly", f"₹{anomalies['debit'].max():,.0f}" if not anomalies.empty else "₹0")
        with col4:
            st.metric("Avg Anomaly Score", f"{df['anomaly_score'].mean():.4f}", help="Higher = more anomalous")
        with col5:
            avg_score = anomalies['anomaly_score'].mean() if not anomalies.empty else 0
            st.metric("Avg Score (Anomalies)", f"{avg_score:.4f}")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Anomaly Rate", f"{anomaly_rate:.2f}%", help="Healthy range: 1–5%")
        with col2:
            st.metric("Total Anomalies", len(anomalies))
        with col3:
            st.metric("Highest Anomaly", f"₹{anomalies['debit'].max():,.0f}" if not anomalies.empty else "₹0")

    st.markdown("---")

    # --- Score distribution chart (only if score column exists) ---
    with st.expander("Anomaly Score Distribution"):
        if "anomaly_score" in df.columns:
            fig_score = px.histogram(
                df, x="anomaly_score",
                color=df["anomaly"].map({0: "Normal", 1: "Anomaly"}),
                barmode="overlay",
                opacity=0.7
            )
            st.plotly_chart(fig_score, use_container_width=True)

    # --- Anomaly results ---
    if anomalies.empty:
        st.success("No unusual transactions detected 🎉")
    else:
        fig_anom = px.scatter(df, x="date", y="debit", color=df["anomaly"].map({0: "Normal", 1: "Anomaly"}), title="Anomaly Detection")
        st.plotly_chart(fig_anom, use_container_width=True)
        st.dataframe(anomalies, use_container_width=True)
        st.info("Isolation Forest is used for detecting unusual transactions")

#LANDING LOGIN PAGE

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
        login_tab, register_tab = st.tabs(["Login", "Register"])

        # LOGIN
        with login_tab:

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Log In", use_container_width=True):

                if login_user(username, password):

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = "analysis"

                    st.success("Login successful")
                    st.rerun()

                else:

                    st.error("Invalid username or password")

        # REGISTER
        with register_tab:

            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")

            if st.button("Register", use_container_width=True):

                if register_user(new_user, new_pass):

                    st.success("Account created! Login now.")

                else:
                    st.error("Username already exists.")

    

if st.session_state.logged_in:

    col1, col2 = st.columns([8, 1])

    # -------- SIDEBAR --------
    with col1:
        st.sidebar.markdown(f"### 👋 Welcome, {st.session_state.username}")

    # -------- PROFILE --------
    with col2:
        with st.popover("👤"):
            st.write("**User Profile**")
            st.write(f"Username - {st.session_state.username}")
            st.write("Email: user@example.com")

            if st.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()

    # -------- MAIN HEADER --------
    st.markdown("""
    <div class="head">
        <h1>💳 Bank Statement Analyzer</h1>
        <p>Upload your bank statement and instantly understand where your money goes</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # -------- FILE UPLOAD --------
    uploaded_file = st.file_uploader("Upload file here:", type=["csv","xlsx","xls"])

    if uploaded_file is not None:

    # Only update if NEW file
        if "uploaded_file" not in st.session_state or uploaded_file != st.session_state.uploaded_file:

            st.session_state.uploaded_file = uploaded_file

            # Clear analysis ONLY when new file uploaded
            st.session_state.pop("expenses_df", None)
            st.session_state.pop("category_summary", None)
            st.session_state.pop("recurring", None)

    # CASE 2: File removed
    else:
        st.session_state.pop("uploaded_file", None)
        st.session_state.pop("expenses_df", None)
        st.session_state.pop("category_summary", None)
        st.session_state.pop("recurring", None)

    if uploaded_file is None:
        st.markdown("""
        <div class="insight-card" style="text-align:center;">
        <strong>How to get your bank statement?</strong><br>
        Login to your net banking → Download → Upload here
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------- NAV BUTTONS --------
    if st.session_state.get("uploaded_file"):
        # Initialize page state
        if "page" not in st.session_state:
            st.session_state.page = "analyse"

        # Sidebar Navigation
        st.sidebar.markdown("## 📂 Navigation")

        if st.sidebar.button("📊 Analyse", use_container_width=True):
            st.session_state.page = "analyse"

        if st.sidebar.button("💡 Insights", use_container_width=True):
            st.session_state.page = "insights"

        if st.sidebar.button("📜 Transactions", use_container_width=True):
            st.session_state.page = "transactions"

        if st.sidebar.button("🤖 Anomaly Detection", use_container_width=True):
            st.session_state.page = "anomaly"

        # Load selected page
        page = st.session_state.page

        if page == "analyse":
            show_analysis()

        elif page == "insights":
            show_insights()

        elif page == "transactions":
            show_transactions()

        elif page =="anomaly":
            anomaly_detection()
