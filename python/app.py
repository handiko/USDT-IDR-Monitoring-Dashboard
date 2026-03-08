import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- 1. SETUP ---
st.set_page_config(
    page_title="Monitoring Dashboard: USDT/IDR Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #080d14;
    color: #c9d1d9;
}
.stApp {
    background: linear-gradient(160deg, #080d14 0%, #0b1220 60%, #080d14 100%);
}

/* ── Header ── */
.terminal-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 0 6px 0;
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 20px;
}
.terminal-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    margin: 0;
    background: linear-gradient(90deg, #f0c040, #e0a020);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.terminal-badge {
    background: #0d2137;
    border: 1px solid #1e4a7a;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 0.68rem;
    font-weight: 600;
    color: #4da3ff;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.terminal-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px #22c55e;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}

/* ── Metric Cards ── */
div[data-testid="metric-container"] {
    background: #0b1828;
    border: 1px solid #1a3050;
    border-radius: 6px;
    padding: 14px 16px !important;
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #f0c040, #4da3ff);
}
div[data-testid="metric-container"] label {
    font-size: 0.65rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a7fa8 !important;
    font-weight: 600;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 700;
    color: #e8f0fe !important;
    letter-spacing: 0.02em;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.72rem !important;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4a7fa8;
    font-weight: 600;
    border-left: 2px solid #f0c040;
    padding-left: 8px;
    margin-bottom: 10px;
}

/* ── Info / Impact card ── */
.impact-card {
    background: #0b1828;
    border: 1px solid #1a3050;
    border-radius: 6px;
    padding: 16px;
}
.impact-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #111e2e;
    font-size: 0.78rem;
}
.impact-row:last-child { border-bottom: none; }
.impact-key { color: #4a7fa8; letter-spacing: 0.06em; }
.impact-val { color: #e8f0fe; font-weight: 600; }
.impact-val.green { color: #22c55e; }
.impact-val.amber { color: #f0c040; }
.impact-val.red   { color: #f87171; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #090f1a !important;
    border-right: 1px solid #1a3050 !important;
}
[data-testid="stSidebar"] .css-1d391kg { background: transparent; }
[data-testid="stSidebar"] label {
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4a7fa8 !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select {
    background: #0d1e30 !important;
    border: 1px solid #1a3050 !important;
    color: #e8f0fe !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Divider ── */
hr { border-color: #1a3050 !important; }

/* ── Plotly chart containers ── */
.stPlotlyChart {
    border: 1px solid #1a3050;
    border-radius: 6px;
    overflow: hidden;
}

/* ── Error / info ── */
div[data-testid="stAlert"] {
    background: #0b1828 !important;
    border: 1px solid #1a3050 !important;
    border-radius: 6px !important;
    font-size: 0.76rem !important;
    color: #4a7fa8 !important;
}

/* ── Radio buttons ── */
div[data-testid="stRadio"] > label > div { color: #c9d1d9; }
div[data-testid="stRadio"] [data-baseweb="radio"] span { border-color: #4da3ff !important; }

/* ── Timestamp ── */
.timestamp {
    font-size: 0.62rem;
    color: #2a4a6a;
    letter-spacing: 0.08em;
    text-align: right;
    margin-top: 4px;
}

/* ── Order book table ── */
.ob-table { width: 100%; border-collapse: collapse; font-size: 0.74rem; }
.ob-table th {
    color: #4a7fa8;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 8px;
    border-bottom: 1px solid #1a3050;
    text-align: right;
}
.ob-table th:first-child { text-align: left; }
.ob-table td {
    padding: 5px 8px;
    text-align: right;
    border-bottom: 1px solid #0d1a28;
    font-variant-numeric: tabular-nums;
}
.ob-table td:first-child { text-align: left; }
.ob-bid { color: #22c55e; }
.ob-ask { color: #f87171; }
.ob-size { color: #8ba8c4; }
</style>
""", unsafe_allow_html=True)

# ── Exchange Init ────────────────────────────────────────────────────────────
idx = ccxt.indodax({'enableRateLimit': True})
tkc = ccxt.tokocrypto({'enableRateLimit': True})
SYMBOL = 'USDT/IDR'

if 'spread_history' not in st.session_state:
    st.session_state.spread_history = []

# ── Chart theme ─────────────────────────────────────────────────────────────
CHART_BG  = '#0b1828'
GRID_CLR  = '#1a3050'
FONT_CLR  = '#4a7fa8'
FONT_FAM  = 'JetBrains Mono, monospace'

def chart_layout(height=280, title=""):
    return dict(
        height=height,
        margin=dict(l=0, r=0, t=28 if title else 10, b=0),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_FAM, color=FONT_CLR, size=10),
        title=dict(text=title, font=dict(size=11, color='#6a9fc0'), x=0.01) if title else None,
        xaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(size=9)),
        yaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(size=9)),
    )


# --- 2. DATA ENGINES ---
def fetch_data():
    ob    = idx.fetch_order_book(SYMBOL, limit=50)
    ohlcv = idx.fetch_ohlcv(SYMBOL, timeframe='1m', limit=60)
    return ob, ohlcv


def get_tkc_price():
    try:
        return tkc.fetch_ticker(SYMBOL)['last']
    except:
        return None


def simulate_impact(side, amount_idr, ob):
    """Walk the order book to estimate slippage for a given IDR trade size."""
    levels = ob['asks'] if side == 'Buy' else ob['bids']
    remaining = amount_idr
    total_usdt = 0.0
    worst_px   = None
    for px, qty in levels:
        value = px * qty
        if remaining <= 0:
            break
        fill       = min(remaining, value)
        total_usdt += fill / px
        remaining  -= fill
        worst_px    = px
    if total_usdt == 0:
        return None, None, None
    avg_px    = (amount_idr - max(remaining, 0)) / total_usdt if total_usdt else 0
    ref_px    = ob['asks'][0][0] if side == 'Buy' else ob['bids'][0][0]
    slippage  = abs(avg_px - ref_px) / ref_px * 100
    filled_idr = amount_idr - max(remaining, 0)
    return avg_px, slippage, filled_idr


# --- 3. UI ---------------------------------------------------------------

# Header
st.markdown("""
<div class="terminal-header">
    <div class="terminal-dot"></div>
    <h1>Monitoring Dashboard — USDT/IDR</h1>
    <span class="terminal-badge">Indodax · Live</span>
    <span class="terminal-badge">Tokocrypto · Live</span>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<p class="section-label">⚙ Execution Controls</p>', unsafe_allow_html=True)
    sim_side   = st.radio("Simulate Side", ["Buy", "Sell"], horizontal=True)
    sim_amount = st.number_input("Trade Amount (IDR)", value=100_000_000, step=10_000_000, format="%d")
    st.markdown("---")
    st.markdown('<p class="section-label">ℹ About</p>', unsafe_allow_html=True)
    st.caption("Real-time USDT/IDR market terminal.\nData: Indodax · Tokocrypto.\nRefresh: ~1 s")


@st.fragment(run_every=1.0)
def dashboard_body():
    try:
        ob, ohlcv = fetch_data()
        tkc_price = get_tkc_price()
        now_str   = datetime.now().strftime('%Y-%m-%d  %H:%M:%S')

        # ── Derived metrics ────────────────────────────────────────────────
        best_bid   = ob['bids'][0][0]
        best_ask   = ob['asks'][0][0]
        mid_price  = (best_bid + best_ask) / 2
        spread_abs = best_ask - best_bid
        spread_pct = (spread_abs / best_bid) * 100

        # Spread history
        st.session_state.spread_history.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'spread': spread_pct
        })
        if len(st.session_state.spread_history) > 120:
            st.session_state.spread_history.pop(0)

        # ── A. Top metrics ─────────────────────────────────────────────────
        cols = st.columns(5)
        cols[0].metric("Best Bid",    f"Rp {best_bid:,.0f}")
        cols[1].metric("Best Ask",    f"Rp {best_ask:,.0f}")
        cols[2].metric("Mid Price",   f"Rp {mid_price:,.0f}")
        cols[3].metric("Spread",      f"{spread_pct:.4f}%",  f"Rp {spread_abs:,.0f}")
        if tkc_price:
            diff = best_ask - tkc_price
            cols[4].metric(
                "vs Tokocrypto",
                f"Rp {tkc_price:,.0f}",
                f"Rp {diff:,.0f}",
                delta_color="inverse"
            )
        else:
            cols[4].metric("vs Tokocrypto", "—")

        st.markdown(f'<p class="timestamp">⏱ Last sync: {now_str} WIB</p>', unsafe_allow_html=True)
        st.markdown("---")

        # ── B. Charts row ─────────────────────────────────────────────────
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<p class="section-label">📈 Price Trend — 1m OHLCV</p>', unsafe_allow_html=True)
            df_hist = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
            df_hist['t'] = pd.to_datetime(df_hist['t'], unit='ms')

            fig_p = go.Figure()
            fig_p.add_trace(go.Candlestick(
                x=df_hist['t'],
                open=df_hist['o'], high=df_hist['h'],
                low=df_hist['l'],  close=df_hist['c'],
                increasing_line_color='#22c55e',
                decreasing_line_color='#f87171',
                increasing_fillcolor='#166534',
                decreasing_fillcolor='#7f1d1d',
                name='Price',
            ))
            fig_p.update_layout(**chart_layout(height=290))
            fig_p.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_p, use_container_width=True)

        with c2:
            st.markdown('<p class="section-label">📊 Spread History (%)</p>', unsafe_allow_html=True)
            df_spread = pd.DataFrame(st.session_state.spread_history)
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(
                x=df_spread['time'], y=df_spread['spread'],
                mode='lines',
                line=dict(color='#f0c040', width=1.5),
                fill='tozeroy',
                fillcolor='rgba(240,192,64,0.07)',
                name='Spread %',
            ))
            fig_s.update_layout(**chart_layout(height=290))
            st.plotly_chart(fig_s, use_container_width=True)

        # ── C. Depth + Order Book + Impact ────────────────────────────────
        st.markdown("---")
        d1, d2, d3 = st.columns([3, 2, 2])

        with d1:
            st.markdown('<p class="section-label">🔍 Market Depth</p>', unsafe_allow_html=True)
            b_df = pd.DataFrame(ob['bids'][:30], columns=['p', 'q']).assign(cum=lambda x: x['q'].cumsum())
            a_df = pd.DataFrame(ob['asks'][:30], columns=['p', 'q']).assign(cum=lambda x: x['q'].cumsum())

            fig_d = go.Figure()
            fig_d.add_trace(go.Scatter(
                x=b_df['p'], y=b_df['cum'],
                fill='tozeroy', name='Bids',
                line=dict(color='#22c55e', width=1.5),
                fillcolor='rgba(34,197,94,0.12)',
            ))
            fig_d.add_trace(go.Scatter(
                x=a_df['p'], y=a_df['cum'],
                fill='tozeroy', name='Asks',
                line=dict(color='#f87171', width=1.5),
                fillcolor='rgba(248,113,113,0.12)',
            ))
            fig_d.add_vline(x=mid_price, line_dash="dot", line_color="#f0c040", line_width=1)
            fig_d.update_layout(**chart_layout(height=280))
            st.plotly_chart(fig_d, use_container_width=True)

        with d2:
            st.markdown('<p class="section-label">📋 Order Book (Top 8)</p>', unsafe_allow_html=True)
            asks_top = ob['asks'][:8][::-1]
            bids_top = ob['bids'][:8]
            rows = []
            for px, qty in asks_top:
                rows.append(f'<tr><td class="ob-ask">{px:,.0f}</td><td class="ob-size">{qty:.4f}</td><td class="ob-size">{px*qty:,.0f}</td></tr>')
            rows.append(f'<tr style="background:#0d1e30"><td colspan="3" style="text-align:center;color:#f0c040;padding:5px;font-size:0.65rem;letter-spacing:0.1em">── SPREAD {spread_abs:,.0f} ──</td></tr>')
            for px, qty in bids_top:
                rows.append(f'<tr><td class="ob-bid">{px:,.0f}</td><td class="ob-size">{qty:.4f}</td><td class="ob-size">{px*qty:,.0f}</td></tr>')

            st.markdown(f"""
            <div style="background:#0b1828;border:1px solid #1a3050;border-radius:6px;padding:10px;max-height:300px;overflow-y:auto">
            <table class="ob-table">
              <thead><tr><th>Price (IDR)</th><th>Size (USDT)</th><th>Value (IDR)</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
            </div>
            """, unsafe_allow_html=True)

        with d3:
            st.markdown('<p class="section-label">⚡ Impact Calculator</p>', unsafe_allow_html=True)
            avg_px, slippage, filled_idr = simulate_impact(sim_side, sim_amount, ob)

            if avg_px:
                usdt_recv  = filled_idr / avg_px
                slip_class = "green" if slippage < 0.05 else ("amber" if slippage < 0.2 else "red")
                slip_emoji = "🟢" if slippage < 0.05 else ("🟡" if slippage < 0.2 else "🔴")

                st.markdown(f"""
                <div class="impact-card">
                  <div class="impact-row">
                    <span class="impact-key">SIDE</span>
                    <span class="impact-val {'green' if sim_side=='Buy' else 'red'}">{sim_side.upper()}</span>
                  </div>
                  <div class="impact-row">
                    <span class="impact-key">NOTIONAL</span>
                    <span class="impact-val">Rp {sim_amount:,.0f}</span>
                  </div>
                  <div class="impact-row">
                    <span class="impact-key">AVG FILL</span>
                    <span class="impact-val">Rp {avg_px:,.2f}</span>
                  </div>
                  <div class="impact-row">
                    <span class="impact-key">USDT {'RECV' if sim_side=='Buy' else 'SOLD'}</span>
                    <span class="impact-val">{usdt_recv:,.4f} USDT</span>
                  </div>
                  <div class="impact-row">
                    <span class="impact-key">SLIPPAGE</span>
                    <span class="impact-val {slip_class}">{slip_emoji} {slippage:.4f}%</span>
                  </div>
                  <div class="impact-row">
                    <span class="impact-key">FILLED</span>
                    <span class="impact-val">Rp {filled_idr:,.0f}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="impact-card"><p style="color:#4a7fa8;font-size:0.75rem">Insufficient depth for simulation.</p></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠ Stream error — retrying…  ({e})")


dashboard_body()
