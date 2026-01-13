import streamlit as st
from data_fetcher import fetch_market_news, fetch_price, fetch_multiple_prices
from sentiment_analysis import analyze_headlines, score_text
from visualizer import plot_sentiment_bar, plot_price_trend
# from predictor import build_training_set, train_model, predict_for_symbols  # Old ML-based predictions
from realtime_data import get_index_data, get_stock_data, data_fetcher
from intraday_predictor import get_index_predictions, get_stock_picks
from enhanced_intraday_predictor import get_enhanced_intraday_tables
from stable_predictor import get_stable_predictions
from fast_cache import cached_fetch, CACHE_KEYS
from utils import get_logger
import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
from typing import Dict

logger = get_logger("ui_app")

def _display_index_card(index_name: str, pred_data: Dict, full_width: bool = False):
    """Display a single index card with responsive design."""
    # Determine card color based on signal
    if pred_data['signal'] == 'CALL':
        bg_color = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
        emoji = '📈'
    elif pred_data['signal'] == 'PUT':
        bg_color = 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)'
        emoji = '📉'
    else:
        bg_color = 'linear-gradient(135deg, #6c757d 0%, #495057 100%)'
        emoji = '➡️'
    
    # Responsive padding and font sizes
    if st.session_state.get('screen_width', 1200) < 480:
        padding = '15px'
        font_size = '1.8em'
        name_font = '1.0em'
    elif st.session_state.get('screen_width', 1200) < 768:
        padding = '20px'
        font_size = '2.2em'
        name_font = '1.1em'
    else:
        padding = '25px'
        font_size = '2.5em'
        name_font = '1.2em'
    
    # Custom index card
    st.markdown(f"""
    <div style="background: {bg_color}; color: white; padding: {padding}; border-radius: 15px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <div style="text-align: center; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: {name_font};">{index_name}</h3>
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: {font_size}; font-weight: bold; margin-bottom: 10px;">{emoji} {pred_data['signal']}</div>
            <div style="font-size: 1.1em;">Confidence: {pred_data['confidence']}%</div>
        </div>
        <div style="font-size: 0.9em; opacity: 0.9;">
            <strong>Current Price:</strong> ₹{pred_data.get('current_price', 0):.2f}<br/>
            <strong>Change:</strong> {pred_data.get('price_change_pct', 0):+.2f}%<br/>
            <strong>Volume:</strong> {pred_data.get('volume_ratio', 1.0):.1f}x avg
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display reasons
    if pred_data.get('reasons'):
        st.markdown("**Why this signal?**")
        for reason in pred_data['reasons']:
            st.write(f"• {reason}")
st.set_page_config(
    page_title="Live Intraday Stock Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",  # Auto-adjust based on screen size
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Live Intraday Stock Market Predictor - Educational Tool"
    }
)

# Custom CSS for responsive beginner-friendly styling
st.markdown("""
    <style>
    /* Base styles */
    .big-font { font-size: 24px; font-weight: bold; color: #1f77b4; }
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .call-box { background-color: #d4edda; padding: 20px; border-radius: 12px; border-left: 6px solid #28a745; margin: 10px 0; }
    .put-box { background-color: #f8d7da; padding: 20px; border-radius: 12px; border-left: 6px solid #dc3545; margin: 10px 0; }
    .neutral-box { background-color: #e7e7e7; padding: 20px; border-radius: 12px; border-left: 6px solid #6c757d; margin: 10px 0; }
    .index-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .stock-pick-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #007bff; }
    .confidence-badge { background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .disclaimer { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .big-font { font-size: 18px; }
        .call-box, .put-box, .neutral-box { padding: 15px; margin: 8px 0; }
        .index-card { padding: 20px; margin: 10px 0; }
        .stock-pick-card { padding: 15px; margin: 8px 0; }
        .disclaimer { padding: 12px; margin: 15px 0; }
    }
    
    @media (max-width: 480px) {
        .big-font { font-size: 16px; }
        .call-box, .put-box, .neutral-box { padding: 12px; margin: 5px 0; }
        .index-card { padding: 15px; margin: 8px 0; }
        .stock-pick-card { padding: 12px; margin: 5px 0; }
        .disclaimer { padding: 10px; margin: 10px 0; }
    }
    
    /* Table responsive styles */
    .dataframe {
        font-size: 14px;
    }
    
    @media (max-width: 768px) {
        .dataframe {
            font-size: 12px;
        }
    }
    
    @media (max-width: 480px) {
        .dataframe {
            font-size: 10px;
        }
    }
    
    /* Hide streamlit footer on mobile */
    @media (max-width: 768px) {
        .stDeployButton {
            display: none;
        }
    }
    
    /* Responsive columns */
    @media (max-width: 768px) {
        .element-container:has([data-testid="stHorizontalBlock"]) {
            flex-direction: column !important;
        }
    }
    
    /* Mobile-friendly sidebar */
    @media (max-width: 768px) {
        .css-1d391kg {
            width: 100% !important;
        }
    }
    
    /* Touch-friendly buttons */
    @media (max-width: 768px) {
        .stButton > button {
            padding: 12px 24px;
            font-size: 16px;
            margin: 5px 0;
        }
    }
    
    /* Responsive metrics */
    @media (max-width: 768px) {
        .metric-container {
            margin: 5px 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Live Intraday Stock Predictor")
st.write("*Real-time intraday predictions for Indian indices and stocks*")
st.write(f"<small>Last Updated: {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}</small>", unsafe_allow_html=True)

# Mobile-friendly header
st.markdown("""
<style>
@media (max-width: 768px) {
    .stTitle {
        font-size: 24px !important;
    }
    .stMarkdown {
        font-size: 14px !important;
    }
}
@media (max-width: 480px) {
    .stTitle {
        font-size: 20px !important;
    }
    .stMarkdown {
        font-size: 12px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation - responsive design
st.sidebar.header("📋 Navigation")
page = st.sidebar.radio("Choose a Section", [
    "🎯 Live Market Calls",
    "📊 Intraday Stock Picks",
    "📰 News Sentiment",
    "💹 Stock Trends"
], key="navigation")

# Auto-refresh control - mobile-friendly
st.sidebar.header("⚙️ Settings")
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (60s)", value=False)
if auto_refresh:
    st.sidebar.warning("Auto-refresh is disabled for better performance")
    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
else:
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Add mobile-friendly info
st.sidebar.markdown("---")
st.sidebar.markdown("**📱 Device Info:**")
if st.sidebar.button("📊 Show Performance Tips"):
    st.sidebar.info("""
    💡 **Performance Tips:**
    - Use manual refresh on mobile
    - Close other tabs for better speed
    - Use WiFi for faster loading
    - Refresh data when needed
    """)

# Add loading optimization info
st.sidebar.markdown("---")
st.sidebar.markdown("**⚡ Performance:**")
st.sidebar.info("""
    🚀 **Optimizations Active:**
    - 24hr stable predictions
    - Smart caching enabled
    - Fast loading times
    - Minimal data usage
    """)

# Add cache management
st.sidebar.markdown("---")
st.sidebar.markdown("**🗂️ Cache Management:**")
if st.sidebar.button("🔄 Clear Cache & Regenerate"):
    from fast_cache import fast_cache
    fast_cache.clear()
    from stable_predictor import stable_predictor
    try:
        os.remove(stable_predictor.prediction_file)
    except:
        pass
    st.sidebar.success("Cache cleared! New predictions will be generated.")
    st.rerun()

# Add force refresh button for dynamic reasons
st.sidebar.markdown("---")
st.sidebar.markdown("**📰 Dynamic Reasons:**")
if st.sidebar.button("🌐 Refresh with Latest News", help="Generate new predictions with current market news"):
    from fast_cache import fast_cache
    from stable_predictor import stable_predictor
    fast_cache.clear()
    try:
        os.remove(stable_predictor.prediction_file)
    except:
        pass
    st.sidebar.info("Fetching latest news and generating new reasons...")
    st.rerun()

# ============ Page 1: Live Market Calls ============
if page == "🎯 Live Market Calls":
    st.header("🎯 Live Market Calls - Real-time Index Predictions")
    
    st.info("""
    💡 **What does this mean for beginners?**
    - **CALL**: Market expected to go UP ⬆️ - Consider buying CALL options
    - **PUT**: Market expected to go DOWN ⬇️ - Consider buying PUT options
    - **NEUTRAL**: Market UNCERTAIN - Be cautious with new positions
    
    📊 **Confidence %**: How sure we are about the prediction (higher = better)
    """)
    
    # Add disclaimer
    st.markdown("""
    <div class="disclaimer">
    <strong>⚠️ Educational Disclaimer:</strong> This is for educational purposes only and NOT financial advice. 
    Always consult a qualified financial advisor before making any investment decisions. 
    Markets are inherently risky and predictions can be wrong.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Fetch real-time predictions with fast caching
    with st.spinner("🔄 Loading market data..."):
        try:
            # Use cached data for faster loading
            predictions = cached_fetch(
                CACHE_KEYS['index_predictions'],
                get_index_predictions,
                max_age_hours=0.5  # 30 minutes cache
            )
            
            # Display index predictions in responsive cards
            # Responsive columns based on screen size
            if st.session_state.get('screen_width', 1200) < 768:
                # Mobile: Single column
                for i, (index_name, pred_data) in enumerate(predictions.items()):
                    _display_index_card(index_name, pred_data, full_width=True)
            elif st.session_state.get('screen_width', 1200) < 1024:
                # Tablet: 2 columns
                col1, col2 = st.columns(2)
                items = list(predictions.items())
                for i, (index_name, pred_data) in enumerate(items[:2]):
                    with [col1, col2][i]:
                        _display_index_card(index_name, pred_data)
                if len(items) > 2:
                    with col1:
                        _display_index_card(items[2][0], items[2][1])
            else:
                # Desktop: 3 columns
                col1, col2, col3 = st.columns(3)
                for i, (index_name, pred_data) in enumerate(predictions.items()):
                    col = [col1, col2, col3][i]
                    with col:
                        _display_index_card(index_name, pred_data)
            
            st.write("---")
            
            # Market summary
            st.subheader("📊 Market Summary")
            
            # Calculate overall market sentiment
            calls = sum(1 for p in predictions.values() if p['signal'] == 'CALL')
            puts = sum(1 for p in predictions.values() if p['signal'] == 'PUT')
            neutrals = sum(1 for p in predictions.values() if p['signal'] == 'NEUTRAL')
            avg_confidence = sum(p['confidence'] for p in predictions.values()) / 3
            
            # Display responsive market summary
            if st.session_state.get('screen_width', 1200) < 768:
                # Mobile: 2x2 grid
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📈 CALL Signals", calls, f"{calls/3*100:.0f}%")
                with col2:
                    st.metric("📉 PUT Signals", puts, f"{puts/3*100:.0f}%")
                
                col3, col4 = st.columns(2)
                with col3:
                    st.metric("➡️ NEUTRAL", neutrals, f"{neutrals/3*100:.0f}%")
                with col4:
                    st.metric("💯 Avg Confidence", f"{avg_confidence:.1f}%", "Overall confidence")
            else:
                # Desktop/Tablet: 4 columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📈 CALL Signals", calls, f"{calls/3*100:.0f}%")
                with col2:
                    st.metric("📉 PUT Signals", puts, f"{puts/3*100:.0f}%")
                with col3:
                    st.metric("➡️ NEUTRAL", neutrals, f"{neutrals/3*100:.0f}%")
                with col4:
                    st.metric("💯 Avg Confidence", f"{avg_confidence:.1f}%", "Overall confidence")
            
            # Overall market recommendation
            if calls > puts:
                overall_sentiment = "🟢 BULLISH - Market bias towards CALL options"
                sentiment_color = "green"
            elif puts > calls:
                overall_sentiment = "🔴 BEARISH - Market bias towards PUT options"
                sentiment_color = "red"
            else:
                overall_sentiment = "🟡 MIXED - Market uncertain, be cautious"
                sentiment_color = "orange"
            
            st.markdown(f"**Overall Market Sentiment:** <span style='color: {sentiment_color}; font-weight: bold;'>{overall_sentiment}</span>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error fetching live data: {str(e)}")
            st.info("Please check your internet connection and try again.")

# ============ Page 2: Intraday Stock Picks ============
elif page == "📊 Intraday Stock Picks":
    st.header("📊 Enhanced Intraday Analysis - 3 Separate Tables")
    
    st.info("""
    🎯 **Advanced Intraday Predictions:**
    - **Regular Stocks**: Large-cap stocks with stable movements
    - **Penny Stocks**: High-risk, high-reward opportunities (< ₹50)
    - **Mixed Picks**: Best opportunities from both categories
    
    📊 **Table Columns Explained:**
    - **Buy Position**: Optimal entry point for the trade
    - **Sell Position**: Target exit point for profit
    - **Reason**: Why this stock is recommended
    - **High Returns**: Expected profit range
    - **Risk Factors**: Potential risks to consider
    """)
    
    # Add disclaimer
    st.markdown("""
    <div class="disclaimer">
    <strong>⚠️ Educational Disclaimer:</strong> These are educational recommendations, NOT financial advice. 
    Penny stocks are extremely risky and can result in complete loss of capital. 
    Always consult a financial advisor and do your own research.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Add info about dynamic reasons
    st.info("""
    📰 **Dynamic News-Based Reasons:**
    The "Reason to Buy/Sell" column now shows real-time reasons based on:
    - Current market news and events
    - Festival seasons (PONGAL, Diwali, etc.)
    - Economic announcements
    - Government policies
    - Seasonal trends
    
    Click "🌐 Refresh with Latest News" in sidebar for fresh reasons!
    """)
    
    # Fetch enhanced intraday tables with loading optimization
    with st.spinner(" Loading optimized predictions..."):
        try:
            # Use stable predictor with caching for ultra-fast loading
            intraday_tables = cached_fetch(
                CACHE_KEYS['stock_predictions'],
                get_stable_predictions,
                max_age_hours=23  # 23 hours cache (stable for the day)
            )
            
            # Display each table
            for table_name, stocks in intraday_tables.items():
                if not stocks:
                    continue
                    
                st.subheader(f"📈 {table_name} - Top {len(stocks)} Picks")
                
                # Create DataFrame for the table
                table_data = []
                for stock in stocks:
                    table_data.append({
                        'Stock Name': stock['stock_name'],
                        'Price': stock['price'],
                        'Buy Position': stock['buy_position'],
                        'Sell Position': stock['sell_position'],
                        'Reason to Buy/Sell': stock['reason'],
                        'High Returns': stock['high_returns'],
                        'Risk Factors': stock['risk_factors'],
                        'Confidence': f"{stock['confidence']:.0f}%"
                    })
                
                df = pd.DataFrame(table_data)
                
                # Display with responsive styling
                def color_confidence(val):
                    if isinstance(val, str) and '%' in val:
                        conf_val = float(val.replace('%', ''))
                        if conf_val >= 80:
                            return 'background-color: #d4edda; color: #155724'
                        elif conf_val >= 60:
                            return 'background-color: #fff3cd; color: #856404'
                        else:
                            return 'background-color: #f8d7da; color: #721c24'
                    return ''
                
                styled_df = df.style.applymap(color_confidence, subset=['Confidence'])
                
                # Responsive table display
                if st.session_state.get('screen_width', 1200) < 768:
                    # Mobile: Show simplified table with horizontal scroll
                    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=300)
                elif st.session_state.get('screen_width', 1200) < 1024:
                    # Tablet: Medium height
                    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)
                else:
                    # Desktop: Full height
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # Add category-specific insights
                if table_name == "Penny Stocks":
                    st.warning("""
                    🚨 **Penny Stock Alert:** These are high-risk, high-reward stocks. 
                    - Only invest what you can afford to lose completely
                    - These stocks can be very volatile
                    - Liquidity may be limited
                    - Suitable for experienced traders only
                    """)
                elif table_name == "Regular Stocks":
                    st.info("""
                    💼 **Regular Stocks:** More stable large-cap stocks. 
                    - Lower risk compared to penny stocks
                    - Better liquidity and tracking
                    - Suitable for most investors
                    - Moderate returns expected
                    """)
                else:  # Mixed Picks
                    st.success("""
                    🎯 **Mixed Picks:** Best opportunities across categories. 
                    - Balanced risk-reward profile
                    - Diversified recommendations
                    - Carefully selected from both segments
                    """)
                
                st.write("---")
            
            # Overall market summary - responsive layout
            st.subheader("📊 Market Summary & Insights")
            
            # Calculate summary statistics
            all_stocks = []
            for stocks in intraday_tables.values():
                all_stocks.extend(stocks)
            
            if all_stocks:
                avg_confidence = sum(s['confidence'] for s in all_stocks) / len(all_stocks)
                penny_count = sum(1 for s in all_stocks if s['is_penny'])
                regular_count = len(all_stocks) - penny_count
                positive_changes = sum(1 for s in all_stocks if s['price_change_pct'] > 0)
                
                # Responsive metrics layout
                if st.session_state.get('screen_width', 1200) < 480:
                    # Mobile: Single column
                    st.metric("💯 Avg Confidence", f"{avg_confidence:.1f}%")
                    st.metric("📈 Penny Stocks", penny_count)
                    st.metric("💼 Regular Stocks", regular_count)
                    st.metric("📊 Positive Signals", f"{positive_changes}/{len(all_stocks)}")
                elif st.session_state.get('screen_width', 1200) < 768:
                    # Tablet: 2x2 grid
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("💯 Avg Confidence", f"{avg_confidence:.1f}%")
                    with col2:
                        st.metric("📈 Penny Stocks", penny_count)
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        st.metric("💼 Regular Stocks", regular_count)
                    with col4:
                        st.metric("📊 Positive Signals", f"{positive_changes}/{len(all_stocks)}")
                else:
                    # Desktop: 4 columns
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("💯 Avg Confidence", f"{avg_confidence:.1f}%")
                    with col2:
                        st.metric("📈 Penny Stocks", penny_count)
                    with col3:
                        st.metric("💼 Regular Stocks", regular_count)
                    with col4:
                        st.metric("📊 Positive Signals", f"{positive_changes}/{len(all_stocks)}")
                
                # Market recommendation
                if avg_confidence > 75:
                    market_rec = "🟢 STRONG MARKET - Good trading conditions"
                elif avg_confidence > 60:
                    market_rec = "🟡 MODERATE MARKET - Decent opportunities"
                else:
                    market_rec = "🔴 WEAK MARKET - Be very cautious"
                
                st.markdown(f"**Overall Market Condition:** {market_rec}")
                
                # Top pick highlight
                top_stock = max(all_stocks, key=lambda x: x['overall_score'])
                st.success(f"🏆 **Today's Top Pick:** {top_stock['stock_name']} at {top_stock['price']} with {top_stock['confidence']:.0f}% confidence")
            
        except Exception as e:
            st.error(f"❌ Error analyzing stocks: {str(e)}")
            st.info("Please check your internet connection and try again.")
    
    st.write("---")
    st.markdown("""
    **📌 How to use these tables:**
    - **Buy Position**: Enter the trade at or near this price
    - **Sell Position**: Take profits at this target price
    - **High Returns**: Expected profit range (not guaranteed)
    - **Risk Factors**: Be aware of these potential issues
    - **Confidence**: How sure we are about the prediction
    
    **⚠️ Important Notes:**
    - These are educational recommendations, NOT financial advice
    - Penny stocks can lose 100% of their value
    - Always use stop-loss orders to limit losses
    - Market conditions can change rapidly
    - Past performance does not guarantee future results
    
    **📊 Data Sources:**
    - Live price data from Yahoo Finance
    - Volume and trend analysis
    - Options chain sentiment (when available)
    - Market news sentiment analysis
    - Technical indicators and patterns
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

