# Monitoring Dashboard: USDT/IDR Terminal — Technical Deep Dive

A high-fidelity monitoring terminal for the **USDT/IDR** pair, built for liquidity analysis and execution simulation across Indonesian exchanges. This project focuses on minimizing latency and maximizing the visibility of order book depth through a "Terminal-as-a-Service" UI.

---

## Architectural Overview

The application follows a **Reactive Polling Architecture**. Unlike traditional Streamlit apps that rerun the entire script on every interaction, this terminal utilizes **Streamlit Fragments** to isolate the data-heavy monitoring loop from the static UI components.

### 1. The Data Engine (`ccxt` Integration)
The core of the system leverages the **CCXT (CryptoCurrency eXchange Trading Library)** to interface with Indodax and Tokocrypto.
* **Rate Limiting**: `enableRateLimit: True` is enforced to prevent IP bans during the 1-second polling cycles.
* **Data Aggregation**: The `fetch_data()` function concurrently pulls the L2 Order Book (top 50 levels) and 1-minute OHLCV (Open, High, Low, Close, Volume) data from Indodax.
* **Cross-Exchange Comparison**: A secondary engine fetches the last traded price from Tokocrypto to calculate real-time arbitrage spreads.

### 2. Real-Time State Management
Streamlit’s `session_state` is utilized to provide a persistent "memory" for transient data:
* **`spread_history`**: An in-memory buffer that stores a rolling window of the last 120 data points of the bid/ask spread percentage.
* **Buffer Pruning**: To prevent memory leaks, the system automatically pops the oldest record once the 120-item limit is reached, ensuring the "Spread History" chart remains performant over long sessions.

---

## Inner Working Mechanisms

### Liquidity Walking (The Impact Calculator)
The `simulate_impact` function is a custom-built engine that mimics how a **Market Order** would behave in a live environment. Instead of just looking at the "Best Ask," it "walks" the order book to find the true execution price:

1.  **Level Iteration**: It iterates through the `asks` (for Buys) or `bids` (for Sells).
2.  **Cumulative Fill**: For each level, it calculates the available liquidity ($Price \times Quantity$).
3.  **Partial Fills**: If the trade amount is larger than a single level, it consumes that level and moves to the next, tracking the `worst_px` encountered.
4.  **Slippage Calculation**: It computes the **Volume Weighted Average Price (VWAP)** and compares it to the **Best Bid/Ask** to determine the percentage of slippage.

### Fragmented Rendering
To achieve the "Live" feel, the `dashboard_body()` is wrapped in the `@st.fragment(run_every=1.0)` decorator. 
* **Logic**: This tells Streamlit to only rerun the code inside this function every 1 second.
* **Benefit**: The sidebar inputs and the custom CSS header remain static. This significantly reduces computational overhead and prevents the "flicker" associated with full-page refreshes.

### UI & UX Engineering
The interface is transformed via **Global CSS Injection** to mimic a professional financial terminal (e.g., Bloomberg or Refinitiv):
* **Typography**: Uses `JetBrains Mono` for a "code-centric" data feel and `Syne` for high-impact headers.
* **Color Theory**: Adheres to a strict dark-mode palette:
    * **Background**: `#080d14` (Deep Navy)
    * **Success/Bids**: `#22c55e` (Emerald)
    * **Danger/Asks**: `#f87171` (Coral Red)
* **Animations**: Includes a CSS-based pulse animation on the "Live" status dot to indicate active data streaming.

---

## Data Visualization Logic

| Component | Logic Applied | Visualization Tool |
| :--- | :--- | :--- |
| **Price Trend** | Candlestick representation of 1m OHLCV data with custom fill colors. | Plotly (Candlestick) |
| **Market Depth** | Cumulative sum of Bid/Ask volume plotted against price levels. | Plotly (Area Chart) |
| **Order Book** | A custom HTML-table-rendered display of the top 8 levels with a central "Spread Row". | Markdown/HTML |
| **Spread History** | Time-series line chart tracking the liquidity gap over the session. | Plotly (Scatter/Line) |

---

## Setup and Development

### Prerequisites
* Python 3.9+
* Streamlit 1.37+ (for Fragment support)
* CCXT
* Plotly
* Pandas

### Installation
1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/your-username/ajaib-ops-terminal.git](https://github.com/your-username/ajaib-ops-terminal.git)
    cd ajaib-ops-terminal
    ```
2.  **Install dependencies**:
    ```bash
    pip install streamlit ccxt pandas plotly
    ```
3.  **Launch the terminal**:
    ```bash
    streamlit run app_dashboard.py
    ```

## Disclaimer
This terminal is a monitoring and simulation tool. The slippage calculated is a theoretical "best-case" scenario and does not account for exchange fees, network latency, or "phantom" liquidity often found in high-frequency trading environments.
