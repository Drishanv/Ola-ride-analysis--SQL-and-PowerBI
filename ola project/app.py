# app.py — OLA Rides Insights (with resilient Power BI PDF viewer)
# -------------------------------------------------------------
# Tabs:
#   1) Project Overview (Problem Statement + Business Use Cases)
#   2) Explore (filters, KPIs, quick charts, searchable table)
#   3) SQL Runner (predefined & custom SELECT queries)
#   4) Power BI (PDF) — robust viewer (component -> images -> download)
#
# Expects:
#   - SQLite DB file 'ola_rides.db' with a table named 'bookings'
#   - Exported Power BI PDF named 'Ola ride analysis.pdf' (or upload in UI)

import os
import sqlite3
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="OLA Rides Insights", layout="wide")

# ---------- Helpers (no caching on functions that take a sqlite3.Connection)
@st.cache_resource(show_spinner=False)
def get_conn(db_path: str):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")
    return sqlite3.connect(db_path, check_same_thread=False)

def run_sql_df(conn, sql: str, params: tuple = ()):
    """Execute SQL and return a DataFrame (no caching here)."""
    return pd.read_sql_query(sql, conn, params=params)

def list_tables(conn):
    q = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    return pd.read_sql_query(q, conn)["name"].tolist()

def list_views(conn):
    q = "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
    return pd.read_sql_query(q, conn)["name"].tolist()

@st.cache_data(show_spinner=False)
def distinct_values(db_path: str, table: str, col: str):
    """
    Cached distinct values for filters.
    Uses db_path (hashable) instead of a live connection (unhashable).
    """
    temp_conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        df = pd.read_sql_query(
            f"SELECT DISTINCT {col} AS v FROM {table} WHERE {col} IS NOT NULL ORDER BY 1",
            temp_conn
        )
        return df["v"].dropna().astype(str).tolist()
    finally:
        temp_conn.close()

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# ---------- Sidebar: DB connect (robust default path)
APP_DIR = Path(__file__).parent
default_db = str((APP_DIR / "ola_rides.db").resolve())

st.sidebar.header("🔌 Data Source")
db_path = st.sidebar.text_input("SQLite DB path", value=default_db)

# Create/store a single connection resource
if "conn" not in st.session_state and os.path.exists(db_path):
    st.session_state.conn = get_conn(db_path)

if st.sidebar.button("Connect / Refresh", use_container_width=True):
    st.session_state.conn = get_conn(db_path)

if "conn" not in st.session_state:
    st.warning("Connect to your SQLite DB to continue.")
    st.stop()

conn = st.session_state.conn

# ---------- Inspect schema
tables = list_tables(conn)
views = list_views(conn)
table = "bookings" if "bookings" in tables else (tables[0] if tables else None)
if not table:
    st.error("No tables found in the database.")
    st.stop()

sample = run_sql_df(conn, f"SELECT * FROM {table} LIMIT 5")
all_cols = sample.columns.tolist()

has_date     = "date" in all_cols
has_status   = "booking_status" in all_cols
has_vehicle  = "vehicle_type" in all_cols
has_payment  = "payment_method" in all_cols
has_cust_id  = "customer_id" in all_cols
has_pickup   = "pickup_location" in all_cols
has_drop     = "drop_location" in all_cols

# ---------- Tabs (added a 4th tab for Power BI PDF)
tab_overview, tab_explore, tab_sql, tab_pdf = st.tabs(
    ["📘 Project Overview", "🔭 Explore", "🧠 SQL Runner", "📄 Power BI Visuals"]
)

