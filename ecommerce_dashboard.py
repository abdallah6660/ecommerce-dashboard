import copy
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.stApp { background: #080b12; color: #dde1f0; }

section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1a2035;
}
section[data-testid="stSidebar"] * { color: #c0c8de !important; }

[data-testid="metric-container"] {
    background: #0d1117;
    border: 1px solid #1a2035;
    border-radius: 10px;
    padding: 18px 20px;
    transition: border-color 0.25s, transform 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: #00e5ff;
    transform: translateY(-2px);
}
[data-testid="metric-container"] label {
    color: #606880 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #dde1f0 !important;
    font-size: 1.55rem !important;
    font-weight: 600;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}

.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #00e5ff;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1a2035;
}
.main-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.45rem;
    font-weight: 600;
    color: #dde1f0;
}
.main-subtitle {
    color: #404860;
    font-size: 0.88rem;
    margin-top: 3px;
}

hr { border-color: #1a2035 !important; margin: 8px 0 !important; }
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #0d1117 !important;
    border-color: #1a2035 !important;
    color: #dde1f0 !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080b12; }
::-webkit-scrollbar-thumb { background: #1a2035; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Colors ───────────────────────────────────────────────────────────────────
CAT_COLORS = {
    "Electronics":  "#00e5ff",
    "Fashion":      "#ff4d8d",
    "Accessories":  "#ffc145",
}
PROD_COLORS = [
    "#00e5ff","#ff4d8d","#ffc145","#7c5cfc",
    "#00d68f","#ff7043","#40c4ff","#e040fb",
]
PAY_COLORS  = ["#00e5ff", "#7c5cfc", "#ffc145"]
CITY_COLORS = ["#00e5ff","#ff4d8d","#ffc145","#7c5cfc","#00d68f","#ff7043"]

BG       = "#0d1117"
GRID_C   = "#1a2035"
TEXT_C   = "#8090b0"
ACCENT   = "#00e5ff"

_BASE = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(family="IBM Plex Sans", color=TEXT_C, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C, tickfont=dict(size=11)),
)
def bl(**kw):
    l = copy.deepcopy(_BASE)
    l.update(kw)
    return l

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("realistic_ecommerce_data.csv", parse_dates=["Order_Date"])
    df["Month"]      = df["Order_Date"].dt.to_period("M").astype(str)
    df["MonthName"]  = df["Order_Date"].dt.strftime("%b %Y")
    df["MonthShort"] = df["Order_Date"].dt.strftime("%b")
    df["Quarter"]    = df["Order_Date"].dt.to_period("Q").astype(str)
    df["DayOfWeek"]  = df["Order_Date"].dt.day_name()
    df["WeekNum"]    = df["Order_Date"].dt.isocalendar().week.astype(int)
    return df

df = load_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">Date Range</div>', unsafe_allow_html=True)
    months_sorted = sorted(df["Month"].unique())
    month_range = st.select_slider(
        "Select period",
        options=months_sorted,
        value=(months_sorted[0], months_sorted[-1]),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown('<div class="section-title">Category</div>', unsafe_allow_html=True)
    all_cats = sorted(df["Category"].unique())
    selected_cats = st.multiselect("", all_cats, default=all_cats,
                                   label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-title">Payment Method</div>', unsafe_allow_html=True)
    all_pay = sorted(df["Payment_Method"].unique())
    selected_pay = st.multiselect("", all_pay, default=all_pay,
                                  label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-title">City</div>', unsafe_allow_html=True)
    all_cities = sorted(df["City"].unique())
    selected_cities = st.multiselect("", all_cities, default=all_cities,
                                     label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-title">Include Returns</div>', unsafe_allow_html=True)
    include_returned = st.toggle("Show returned orders", value=True)

# ─── Filter ───────────────────────────────────────────────────────────────────
mask = (
    (df["Month"] >= month_range[0]) &
    (df["Month"] <= month_range[1]) &
    (df["Category"].isin(selected_cats)) &
    (df["Payment_Method"].isin(selected_pay)) &
    (df["City"].isin(selected_cities))
)
if not include_returned:
    mask &= (df["Returned"] == 0)
filtered = df[mask].copy()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:22px">
  <div class="main-title">E-Commerce Sales Dashboard</div>
  <div class="main-subtitle">Sales intelligence · Egypt Market · 2023</div>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No data matches the selected filters. Please adjust your selection.")
    st.stop()

# ─── KPIs ─────────────────────────────────────────────────────────────────────
total_rev    = filtered["Total_Sales"].sum()
total_orders = len(filtered)
avg_order    = filtered["Total_Sales"].mean()
total_qty    = filtered["Quantity"].sum()
return_rate  = filtered["Returned"].mean() * 100
avg_discount = filtered["Discount"].mean() * 100

# Compare to full dataset for deltas
all_avg_order = df["Total_Sales"].mean()
all_return    = df["Returned"].mean() * 100

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Total Revenue",   f"{total_rev:,.0f} EGP")
k2.metric("Total Orders",    f"{total_orders:,}")
k3.metric("Avg Order Value", f"{avg_order:,.0f} EGP",
          f"{avg_order - all_avg_order:+,.0f} vs all")
k4.metric("Units Sold",      f"{total_qty:,}")
k5.metric("Return Rate",     f"{return_rate:.1f}%",
          f"{return_rate - all_return:+.1f}% vs all")
k6.metric("Avg Discount",    f"{avg_discount:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 1: Revenue Trend + Category Breakdown ───────────────────────────────
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="section-title">Monthly Revenue Trend</div>', unsafe_allow_html=True)

    monthly = (
        filtered.groupby(["Month", "MonthName"])["Total_Sales"]
        .sum().reset_index().sort_values("Month")
    )
    monthly_orders = (
        filtered.groupby("Month")
        .size().reset_index(name="Orders").sort_values("Month")
    )
    monthly = monthly.merge(monthly_orders, on="Month")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["MonthName"], y=monthly["Total_Sales"],
        fill="tozeroy", fillcolor="rgba(0,229,255,0.06)",
        line=dict(color=ACCENT, width=2.5),
        mode="lines+markers",
        marker=dict(size=6, color=ACCENT, line=dict(width=2, color=BG)),
        name="Revenue",
        hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f} EGP<extra></extra>"
    ))
    fig_trend.add_trace(go.Bar(
        x=monthly["MonthName"], y=monthly["Orders"],
        yaxis="y2", name="Orders",
        marker_color="rgba(124,92,252,0.4)",
        hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>"
    ))
    fig_trend.update_layout(
        **bl(height=300, showlegend=True,
             yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickfont=dict(size=11), tickformat=",",
                        title=dict(text="Revenue (EGP)", font=dict(size=11, color=TEXT_C))),
             yaxis2=dict(overlaying="y", side="right", showgrid=False,
                         tickfont=dict(size=11), zeroline=False,
                         title=dict(text="Orders", font=dict(size=11, color=TEXT_C))),
             legend=dict(bgcolor=BG, font=dict(size=10), orientation="h",
                         x=0, y=1.12))
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.markdown('<div class="section-title">Revenue by Category</div>', unsafe_allow_html=True)

    cat_totals = filtered.groupby("Category")["Total_Sales"].sum().reset_index()
    cat_totals = cat_totals.sort_values("Total_Sales", ascending=False)

    fig_cat = go.Figure(go.Pie(
        labels=cat_totals["Category"],
        values=cat_totals["Total_Sales"],
        marker_colors=[CAT_COLORS.get(c, "#888") for c in cat_totals["Category"]],
        hole=0.55,
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} EGP (%{percent})<extra></extra>",
    ))
    fig_cat.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="IBM Plex Sans", color=TEXT_C),
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(bgcolor=BG, font=dict(size=10), orientation="v", x=1.02)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ─── Row 2: Top Products + Payment Methods ────────────────────────────────────
c3, c4 = st.columns([3, 2])

with c3:
    st.markdown('<div class="section-title">Top Products by Revenue</div>', unsafe_allow_html=True)

    prod_totals = (
        filtered.groupby("Product")
        .agg(Revenue=("Total_Sales","sum"), Orders=("Order_ID","count"))
        .reset_index().sort_values("Revenue", ascending=True)
    )
    colors_bar = PROD_COLORS[:len(prod_totals)]

    fig_prod = go.Figure(go.Bar(
        x=prod_totals["Revenue"],
        y=prod_totals["Product"],
        orientation="h",
        marker_color=colors_bar,
        text=prod_totals["Revenue"].apply(lambda x: f"{x/1e6:.1f}M"),
        textposition="outside",
        textfont=dict(size=11, color=TEXT_C),
        hovertemplate="<b>%{y}</b><br>Revenue: %{x:,.0f} EGP<extra></extra>",
    ))
    fig_prod.update_layout(
        **bl(height=300, showlegend=False,
             xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickfont=dict(size=10), tickformat=","),
             yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickfont=dict(size=11)))
    )
    st.plotly_chart(fig_prod, use_container_width=True)

