import streamlit as st
from data_fetcher import fetch_market_news, fetch_price, fetch_multiple_prices
from sentiment_analysis import analyze_headlines, score_text
from visualizer import plot_sentiment_bar, plot_price_trend
from predictor import build_training_set, train_model, predict_for_symbols
from utils import get_logger
import pandas as pd
import numpy as np

logger = get_logger("ui_app")
st.set_page_config(page_title="Stock Market Guide for Beginners", layout="wide")

# Custom CSS for beginner-friendly styling
st.markdown("""
    <style>
    .big-font { font-size: 24px; font-weight: bold; color: #1f77b4; }
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .call-box { background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745; }
    .put-box { background-color: #f8d7da; padding: 15px; border-radius: 8px; border-left: 5px solid #dc3545; }
    .neutral-box { background-color: #e7e7e7; padding: 15px; border-radius: 8px; border-left: 5px solid #6c757d; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Stock Market Guide for Beginners")
st.write("*Learn about Indian stocks with real-time sentiment analysis and AI predictions*")

# Sidebar for navigation
st.sidebar.header("📋 Navigation")
page = st.sidebar.radio("Choose a Section", [
    "🎯 Today's Market Call",
    "📊 Stock Predictions",
    "📰 News Sentiment",
    "💹 Stock Trends"
])

# ============ Page 1: Today's Market Call ============
if page == "🎯 Today's Market Call":
    st.header("🎯 Today's Market Call - Call vs Put Decision")
    
    st.info("""
    💡 **What does this mean for beginners?**
    - **CALL**: Market is expected to go UP ⬆️ - Good time to BUY CALL OPTIONS
    - **PUT**: Market is expected to go DOWN ⬇️ - Better to BUY PUT OPTIONS or WAIT
    - **NEUTRAL**: Market is UNCERTAIN - Be CAUTIOUS with options
    """)
    
    st.write("---")
    
    # Fetch and analyze news
    with st.spinner("🔄 Analyzing latest market news..."):
        news = fetch_market_news()
        combined_headlines = []
        for src, headlines in news.items():
            combined_headlines.extend(headlines)
        
        if combined_headlines:
            sentiments = analyze_headlines(combined_headlines[:100])
            
            # Calculate sentiment statistics
            positive = sum(1 for s in sentiments if s.get("compound", 0) > 0.05)
            negative = sum(1 for s in sentiments if s.get("compound", 0) < -0.05)
            neutral = len(sentiments) - positive - negative
            avg_compound = sum(s.get("compound", 0) for s in sentiments) / len(sentiments) if sentiments else 0
            
            # Determine market call
            if avg_compound > 0.1:
                call_type = "CALL (BUY)"
                call_color = "green"
                call_emoji = "📈"
                recommendation = "Market sentiment is POSITIVE. Consider BUYING CALLS or HOLDING."
            elif avg_compound < -0.1:
                call_type = "PUT (SELL)"
                call_color = "red"
                call_emoji = "📉"
                recommendation = "Market sentiment is NEGATIVE. Consider BUYING PUTS or WAITING."
            else:
                call_type = "NEUTRAL (HOLD)"
                call_emoji = "➡️"
                call_color = "gray"
                recommendation = "Market sentiment is MIXED. Be CAUTIOUS with new positions."
            
            # Display main indices table
            st.markdown("### 📊 Index Calls Today")
            
            indices_data = {
                "Index Name": ["Nifty 50", "Bank Nifty", "Sensex"],
                "Current Call": [call_type, call_type, call_type],
                "Sentiment Score": [f"{avg_compound:.2f}", f"{avg_compound:.2f}", f"{avg_compound:.2f}"],
                "Recommendation": [recommendation, recommendation, recommendation],
                "Data Source": ["NSE (National Stock Exchange)", "NSE", "BSE (Bombay Stock Exchange)"]
            }
            
            indices_df = pd.DataFrame(indices_data)
            
            # Color the Call column
            def color_call(call):
                if "CALL" in call:
                    return "color: green; font-weight: bold;"
                elif "PUT" in call:
                    return "color: red; font-weight: bold;"
                else:
                    return "color: orange; font-weight: bold;"
            
            st.dataframe(
                indices_df.style.applymap(lambda x: color_call(x) if isinstance(x, str) else "", subset=["Current Call"]),
                use_container_width=True,
                height=200
            )
            
            st.write("---")
            
            # ========== NEW: Index Options Section ==========
            st.markdown("### 🎯 OPTIONS TO BUY TODAY")
            st.markdown("**Based on today's market analysis, here are the recommended options:**")
            
            # Create options recommendations based on sentiment
            options_data = []
            
            # Nifty 50 options
            if call_type == "CALL (BUY)":
                options_data.append({
                    "Index": "Nifty 50",
                    "Strategy": "📈 BUY CALL",
                    "Strike Price": "23,600",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Positive sentiment - Market expected to go UP",
                    "Risk Level": "🟢 Low-Medium"
                })
                options_data.append({
                    "Index": "Nifty 50",
                    "Strategy": "📈 BUY CALL",
                    "Strike Price": "23,700",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Target higher - More profit potential",
                    "Risk Level": "🟡 Medium"
                })
            else:
                options_data.append({
                    "Index": "Nifty 50",
                    "Strategy": "📉 BUY PUT",
                    "Strike Price": "23,400",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Negative sentiment - Market expected to go DOWN",
                    "Risk Level": "🟢 Low-Medium"
                })
                options_data.append({
                    "Index": "Nifty 50",
                    "Strategy": "📉 BUY PUT",
                    "Strike Price": "23,300",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Target lower - More profit potential",
                    "Risk Level": "🟡 Medium"
                })
            
            # Bank Nifty options
            if call_type == "CALL (BUY)":
                options_data.append({
                    "Index": "Bank Nifty",
                    "Strategy": "📈 BUY CALL",
                    "Strike Price": "60,000",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Positive market - Finance sector strong",
                    "Risk Level": "🟢 Low-Medium"
                })
                options_data.append({
                    "Index": "Bank Nifty",
                    "Strategy": "📈 BUY CALL",
                    "Strike Price": "60,500",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Aggressive strategy - Higher returns",
                    "Risk Level": "🟡 Medium"
                })
            else:
                options_data.append({
                    "Index": "Bank Nifty",
                    "Strategy": "📉 BUY PUT",
                    "Strike Price": "59,500",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Negative market - Protect from losses",
                    "Risk Level": "🟢 Low-Medium"
                })
                options_data.append({
                    "Index": "Bank Nifty",
                    "Strategy": "📉 BUY PUT",
                    "Strike Price": "59,000",
                    "Expiry Date": "27 Jan 2026",
                    "Reason": "Target lower - More profit potential",
                    "Risk Level": "🟡 Medium"
                })
            
            options_df = pd.DataFrame(options_data)
            
            # Display options in colored boxes
            for idx, row in options_df.iterrows():
                if "CALL" in row["Strategy"]:
                    st.markdown(f"""
                    <div class="call-box">
                        <b>{row['Index']} - {row['Strategy']}</b><br/>
                        Strike: ₹{row['Strike Price']} | Expiry: {row['Expiry Date']}<br/>
                        <small>📝 {row['Reason']}<br/>
                        Risk: {row['Risk Level']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="put-box">
                        <b>{row['Index']} - {row['Strategy']}</b><br/>
                        Strike: ₹{row['Strike Price']} | Expiry: {row['Expiry Date']}<br/>
                        <small>📝 {row['Reason']}<br/>
                        Risk: {row['Risk Level']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.write("---")
            
            # Sentiment breakdown
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📈 Positive News", positive, f"{(positive/len(sentiments)*100):.1f}%")
            with col2:
                st.metric("📉 Negative News", negative, f"{(negative/len(sentiments)*100):.1f}%")
            with col3:
                st.metric("➡️ Neutral News", neutral, f"{(neutral/len(sentiments)*100):.1f}%")
            with col4:
                st.metric("💯 Sentiment Score", f"{avg_compound:.3f}", "Range: -1 to +1")
            
            st.write("---")
            
            # Top headlines
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Top Positive News (BUY Indicators)")
                positive_headlines = sorted(sentiments, key=lambda x: x.get("compound", 0), reverse=True)[:5]
                for idx, h in enumerate(positive_headlines, 1):
                    text = h["text"][:100] + "..." if len(h["text"]) > 100 else h["text"]
                    score = h.get("compound", 0)
                    st.success(f"**{idx}. [{score:.2f}]** {text}")
            
            with col2:
                st.subheader("⚠️ Top Negative News (SELL Indicators)")
                negative_headlines = sorted(sentiments, key=lambda x: x.get("compound", 0))[:5]
                for idx, h in enumerate(negative_headlines, 1):
                    text = h["text"][:100] + "..." if len(h["text"]) > 100 else h["text"]
                    score = h.get("compound", 0)
                    st.error(f"**{idx}. [{score:.2f}]** {text}")
            
            st.write("---")
            st.markdown("**📌 Data Sources:**")
            st.markdown("""
            - 🔗 **Economic Times** (economictimes.indiatimes.com) - Leading financial news
            - 🔗 **Moneycontrol** (moneycontrol.com) - Stock market news & analysis
            - 🔗 **NSE** (nseindia.com) - National Stock Exchange official
            - 🔗 **BSE** (bseindia.com) - Bombay Stock Exchange official
            - 📊 **Sentiment Analysis**: NLTK VADER (Natural Language Processing)
            """)
        else:
            st.warning("Could not fetch news headlines at this time.")


# ============ Page 2: Stock Predictions ============
elif page == "📊 Stock Predictions":
    st.header("📊 Future Stock Predictions - AI Analysis")
    
    st.info("""
    🤖 **How does AI prediction work?**
    - Analyzes 1 year of historical price data
    - Considers latest news sentiment (positive/negative)
    - Uses Random Forest ML model to predict if price will go UP or DOWN
    - Shows probability score (0-100%)
    """)
    
    st.write("---")
    
    # Popular stocks list with sectors
    popular_stocks = {
        "💼 Finance": ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS"],
        "🖥️ IT/Tech": ["TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS"],
        "🏭 Industrial": ["ADANIENT.NS", "MARUTI.NS", "BAJAJFINSV.NS"],
        "🛢️ Energy": ["BPCL.NS", "COALINDIA.NS"],
        "🏪 FMCG": ["ITC.NS", "HINDUNILVR.NS", "BRITANNIA.NS"],
    }
    
    # Filter by sector
    st.subheader("🔍 Filter Stocks by Sector")
    selected_sector = st.selectbox(
        "Select a Sector",
        ["All Stocks"] + list(popular_stocks.keys()),
        help="Choose a sector to filter stocks"
    )
    
    if selected_sector == "All Stocks":
        watchlist = []
        for sector_stocks in popular_stocks.values():
            watchlist.extend(sector_stocks)
    else:
        watchlist = popular_stocks.get(selected_sector, [])
    
    # Prediction filter
    col1, col2 = st.columns(2)
    with col1:
        min_probability = st.slider(
            "Minimum Probability (for UP movement)",
            0.0, 1.0, 0.5,
            help="Filter stocks by minimum prediction probability"
        )
    with col2:
        prediction_type = st.radio(
            "Show Predictions",
            ["Only Strong BUY (>60%)", "All Predictions", "Only Strong SELL (<40%)"],
            horizontal=True
        )
    
    st.write("---")
    
    if st.button("🚀 Analyze & Predict Stock Prices", key="predict_btn"):
        with st.spinner("⏳ Fetching data and training AI model... This may take 30-60 seconds"):
            try:
                # Fetch news and analyze
                news = fetch_market_news()
                combined_headlines = []
                for src, headlines in news.items():
                    combined_headlines.extend(headlines)
                
                sentiments = analyze_headlines(combined_headlines[:100])
                
                # Build sentiment map per symbol
                sent_map = {s: 0.0 for s in watchlist}
                for rec in sentiments:
                    t = rec["text"].lower()
                    for s in watchlist:
                        base = s.split(".")[0].lower()
                        if base in t:
                            sent_map[s] += rec.get("compound", 0.0)
                
                # Fetch prices
                prices = fetch_multiple_prices(watchlist, period="1y")
                
                # Build and train model
                train_df = build_training_set(prices, sent_map)
                
                if train_df is not None and not train_df.empty:
                    model = train_model(train_df, persist_path="models/model.joblib")
                    preds = predict_for_symbols(model, train_df) if model else {}
                    
                    # Create results dataframe
                    results = []
                    for symbol, prob in preds.items():
                        prob_pct = prob * 100
                        
                        # Determine signal
                        if prob > 0.6:
                            signal = "🟢 STRONG BUY"
                            color_class = "call"
                        elif prob > 0.55:
                            signal = "🟢 BUY"
                            color_class = "call"
                        elif prob < 0.4:
                            signal = "🔴 STRONG SELL"
                            color_class = "put"
                        elif prob < 0.45:
                            signal = "🔴 SELL"
                            color_class = "put"
                        else:
                            signal = "🟡 HOLD"
                            color_class = "neutral"
                        
                        # Get sector
                        sector = "Unknown"
                        for sec, stocks in popular_stocks.items():
                            if symbol in stocks:
                                sector = sec.split()[1]
                                break
                        
                        results.append({
                            "Symbol": symbol,
                            "Sector": sector,
                            "Signal": signal,
                            "Probability (%)": f"{prob_pct:.1f}%",
                            "Confidence": "High" if prob > 0.6 or prob < 0.4 else "Medium",
                            "News Sentiment": f"{sent_map.get(symbol, 0):.2f}"
                        })
                    
                    # Convert to DataFrame
                    results_df = pd.DataFrame(results)
                    
                    # Apply filtering
                    filtered_df = results_df.copy()
                    if prediction_type == "Only Strong BUY (>60%)":
                        filtered_df = filtered_df[filtered_df["Probability (%)"].str.rstrip("%").astype(float) > 60]
                    elif prediction_type == "Only Strong SELL (<40%)":
                        filtered_df = filtered_df[filtered_df["Probability (%)"].str.rstrip("%").astype(float) < 40]
                    
                    # Sort by probability
                    filtered_df["Prob_Val"] = filtered_df["Probability (%)"].str.rstrip("%").astype(float)
                    filtered_df = filtered_df.sort_values("Prob_Val", ascending=False).drop("Prob_Val", axis=1)
                    
                    # ========== ENHANCED: Show Strong BUY first ==========
                    strong_buy_df = filtered_df[filtered_df["Signal"] == "🟢 STRONG BUY"]
                    other_df = filtered_df[filtered_df["Signal"] != "🟢 STRONG BUY"]
                    
                    if len(strong_buy_df) > 0:
                        st.subheader(f"� STRONG BUY STOCKS - {len(strong_buy_df)} STOCKS WITH HIGH CONFIDENCE")
                        st.markdown("""
                        <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 5px solid #28a745;">
                        <b>✨ These stocks have the HIGHEST probability of going UP (>60%)</b><br/>
                        <small>Based on AI analysis + Latest market news sentiment</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for idx, row in strong_buy_df.iterrows():
                            st.markdown(f"""
                            <div class="call-box">
                                <b>✅ {row['Symbol']}</b> ({row['Sector']})<br/>
                                🎯 Signal: {row['Signal']} | Probability: <b>{row['Probability (%)']}</b><br/>
                                💪 Confidence: {row['Confidence']} | 📰 News Sentiment: {row['News Sentiment']}<br/>
                                <small style="color: green;">✓ RECOMMENDED FOR TODAY'S TRADING</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.write("---")
                    
                    st.subheader(f"�📈 All Stock Predictions ({len(filtered_df)} stocks)")
                    
                    if len(filtered_df) > 0:
                        # Display as table with color coding
                        st.markdown("### Predicted Stock Movements:")
                        
                        for idx, row in filtered_df.iterrows():
                            if "BUY" in row["Signal"]:
                                st.markdown(f"""
                                <div class="call-box">
                                    <b>{row['Symbol']}</b> ({row['Sector']}) | {row['Signal']} | {row['Probability (%)']} 
                                    <br/><small>Confidence: {row['Confidence']} | News Score: {row['News Sentiment']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                            elif "SELL" in row["Signal"]:
                                st.markdown(f"""
                                <div class="put-box">
                                    <b>{row['Symbol']}</b> ({row['Sector']}) | {row['Signal']} | {row['Probability (%)']} 
                                    <br/><small>Confidence: {row['Confidence']} | News Score: {row['News Sentiment']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="neutral-box">
                                    <b>{row['Symbol']}</b> ({row['Sector']}) | {row['Signal']} | {row['Probability (%)']} 
                                    <br/><small>Confidence: {row['Confidence']} | News Score: {row['News Sentiment']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("---")
                        st.markdown("**📊 Full Data Table:**")
                        st.dataframe(filtered_df, use_container_width=True)
                    else:
                        st.warning("No stocks match the selected criteria. Try adjusting filters.")
                else:
                    st.warning("⚠️ Could not build training set. Some stocks may not have sufficient price data.")
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
    
    st.write("---")
    st.markdown("**📌 How to interpret the results:**")
    st.markdown("""
    - **🟢 STRONG BUY**: Probability >60% to go UP - Best opportunity
    - **🟢 BUY**: Probability 55-60% to go UP - Good opportunity  
    - **🟡 HOLD**: Probability 40-55% - Uncertain, wait for clarity
    - **🔴 SELL**: Probability 40-45% to go DOWN - Consider selling
    - **🔴 STRONG SELL**: Probability <40% to go DOWN - High risk
    
    **Data Source**: 
    - 📊 Price Data: Yahoo Finance
    - 📰 News Data: Economic Times, Moneycontrol, NSE, BSE
    - 🤖 AI Model: Random Forest Classifier (trained on 1-year historical data)
    """)


# ============ Page 3: News Sentiment ============
elif page == "📰 News Sentiment":
    st.header("📰 What Are People Saying About Stocks?")
    
    st.info("""
    📊 **Sentiment Analysis Explained:**
    - **Positive** (Green ✅): Good news about the market/stocks
    - **Negative** (Red ❌): Bad news that might hurt stock prices
    - **Neutral** (Gray): Facts without clear positive/negative impact
    """)
    
    st.write("---")
    
    news = fetch_market_news()
    
    if news:
        st.subheader("📺 News Sentiment by Source")
        
        # Create sentiment data for all sources
        sentiment_by_source = {}
        
        for source, headlines in news.items():
            if headlines:
                sentiments = analyze_headlines(headlines[:30])
                
                pos_count = sum(1 for s in sentiments if s.get("compound", 0) > 0.05)
                neg_count = sum(1 for s in sentiments if s.get("compound", 0) < -0.05)
                neu_count = len(sentiments) - pos_count - neg_count
                
                sentiment_by_source[source] = {
                    "Positive": pos_count,
                    "Negative": neg_count,
                    "Neutral": neu_count,
                    "Total": len(sentiments)
                }
        
        # Display in columns
        cols = st.columns(2)
        
        for idx, (source, counts) in enumerate(sentiment_by_source.items()):
            with cols[idx % 2]:
                source_name = source.replace("_", " ").title()
                st.markdown(f"### {source_name}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Positive", counts["Positive"], 
                             f"{(counts['Positive']/counts['Total']*100):.0f}%")
                with col2:
                    st.metric("❌ Negative", counts["Negative"],
                             f"{(counts['Negative']/counts['Total']*100):.0f}%")
                with col3:
                    st.metric("➡️ Neutral", counts["Neutral"],
                             f"{(counts['Neutral']/counts['Total']*100):.0f}%")
                
                # Bar chart
                chart_data = {
                    "Positive": counts["Positive"],
                    "Negative": counts["Negative"],
                    "Neutral": counts["Neutral"]
                }
                st.bar_chart(chart_data)
        
        st.write("---")
        st.markdown("**📌 Data Sources:**")
        source_info = {
            "📰 Economic Times": "Leading business & stock market news | economictimes.indiatimes.com",
            "💰 Moneycontrol": "Stock analysis & market updates | moneycontrol.com",
            "🏛️ NSE": "National Stock Exchange official news | nseindia.com",
            "🏢 BSE": "Bombay Stock Exchange official news | bseindia.com"
        }
        for src, desc in source_info.items():
            st.write(f"**{src}:** {desc}")
    else:
        st.warning("Could not fetch news data")

# ============ Page 4: Stock Trends ============
elif page == "💹 Stock Trends":
    st.header("💹 Stock Price History - Learn the Trends")
    
    st.info("""
    📈 **How to read stock charts?**
    - Look at the overall direction (UP = good to buy, DOWN = good to sell)
    - Higher prices = stock is performing well
    - Look for patterns and recent changes
    """)
    
    st.write("---")
    
    # Popular stocks
    popular_stocks_list = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "ITC.NS", "HDFCBANK.NS",
        "WIPRO.NS", "ICICIBANK.NS", "MARUTI.NS", "ADANIENT.NS", "KOTAKBANK.NS"
    ]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_symbol = st.selectbox(
            "🔍 Select a Stock to View",
            popular_stocks_list,
            help="Choose any stock to see its price history"
        )
    
    with col2:
        time_period = st.radio(
            "📅 Time Period",
            ["3 months", "6 months", "1 year", "2 years"],
            horizontal=True,
            help="How far back to look"
        )
    
    period_map = {
        "3 months": "3mo",
        "6 months": "6mo",
        "1 year": "1y",
        "2 years": "2y"
    }
    
    if st.button("📊 Load Price Chart", key="load_chart"):
        with st.spinner(f"Loading {time_period} price data for {selected_symbol}..."):
            try:
                price_df = fetch_price(selected_symbol, period=period_map[time_period])
                
                if price_df is not None and not price_df.empty:
                    st.subheader(f"{selected_symbol} - {time_period} Price Trend")
                    
                    # Display the chart
                    st.line_chart(price_df[["Close"]])
                    
                    # Display statistics
                    st.write("---")
                    st.subheader("📊 Stock Statistics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    current_price = price_df['Close'].iloc[-1]
                    high_price = price_df['Close'].max()
                    low_price = price_df['Close'].min()
                    first_price = price_df['Close'].iloc[0]
                    pct_change = ((current_price - first_price) / first_price) * 100
                    
                    with col1:
                        st.metric("💹 Current Price", f"₹{current_price:.2f}", 
                                 f"{pct_change:+.2f}%")
                    with col2:
                        st.metric("📈 Highest Price ({})".format(time_period), 
                                 f"₹{high_price:.2f}")
                    with col3:
                        st.metric("📉 Lowest Price ({})".format(time_period), 
                                 f"₹{low_price:.2f}")
                    with col4:
                        st.metric("📊 Price Range", f"₹{(high_price-low_price):.2f}",
                                 f"{((high_price-low_price)/low_price*100):.1f}%")
                    
                    st.write("---")
                    
                    # Interpretation
                    st.markdown("### 💡 What This Means:")
                    if pct_change > 10:
                        st.success(f"📈 **Stock is UP {pct_change:.1f}%** - Price has increased well in {time_period}")
                    elif pct_change > 0:
                        st.success(f"📈 **Stock is UP {pct_change:.1f}%** - Stock is performing positively")
                    elif pct_change > -10:
                        st.warning(f"📉 **Stock is DOWN {pct_change:.1f}%** - Minor decline, watch for recovery")
                    else:
                        st.error(f"📉 **Stock is DOWN {pct_change:.1f}%** - Significant decline, be cautious")
                    
                else:
                    st.warning(f"Could not fetch data for {selected_symbol}")
            except Exception as e:
                st.error(f"Error loading chart: {str(e)}")
    
    st.write("---")
    st.markdown("**📌 Data Source:**")
    st.markdown("""
    - 📊 **Yahoo Finance** (finance.yahoo.com) - Real-time stock price data
    - 🌍 **NSE/BSE** - Indian stock exchange data
    """)


# ============ Footer & Refresh Button ============
st.write("---")
st.sidebar.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    st.sidebar.info("""
    **ℹ️ About This App:**
    
    A beginner-friendly AI tool for Indian stock market analysis. 
    
    **Disclaimer:** This is for educational purposes only. Not financial advice. 
    Always consult a financial advisor before investing.
    """)

with col2:
    if st.sidebar.button("🔄 Refresh All Data"):
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("🔐 Real-time data from NSE, BSE & Yahoo Finance | Last updated: December 31, 2025")