# ====== 1) OVERVIEW ======
with tab_overview:
    st.title("🚖 OLA Rides Insights — Project Overview")

    st.subheader("Problem Statement")
    st.markdown("""
The rise of ride-sharing platforms has transformed urban mobility, offering convenience and affordability to millions of users.
**OLA** generates vast amounts of data (bookings, driver availability, pricing, preferences). To enhance operational efficiency,
improve customer satisfaction, and optimize strategy, this project cleans and analyzes OLA’s data, performs EDA, and presents insights
in an interactive Streamlit application by embedding Power BI visuals).
""")

    st.subheader("Business Use Cases")
    st.markdown("""
- **Peak demand management** — Identify high-demand periods/zones to optimize **driver allocation**.  
- **Customer behavior** — Segment riders for **personalized marketing** and retention.  
- **Pricing intelligence** — Understand pricing patterns and **surge effectiveness**.  
- **Risk & anomalies** — Detect **outliers/fraud** (abnormal booking values, repeated cancels).  
- **Quality monitoring** — Track **ratings** to improve driver performance & customer experience**.  
    """)

    st.caption(f"Connected DB: **{db_path}** | Tables: {', '.join(tables)} | Views: {', '.join(views) or '—'}")

# ====== 2) EXPLORE (table only) ======
with tab_explore:
    st.title("🔭 Explore — Filter Table Data")

    # ---- Filters
    st.sidebar.header("🔎 Filters")
    status = st.sidebar.selectbox(
        "Booking Status", ["All"] + (distinct_values(db_path, table, "booking_status") if has_status else [])
    )
    vehicle = st.sidebar.selectbox(
        "Vehicle Type", ["All"] + (distinct_values(db_path, table, "vehicle_type") if has_vehicle else [])
    )
    payment = st.sidebar.selectbox(
        "Payment Method", ["All"] + (distinct_values(db_path, table, "payment_method") if has_payment else [])
    )

    if has_date:
        bounds = run_sql_df(conn, f"SELECT MIN(date) AS min_d, MAX(date) AS max_d FROM {table}").iloc[0]
        min_d = pd.to_datetime(bounds["min_d"]).date() if pd.notna(bounds["min_d"]) else date(2020,1,1)
        max_d = pd.to_datetime(bounds["max_d"]).date() if pd.notna(bounds["max_d"]) else date.today()
        date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
    else:
        date_range = None

    search = st.sidebar.text_input("Search (Customer / Pickup / Drop)")
    st.sidebar.caption("Tip: Enter partial text; search checks multiple columns when available.")

    # ---- WHERE builder
    where, params = [], []
    if has_status and status != "All":
        where.append("booking_status = ?"); params.append(status)
    if has_vehicle and vehicle != "All":
        where.append("vehicle_type = ?"); params.append(vehicle)
    if has_payment and payment != "All":
        where.append("payment_method = ?"); params.append(payment)
    if has_date and isinstance(date_range, tuple) and len(date_range) == 2:
        where.append("date BETWEEN ? AND ?"); params.extend([str(date_range[0]), str(date_range[1])])
    if search:
        sub = []
        if has_cust_id: sub.append("CAST(customer_id AS TEXT) LIKE ?")
        if has_pickup:  sub.append("LOWER(pickup_location) LIKE ?")
        if has_drop:    sub.append("LOWER(drop_location) LIKE ?")
        if sub:
            where.append("(" + " OR ".join(sub) + ")")
            if has_cust_id: params.append(f"%{search}%")
            if has_pickup:  params.append(f"%{search.lower()}%")
            if has_drop:    params.append(f"%{search.lower()}%")

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    base_sql = f"SELECT * FROM {table} {where_sql}"
    df_filtered = run_sql_df(conn, base_sql, tuple(params))

    # ---- Show table only
    st.subheader("Filtered Results")
    st.dataframe(df_filtered, use_container_width=True, height=520)
    st.download_button(
        "Download filtered CSV",
        data=to_csv_bytes(df_filtered),
        file_name="ola_filtered.csv",
        mime="text/csv"
    )