with c4:
    st.markdown('<div class="section-title">Payment Methods</div>', unsafe_allow_html=True)

    pay_totals = (
        filtered.groupby("Payment_Method")
        .agg(Revenue=("Total_Sales","sum"), Orders=("Order_ID","count"))
        .reset_index().sort_values("Revenue", ascending=False)
    )
    fig_pay = go.Figure(go.Bar(
        x=pay_totals["Revenue"],
        y=pay_totals["Payment_Method"],
        orientation="h",
        marker_color=PAY_COLORS[:len(pay_totals)],
        text=pay_totals["Revenue"].apply(lambda x: f"{x/1e6:.2f}M"),
        textposition="outside",
        textfont=dict(size=11, color=TEXT_C),
        hovertemplate="<b>%{y}</b><br>Revenue: %{x:,.0f} EGP<br>Orders: "
                      + pay_totals["Orders"].astype(str) + "<extra></extra>",
    ))
    fig_pay.update_layout(
        **bl(height=300, showlegend=False,
             xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickformat=",", tickfont=dict(size=10)),
             yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickfont=dict(size=11)))
    )
    st.plotly_chart(fig_pay, use_container_width=True)

# ─── Row 3: Monthly Category Stacked + City Analysis ─────────────────────────
c5, c6 = st.columns([3, 2])

