import os
import pandas as pd
import streamlit as st
from google import genai

# ============================================================
# PSX AI RESEARCH APPLICATION - MVP
# Features:
#   1. AlphaScore™ (0-100)
#   2. Multibagger Radar™
#   3. AI Stock Research Report
# ============================================================

st.set_page_config(
    page_title="PSX AI Research Analyst",
    page_icon="📈",
    layout="wide",
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
DATA_FILE = "stocks.csv"

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 0;
    }
    .sub-title {
        color: #666;
        margin-top: 0;
    }
    .score-box {
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .score-number {
        font-size: 48px;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">📈 PSX AI Research Analyst</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">AlphaScore™ + Multibagger Radar™ + AI Stock Research</div>',
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


try:
    df = load_data()
except FileNotFoundError:
    st.error("stocks.csv was not found. Put it in the same folder as app.py.")
    st.stop()

required_columns = [
    "symbol",
    "company",
    "sector",
    "eps_growth",
    "roe",
    "debt_ratio",
    "pe",
    "dividend_yield",
    "catalyst_score",
    "sales_growth",
    "market_cap_billion",
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error("Missing columns in stocks.csv: " + ", ".join(missing))
    st.stop()


# ============================================================
# ALPHASCORE™
# ============================================================
def score_eps_growth(value):
    if pd.isna(value):
        return 0
    if value > 30:
        return 25
    if value >= 20:
        return 20
    if value >= 10:
        return 15
    if value >= 5:
        return 10
    if value >= 0:
        return 5
    return 0


def score_roe(value):
    if pd.isna(value):
        return 0
    if value > 25:
        return 20
    if value >= 20:
        return 17
    if value >= 15:
        return 14
    if value >= 10:
        return 10
    if value >= 5:
        return 5
    return 0


def score_debt(value):
    # Net Debt / EBITDA
    if pd.isna(value):
        return 0
    if value < 0:
        return 20
    if value <= 1:
        return 18
    if value <= 2:
        return 15
    if value <= 3:
        return 10
    if value <= 4:
        return 5
    return 0


def score_pe(value):
    if pd.isna(value) or value <= 0:
        return 0
    if value < 5:
        return 20
    if value <= 7:
        return 17
    if value <= 10:
        return 14
    if value <= 15:
        return 10
    if value <= 20:
        return 5
    return 0


def score_dividend_and_catalyst(dividend_yield, catalyst_score):
    if pd.isna(dividend_yield):
        dividend_points = 0
    elif dividend_yield >= 10:
        dividend_points = 10
    elif dividend_yield >= 7:
        dividend_points = 8
    elif dividend_yield >= 5:
        dividend_points = 6
    elif dividend_yield >= 3:
        dividend_points = 4
    elif dividend_yield > 0:
        dividend_points = 2
    else:
        dividend_points = 0

    catalyst_points = (
        0
        if pd.isna(catalyst_score)
        else max(0, min(5, float(catalyst_score)))
    )

    return dividend_points + catalyst_points


def calculate_alpha_score(row):
    growth = score_eps_growth(row["eps_growth"])
    quality = score_roe(row["roe"])
    financial = score_debt(row["debt_ratio"])
    valuation = score_pe(row["pe"])
    dividend_catalyst = score_dividend_and_catalyst(
        row["dividend_yield"],
        row["catalyst_score"],
    )

    total = round(
        growth + quality + financial + valuation + dividend_catalyst
    )

    return {
        "growth": growth,
        "quality": quality,
        "financial": financial,
        "valuation": valuation,
        "dividend_catalyst": dividend_catalyst,
        "total": max(0, min(100, total)),
    }


def get_rating(score):
    if score >= 90:
        return "Exceptional", "🟢"
    if score >= 80:
        return "Strong", "🟢"
    if score >= 70:
        return "Attractive", "🟢"
    if score >= 60:
        return "Watch", "🟡"
    if score >= 50:
        return "Weak", "🟠"
    return "Avoid", "🔴"


# ============================================================
# MULTIBAGGER RADAR™
# ============================================================
def calculate_multibagger_score(row, alpha_score):
    """
    Simple MVP multibagger score: 0-100.

    This is deliberately NOT a prediction of a future share price.
    It identifies companies with a combination of:
      - earnings growth
      - sales growth
      - reasonable valuation
      - ROE/business quality
      - manageable debt
      - catalysts
      - smaller market-cap opportunity

    Maximum:
      Growth:       25
      Quality:      15
      Valuation:    15
      Financial:    10
      Catalyst:     10
      Size:          10
      AlphaScore:   15
      Total:       100
    """

    # Growth: EPS growth 0-25
    eps = row["eps_growth"]
    if pd.isna(eps):
        growth_points = 0
    elif eps >= 30:
        growth_points = 25
    elif eps >= 25:
        growth_points = 22
    elif eps >= 20:
        growth_points = 19
    elif eps >= 15:
        growth_points = 15
    elif eps >= 10:
        growth_points = 10
    elif eps >= 5:
        growth_points = 5
    else:
        growth_points = 0

    # Sales growth 0-10 inside growth category
    sales = row["sales_growth"]
    if pd.isna(sales):
        sales_points = 0
    elif sales >= 30:
        sales_points = 10
    elif sales >= 20:
        sales_points = 8
    elif sales >= 10:
        sales_points = 6
    elif sales >= 5:
        sales_points = 3
    else:
        sales_points = 0

    # To keep growth at 25, combine EPS and sales using weighted average
    growth_points = round(
        min(25, growth_points * 0.70 + sales_points * 0.30)
    )

    # Quality 15
    roe = row["roe"]
    if pd.isna(roe):
        quality_points = 0
    elif roe >= 25:
        quality_points = 15
    elif roe >= 20:
        quality_points = 13
    elif roe >= 15:
        quality_points = 10
    elif roe >= 10:
        quality_points = 6
    elif roe >= 5:
        quality_points = 3
    else:
        quality_points = 0

    # Valuation 15
    pe = row["pe"]
    if pd.isna(pe) or pe <= 0:
        valuation_points = 0
    elif pe <= 6:
        valuation_points = 15
    elif pe <= 8:
        valuation_points = 13
    elif pe <= 10:
        valuation_points = 11
    elif pe <= 15:
        valuation_points = 7
    elif pe <= 20:
        valuation_points = 3
    else:
        valuation_points = 0

    # Financial strength 10
    debt = row["debt_ratio"]
    if pd.isna(debt):
        financial_points = 0
    elif debt < 0:
        financial_points = 10
    elif debt <= 1:
        financial_points = 9
    elif debt <= 2:
        financial_points = 7
    elif debt <= 3:
        financial_points = 5
    elif debt <= 4:
        financial_points = 2
    else:
        financial_points = 0

    # Catalyst 10
    catalyst = row["catalyst_score"]
    catalyst_points = (
        0
        if pd.isna(catalyst)
        else max(0, min(10, float(catalyst) * 2))
    )

    # Size 10
    market_cap = row["market_cap_billion"]
    if pd.isna(market_cap):
        size_points = 0
    elif market_cap <= 5:
        size_points = 10
    elif market_cap <= 10:
        size_points = 9
    elif market_cap <= 20:
        size_points = 7
    elif market_cap <= 40:
        size_points = 5
    elif market_cap <= 100:
        size_points = 2
    else:
        size_points = 0

    # AlphaScore contribution 15
    alpha_points = round((alpha_score / 100) * 15)

    total = round(
        growth_points
        + quality_points
        + valuation_points
        + financial_points
        + catalyst_points
        + size_points
        + alpha_points
    )

    return max(0, min(100, total))


def get_multibagger_rating(score):
    if score >= 80:
        return "High Potential", "🟢"
    if score >= 70:
        return "Promising", "🟢"
    if score >= 60:
        return "Watchlist", "🟡"
    if score >= 50:
        return "Speculative", "🟠"
    return "Low Potential", "🔴"


# ============================================================
# STOCK SELECTION
# ============================================================
symbols = sorted(
    df["symbol"].dropna().astype(str).str.upper().unique().tolist()
)

selected_symbol = st.selectbox("Select a PSX stock", symbols)

row = df[
    df["symbol"].astype(str).str.upper() == selected_symbol
].iloc[0]

alpha = calculate_alpha_score(row)
alpha_score = alpha["total"]

alpha_rating, alpha_icon = get_rating(alpha_score)

multibagger_score = calculate_multibagger_score(row, alpha_score)
multibagger_rating, multibagger_icon = get_multibagger_rating(
    multibagger_score
)


# ============================================================
# TOP SUMMARY
# ============================================================
st.divider()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("AlphaScore™", f"{alpha_score}/100")

with c2:
    st.metric("Research Rating", f"{alpha_icon} {alpha_rating}")

with c3:
    st.metric("Multibagger Radar™", f"{multibagger_score}/100")

with c4:
    st.metric("Potential", f"{multibagger_icon} {multibagger_rating}")

st.subheader(str(row["company"]))
st.caption(f'{row["symbol"]} • {row["sector"]}')


# ============================================================
# ALPHASCORE BREAKDOWN
# ============================================================
st.subheader("AlphaScore™ Breakdown")

score_table = pd.DataFrame(
    {
        "Factor": [
            "Profit / EPS Growth",
            "Business Quality / ROE",
            "Financial Strength",
            "Valuation",
            "Dividend + Catalyst",
        ],
        "Score": [
            f"{alpha['growth']}/25",
            f"{alpha['quality']}/20",
            f"{alpha['financial']}/20",
            f"{alpha['valuation']}/20",
            f"{alpha['dividend_catalyst']}/15",
        ],
    }
)

st.table(score_table)


# ============================================================
# MULTIBAGGER RADAR
# ============================================================
st.divider()
st.subheader("🚀 Multibagger Radar™")

st.info(
    "Multibagger Radar identifies companies with a combination of growth, "
    "quality, valuation, financial strength, catalysts and smaller size. "
    "It is a screening score — NOT a promise that the stock will become a multibagger."
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Multibagger Score", f"{multibagger_score}/100")
m2.metric("EPS Growth", f"{row['eps_growth']:.1f}%")
m3.metric("Sales Growth", f"{row['sales_growth']:.1f}%")
m4.metric("Market Cap", f"Rs {row['market_cap_billion']:.1f}B")

# Radar explanation
reasons = []

if row["eps_growth"] >= 20:
    reasons.append("Strong earnings growth")
if row["sales_growth"] >= 15:
    reasons.append("Strong sales growth")
if row["roe"] >= 20:
    reasons.append("High ROE")
if row["pe"] <= 10 and row["pe"] > 0:
    reasons.append("Reasonable P/E")
if row["debt_ratio"] <= 2:
    reasons.append("Manageable leverage")
if row["market_cap_billion"] <= 20:
    reasons.append("Smaller market-cap opportunity")
if row["catalyst_score"] >= 4:
    reasons.append("Strong catalyst score")

if reasons:
    st.markdown("**Why it appears on the radar:**")
    for reason in reasons:
        st.write(f"• {reason}")
else:
    st.write("The supplied data does not show enough strong multibagger characteristics.")


# ============================================================
# KEY INPUTS
# ============================================================
st.subheader("Key Financial Inputs")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("EPS Growth", f"{row['eps_growth']:.1f}%")
k2.metric("ROE", f"{row['roe']:.1f}%")
k3.metric("Net Debt / EBITDA", f"{row['debt_ratio']:.1f}x")
k4.metric("P/E", f"{row['pe']:.1f}x")
k5.metric("Dividend Yield", f"{row['dividend_yield']:.1f}%")


# ============================================================
# AI RESEARCH
# ============================================================
st.divider()
st.subheader("🤖 AI Stock Research")

if st.button(
    "Generate AI Research Report",
    type="primary",
    use_container_width=True,
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "GEMINI_API_KEY is not configured. "
            "Set it as an environment variable and restart Streamlit."
        )
        st.stop()

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are the research analyst inside a Pakistan Stock Exchange research application.

Analyze this company using ONLY the supplied data.

Company: {row['company']}
Symbol: {row['symbol']}
Sector: {row['sector']}

FINANCIAL DATA
EPS Growth: {row['eps_growth']}%
Sales Growth: {row['sales_growth']}%
ROE: {row['roe']}%
Net Debt / EBITDA: {row['debt_ratio']}x
P/E: {row['pe']}x
Dividend Yield: {row['dividend_yield']}%
Market Cap: Rs {row['market_cap_billion']} billion
Catalyst Score: {row['catalyst_score']}/5

ALPHASCORE™
Growth: {alpha['growth']}/25
Quality: {alpha['quality']}/20
Financial Strength: {alpha['financial']}/20
Valuation: {alpha['valuation']}/20
Dividend + Catalyst: {alpha['dividend_catalyst']}/15
Total: {alpha_score}/100
Rating: {alpha_rating}

MULTIBAGGER RADAR™
Score: {multibagger_score}/100
Rating: {multibagger_rating}

RULES
1. Use ONLY the supplied data.
2. Do not invent financial results, prices, news, projects, targets or company facts.
3. Do not claim to have live market data.
4. Do not say the company WILL become a multibagger.
5. Explain why it does or does not show multibagger characteristics.
6. Clearly identify risks and missing information.
7. Do not promise investment returns.
8. This is research, not personalized financial advice.

Write:

## Executive View
## AlphaScore Analysis
## Multibagger Potential
## Growth
## Business Quality
## Financial Strength
## Valuation
## Catalysts
## Key Risks
## What Investors Should Monitor
## Final Research View

Keep the report concise and professional.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        if response.text:
            st.markdown(response.text)
        else:
            st.warning("The AI returned an empty response.")

    except Exception as e:
        st.error(f"Gemini API error: {e}")


# ============================================================
# DISCLAIMER
# ============================================================
st.divider()

st.caption(
    "DISCLAIMER: This application is a research and educational MVP. "
    "AlphaScore™ and Multibagger Radar™ are screening methodologies and do "
    "not guarantee investment performance. Verify financial information "
    "independently. Before commercial deployment, use properly licensed "
    "market/financial data and obtain appropriate Pakistani legal/compliance advice."
)