# ====== 3) SQL RUNNER ======
with tab_sql:
    st.title("🧠 SQL Runner")

    views = list_views(conn)
    v = {name: (name in views) for name in [
        "successful_bookings","avg_vehicle_types","count_cancelled_ride_by_customers",
        "Top_5_customers","cancelled_by_drivers","min_max_driver_ratings",
        "Pay_UPI","Avg_Customer_Rating","Total_values","incomplete_rides"
    ]}

    predefined = {
        "Successful bookings":
            ("SELECT * FROM successful_bookings" if v["successful_bookings"]
             else "SELECT * FROM bookings WHERE booking_status = 'Success'"),

        "Avg distance by vehicle":
            ("SELECT * FROM avg_vehicle_types" if v["avg_vehicle_types"]
             else "SELECT vehicle_type, AVG(ride_distance) AS avg_distance FROM bookings GROUP BY vehicle_type"),

        "Cancelled by customers":
            ("SELECT * FROM count_cancelled_ride_by_customers" if v["count_cancelled_ride_by_customers"]
             else "SELECT COUNT(*) AS total_cancelled_by_customers FROM bookings WHERE booking_status='Canceled_Rides_by_Customer'"),

        "Top 5 customers by rides":
            ("SELECT * FROM Top_5_customers" if v["Top_5_customers"]
             else "SELECT customer_id, COUNT(booking_id) AS total_rides FROM bookings GROUP BY customer_id ORDER BY total_rides DESC LIMIT 5"),

        "Driver cancels (personal/car)":
            ("SELECT * FROM cancelled_by_drivers" if v["cancelled_by_drivers"]
             else "SELECT COUNT(*) AS driver_cancel_personal_car FROM bookings WHERE Canceled_Rides_by_Driver='Personal & Car releated issue'"),

        "Min/Max driver rating (Prime Sedan)":
            ("SELECT * FROM min_max_driver_ratings" if v["min_max_driver_ratings"]
             else "SELECT MAX(driver_ratings) AS max_rating, MIN(driver_ratings) AS min_rating FROM bookings WHERE vehicle_type='Prime Sedan'"),

        "UPI payments":
            ("SELECT * FROM Pay_UPI" if v["Pay_UPI"]
             else "SELECT * FROM bookings WHERE payment_method='UPI'"),

        "Avg customer rating per vehicle":
            ("SELECT * FROM Avg_Customer_Rating" if v["Avg_Customer_Rating"]
             else "SELECT vehicle_type, AVG(customer_rating) AS Avg_Cust_Rating FROM bookings GROUP BY vehicle_type"),

        "Total booking value (successful)":
            ("SELECT * FROM Total_values" if v["Total_values"]
             else "SELECT SUM(booking_value) AS total_success_value FROM bookings WHERE booking_status='Success'"),

        "Incomplete rides with reason":
            ("SELECT * FROM incomplete_rides" if v["incomplete_rides"]
             else "SELECT booking_id, Incomplete_Rides_Reason FROM bookings WHERE Incomplete_Rides='Yes'")
    }

    c1, c2 = st.columns([1,2])
    with c1:
        chosen = st.selectbox("Pick a predefined query", list(predefined.keys()))
    with c2:
        sql_text = st.text_area("SQL (read-only: SELECT)", value=predefined[chosen], height=140)

    col_go, col_clear = st.columns([1,1])
    with col_go:
        if st.button("Run SQL", use_container_width=True):
            try:
                if not sql_text.strip().lower().startswith("select"):
                    st.error("Only SELECT statements are allowed in the app.")
                else:
                    res = run_sql_df(conn, sql_text)
                    st.success(f"Returned {len(res)} rows")
                    st.dataframe(res, use_container_width=True, height=420)
                    st.download_button(
                        "Download results as CSV",
                        data=to_csv_bytes(res),
                        file_name="sql_results.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Query error: {e}")
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.experimental_rerun()

