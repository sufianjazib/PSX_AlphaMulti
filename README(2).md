# PSX AI Research Analyst — MVP

This version has **three simple features**:

1. **AlphaScore™** — 0–100 fundamental research score.
2. **Multibagger Radar™** — 0–100 screen for companies showing a combination of growth, quality, valuation, financial strength, catalysts and smaller market-cap opportunity.
3. **AI Stock Research** — Gemini explains the supplied data and the two scores.

## Project files

```text
psx_research_app/
├── app.py
├── stocks.csv
├── requirements.txt
└── README.md
```

## 1. AlphaScore™

| Factor | Maximum |
|---|---:|
| Profit / EPS Growth | 25 |
| Business Quality / ROE | 20 |
| Financial Strength | 20 |
| Valuation | 20 |
| Dividend + Catalyst | 15 |
| **Total** | **100** |

## 2. Multibagger Radar™

The MVP score is based on:

| Factor | Maximum |
|---|---:|
| Earnings + Sales Growth | 25 |
| Business Quality / ROE | 15 |
| Valuation | 15 |
| Financial Strength | 10 |
| Catalysts | 10 |
| Market-cap opportunity | 10 |
| AlphaScore contribution | 15 |
| **Total** | **100** |

### Multibagger ratings

- 80–100 = High Potential
- 70–79 = Promising
- 60–69 = Watchlist
- 50–59 = Speculative
- Below 50 = Low Potential

**Important:** Multibagger Radar is a screening/ranking system. It does not predict or guarantee that a stock will become a 2x, 5x or 10x investment.

## 3. AI Research

The AI receives the supplied company data, AlphaScore and Multibagger Radar score.

It produces:

- Executive View
- AlphaScore Analysis
- Multibagger Potential
- Growth
- Business Quality
- Financial Strength
- Valuation
- Catalysts
- Key Risks
- What Investors Should Monitor
- Final Research View

The AI is instructed not to invent missing data or claim that a company will become a multibagger.

## Run locally

### Install packages

```bash
pip install -r requirements.txt
```

### Set Gemini API key

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

Optional model:

```powershell
$env:GEMINI_MODEL="gemini-3.8-flash"
```

### Start application

```bash
streamlit run app.py
```

## CSV columns

```text
symbol
company
sector
eps_growth
roe
debt_ratio
pe
dividend_yield
catalyst_score
sales_growth
market_cap_billion
```

### Important

The included `stocks.csv` contains **demonstration values only**.

Do not treat those values as current PSX financial information.

For a commercial product, replace the demo CSV with properly sourced/licensed financial and market data.

## Recommended commercial strategy

Keep the product small for now:

```text
PSX Stock
    ↓
AlphaScore™
    +
Multibagger Radar™
    ↓
AI Research Report
```

Do not add portfolio management, WhatsApp, backtesting, complex AI agents, etc. until users actually find this MVP valuable.

## Commercial/legal note

Before charging customers:

- Use properly licensed data.
- Verify financial data accuracy and update frequency.
- Review Pakistani securities/research/advisory requirements with qualified legal/compliance professionals.
- Avoid promises of returns.
- Keep the scoring methodology on a protected backend once the application becomes multi-user.
- Consider trademark clearance/registration for product names such as AlphaScore™ and Multibagger Radar™ before making them core commercial brands.

## Security

Never put the Gemini API key directly inside `app.py`.

Use:

```text
GEMINI_API_KEY
```

as an environment variable.

For a real multi-user deployment, the AlphaScore and Multibagger calculations should eventually run on a protected server/backend rather than being exposed in the browser.

## Disclaimer

This MVP is a research/educational tool. AlphaScore™ and Multibagger Radar™ are screening methodologies and do not guarantee investment performance. Financial information should be independently verified. Before commercial launch, obtain appropriate legal/compliance advice in Pakistan.