with c5:
    st.markdown('<div class="section-title">Monthly Breakdown by Category</div>', unsafe_allow_html=True)

    monthly_cat = (
        filtered.groupby(["Month", "Category"])["Total_Sales"]
        .sum().reset_index().sort_values("Month")
    )
    fig_stack = go.Figure()
    for cat in all_cats:
        sub = monthly_cat[monthly_cat["Category"] == cat]
        fig_stack.add_trace(go.Bar(
            x=sub["Month"], y=sub["Total_Sales"],
            name=cat,
            marker_color=CAT_COLORS.get(cat, "#888"),
            hovertemplate=f"<b>{cat}</b><br>%{{y:,.0f}} EGP<extra></extra>",
        ))
    fig_stack.update_layout(
        **bl(height=300, barmode="stack",
             yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickformat=",", tickfont=dict(size=11)),
             xaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickfont=dict(size=10), tickangle=-30),
             legend=dict(bgcolor=BG, font=dict(size=10),
                         orientation="h", y=-0.22))
    )
    st.plotly_chart(fig_stack, use_container_width=True)

with c6:
    st.markdown('<div class="section-title">Revenue by City</div>', unsafe_allow_html=True)

    city_totals = (
        filtered.groupby("City")["Total_Sales"]
        .sum().reset_index().sort_values("Total_Sales", ascending=False)
    )
    fig_city = go.Figure(go.Pie(
        labels=city_totals["City"],
        values=city_totals["Total_Sales"],
        marker_colors=CITY_COLORS[:len(city_totals)],
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} EGP (%{percent})<extra></extra>",
    ))
    fig_city.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="IBM Plex Sans", color=TEXT_C),
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(bgcolor=BG, font=dict(size=10), orientation="v", x=1.02)
    )
    st.plotly_chart(fig_city, use_container_width=True)

# ─── Row 4: Discount Impact + Returns Analysis ────────────────────────────────
c7, c8 = st.columns([1, 1])

with c7:
    st.markdown('<div class="section-title">Discount vs Revenue Impact</div>', unsafe_allow_html=True)

    disc_groups = filtered.copy()
    disc_groups["Discount_Band"] = pd.cut(
        disc_groups["Discount"],
        bins=[-0.01, 0, 0.05, 0.1, 0.15, 0.2, 1.0],
        labels=["0%","1-5%","6-10%","11-15%","16-20%","20%+"]
    )
    disc_agg = (
        disc_groups.groupby("Discount_Band", observed=True)
        .agg(Revenue=("Total_Sales","sum"), Orders=("Order_ID","count"))
        .reset_index()
    )
    fig_disc = go.Figure()
    fig_disc.add_trace(go.Bar(
        x=disc_agg["Discount_Band"].astype(str),
        y=disc_agg["Revenue"],
        name="Revenue",
        marker_color=ACCENT,
        hovertemplate="Discount: <b>%{x}</b><br>Revenue: %{y:,.0f} EGP<extra></extra>",
    ))
    fig_disc.add_trace(go.Scatter(
        x=disc_agg["Discount_Band"].astype(str),
        y=disc_agg["Orders"],
        name="Orders", yaxis="y2",
        line=dict(color="#ffc145", width=2),
        mode="lines+markers",
        marker=dict(size=7, color="#ffc145"),
        hovertemplate="Discount: <b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
    ))
    fig_disc.update_layout(
        **bl(height=280,
             yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickformat=",", tickfont=dict(size=11),
                        title=dict(text="Revenue", font=dict(size=11, color=TEXT_C))),
             yaxis2=dict(overlaying="y", side="right", showgrid=False,
                         tickfont=dict(size=11), zeroline=False,
                         title=dict(text="Orders", font=dict(size=11, color=TEXT_C))),
             legend=dict(bgcolor=BG, font=dict(size=10), orientation="h",
                         x=0, y=1.12))
    )
    st.plotly_chart(fig_disc, use_container_width=True)