# ====== 4) POWER BI (PDF) — robust viewer ======
with tab_pdf:
    st.title("📄 Power BI Visuals")

    DEFAULT_PDF_NAME = "Ola ride analysis.pdf"
    PAGE_TITLES = ["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings"]  # rename if needed
    pdf_path = (APP_DIR / DEFAULT_PDF_NAME)

    with st.expander("PDF source / upload", expanded=False):
        st.write(
            "The app looks for a PDF called "
            f"`{DEFAULT_PDF_NAME}` next to `app.py`. If it's not found, upload it below."
        )

    uploaded = None
    if not pdf_path.exists():
        uploaded = st.file_uploader("Upload your Power BI PDF", type=["pdf"])
        if uploaded is not None:
            pdf_bytes = uploaded.read()
            st.success("PDF loaded from upload.")
    else:
        st.success(f"Found PDF file: {pdf_path.name}")

    @st.cache_data(show_spinner=False)
    def load_pdf_bytes_from_disk(path: Path) -> bytes:
        return path.read_bytes()

    pdf_bytes: bytes | None = None
    if pdf_path.exists():
        try:
            pdf_bytes = load_pdf_bytes_from_disk(pdf_path)
        except Exception as e:
            st.error(f"Couldn't read `{pdf_path}`: {e}")
    elif uploaded is not None:
        # Already read into pdf_bytes above
        pass

    # If uploaded but pdf_bytes not set from disk path, use uploaded buffer
    if (uploaded is not None) and (pdf_bytes is None):
        pdf_bytes = uploaded.getvalue()

    st.divider()
    st.subheader("Viewer")

    if not pdf_bytes:
        st.warning(
            "No PDF available yet. Upload the file above or place "
            f"`{DEFAULT_PDF_NAME}` next to `app.py` and refresh."
        )
    else:
        # Try 1: dedicated PDF component (best UX)
        tried_component = False
        try:
            from streamlit_pdf_viewer import pdf_viewer  # pip install streamlit-pdf-viewer
            tried_component = True
            pdf_viewer(
                pdf_bytes,
                height=900,
                pages_to_render=list(range(1, len(PAGE_TITLES) + 1)),  # 1..5
                render_text=True,
                key="pbi_pdf_viewer",
            )
        except Exception as _e_component:
            # Try 2: render pages to PNG (works in all browsers)
            try:
                import fitz  # PyMuPDF
                @st.cache_data(show_spinner=False)
                def render_pdf_to_images(pdf_raw: bytes, zoom: float = 2.0):
                    imgs = []
                    with fitz.open(stream=pdf_raw, filetype="pdf") as doc:
                        mat = fitz.Matrix(zoom, zoom)
                        for i, page in enumerate(doc):
                            pix = page.get_pixmap(matrix=mat, alpha=False)
                            imgs.append((i+1, pix.tobytes("png")))
                    return imgs

                colz1, colz2 = st.columns([1,3])
                with colz1:
                    zoom = st.slider("Render scale", 1.0, 3.0, 2.0, 0.25)
                with colz2:
                    st.caption("Increase scale for sharper images on big screens.")

                images = render_pdf_to_images(pdf_bytes, zoom=zoom)

                # Page subtabs
                subtabs = st.tabs(PAGE_TITLES)
                for (page_no, png), subtab in zip(images, subtabs):
                    with subtab:
                        title = PAGE_TITLES[page_no-1] if page_no-1 < len(PAGE_TITLES) else f"Page {page_no}"
                        st.caption(f"Page {page_no} — {title}")
                        st.image(png, use_column_width=True)
                        st.download_button(
                            f"Download page {page_no} as PNG",
                            data=png,
                            file_name=f"powerbi_page_{page_no}.png",
                            mime="image/png",
                            key=f"dl_png_{page_no}"
                        )
            except Exception as _e_images:
                # Try 3: fall back to download/open
                if tried_component:
                    st.info("Your browser blocked embedded PDFs. Use the download button or open in another browser.")
                else:
                    st.info("Viewer component unavailable. Use the download button or try another browser.")
                st.download_button(
                    "Download original PDF",
                    data=pdf_bytes,
                    file_name=DEFAULT_PDF_NAME,
                    mime="application/pdf",
                )

# ------------------- Footer -------------------
st.caption(
    "Tip: Rename/reorder the PDF page tabs via PAGE_TITLES in the '📄 Power BI (PDF)' section."
)