with c8:
    st.markdown('<div class="section-title">Returns by Category</div>', unsafe_allow_html=True)

    returns_cat = (
        filtered.groupby("Category")
        .agg(Total=("Order_ID","count"), Returned=("Returned","sum"))
        .reset_index()
    )
    returns_cat["Return_Rate"] = returns_cat["Returned"] / returns_cat["Total"] * 100

    fig_ret = go.Figure()
    fig_ret.add_trace(go.Bar(
        x=returns_cat["Category"],
        y=returns_cat["Total"],
        name="Total Orders",
        marker_color="rgba(0,229,255,0.3)",
        hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
    ))
    fig_ret.add_trace(go.Bar(
        x=returns_cat["Category"],
        y=returns_cat["Returned"],
        name="Returned",
        marker_color="#ff4d8d",
        hovertemplate="<b>%{x}</b><br>Returned: %{y:,}<extra></extra>",
    ))
    fig_ret.update_layout(
        **bl(height=280, barmode="overlay",
             yaxis=dict(gridcolor=GRID_C, zerolinecolor=GRID_C,
                        tickfont=dict(size=11)),
             legend=dict(bgcolor=BG, font=dict(size=10),
                         orientation="h", x=0, y=1.12))
    )
    st.plotly_chart(fig_ret, use_container_width=True)

# ─── Row 5: Heatmap + Top 10 Orders ──────────────────────────────────────────
c9, c10 = st.columns([3, 2])

with c9:
    st.markdown('<div class="section-title">Sales Heatmap — Day of Week x Month</div>', unsafe_allow_html=True)

    hmap = (
        filtered.groupby(["DayOfWeek", "Month"])["Total_Sales"]
        .sum().reset_index()
    )
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = hmap.pivot(index="DayOfWeek", columns="Month", values="Total_Sales").fillna(0)
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])

    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0d1117"], [0.4, "#00607a"], [1, "#00e5ff"]],
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z:,.0f} EGP<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(color=TEXT_C, size=10),
                      bgcolor=BG, outlinecolor=GRID_C)
    ))
    fig_heat.update_layout(
        **bl(height=290,
             xaxis=dict(gridcolor=GRID_C, tickfont=dict(size=9),
                        tickangle=-40, zerolinecolor=GRID_C),
             yaxis=dict(gridcolor=GRID_C, tickfont=dict(size=10),
                        zerolinecolor=GRID_C))
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with c10:
    st.markdown('<div class="section-title">Top 10 Orders</div>', unsafe_allow_html=True)

    top10 = (
        filtered.nlargest(10, "Total_Sales")
        [["Order_ID","Product","Category","Total_Sales","Quantity","City","Payment_Method"]]
        .copy()
    )
    top10["Total_Sales"] = top10["Total_Sales"].apply(lambda x: f"{x:,.0f} EGP")
    top10 = top10.rename(columns={
        "Order_ID":      "Order",
        "Product":       "Product",
        "Category":      "Cat",
        "Total_Sales":   "Revenue",
        "Quantity":      "Qty",
        "City":          "City",
        "Payment_Method":"Payment",
    }).reset_index(drop=True)
    top10.index += 1

    st.dataframe(top10, use_container_width=True, height=290)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#252d45;font-size:0.73rem;'
    'font-family:IBM Plex Mono,monospace;">'
    'E-Commerce Sales Dashboard · Egypt 2023 · Built with Streamlit + Plotly'
    '</div>',
    unsafe_allow_html=True
)