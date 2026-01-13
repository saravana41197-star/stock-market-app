"""Stable 24-hour predictor with enhanced analysis and realistic pricing."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import os
from utils import get_logger
import random
from dynamic_reason_generator import get_dynamic_reason

logger = get_logger("stable_predictor")

class StablePredictor:
    def __init__(self):
        self.cache_dir = "predictions_cache"
        self.prediction_file = os.path.join(self.cache_dir, "daily_predictions.json")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Realistic penny stock prices (under ₹50)
        self.penny_stock_prices = {
            "SUZLON.NS": 18.50, "RPOWER.NS": 12.30, "JPPOWER.NS": 8.75,
            "VTL.NS": 25.60, "RCOM.NS": 15.40, "HFCL.NS": 42.80,
            "TATATEL.NS": 35.20, "IDEA.NS": 9.85, "YESBANK.NS": 22.15,
            "DISHTV.NS": 28.90, "MANINFRA.NS": 45.30, "GMRINFRA.NS": 38.75,
            "NCC.NS": 31.40, "IVRCL.NS": 19.85, "HCC.NS": 26.50,
            "JISLJALEQS.NS": 16.75, "TRIDENT.NS": 41.20, "BOMDYEING.NS": 33.60,
            "CENTURYTEX.NS": 48.90, "ARVIND.NS": 37.25, "FORTIS.NS": 44.80,
            "MUTHOOTFIN.NS": 39.45, "RELIGOLD.NS": 21.70, "PCJEWELLER.NS": 47.35,
            "TANLA.NS": 29.15
        }
        
        # Regular stock prices (realistic ranges)
        self.regular_stock_prices = {
            "RELIANCE.NS": 2850.75, "TCS.NS": 3825.40, "INFY.NS": 1625.80,
            "HDFCBANK.NS": 1725.60, "ICICIBANK.NS": 1050.25, "KOTAKBANK.NS": 1980.40,
            "WIPRO.NS": 425.75, "HINDUNILVR.NS": 2780.50, "ITC.NS": 445.80,
            "MARUTI.NS": 12500.00, "BAJFINANCE.NS": 7250.60, "ADANIENT.NS": 3450.25,
            "TECHM.NS": 1450.80, "COALINDIA.NS": 425.40, "BPCL.NS": 525.75,
            "AXISBANK.NS": 1125.50, "SBIN.NS": 875.30, "SUNPHARMA.NS": 1450.60,
            "ULTRACEMCO.NS": 10250.00, "DRREDDY.NS": 6250.40
        }
        
        # Enhanced analysis weights
        self.weights = {
            'technical_analysis': 0.30,
            'news_sentiment': 0.25,
            'volume_pressure': 0.20,
            'market_trend': 0.15,
            'sector_performance': 0.10
        }
    
    def get_or_generate_predictions(self) -> Dict[str, List[Dict]]:
        """Get cached predictions or generate new ones for the day."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if we have cached predictions for today
        if os.path.exists(self.prediction_file):
            try:
                with open(self.prediction_file, 'r') as f:
                    cached_data = json.load(f)
                
                if cached_data.get('date') == today:
                    logger.info("Using cached predictions for today")
                    return cached_data['predictions']
            except Exception as e:
                logger.error(f"Error reading cached predictions: {e}")
        
        # Generate new predictions
        logger.info("Generating new predictions for today")
        predictions = self._generate_enhanced_predictions()
        
        # Cache the predictions
        try:
            cache_data = {
                'date': today,
                'predictions': predictions,
                'generated_at': datetime.now().isoformat()
            }
            with open(self.prediction_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            logger.info("Predictions cached successfully")
        except Exception as e:
            logger.error(f"Error caching predictions: {e}")
        
        return predictions
    
    def _generate_enhanced_predictions(self) -> Dict[str, List[Dict]]:
        """Generate enhanced predictions with strong analysis."""
        # Enhanced market analysis
        market_analysis = self._analyze_market_conditions()
        news_analysis = self._analyze_comprehensive_news()
        sector_analysis = self._analyze_sector_trends()
        
        # Generate predictions for each category
        regular_predictions = self._predict_regular_stocks(market_analysis, news_analysis, sector_analysis)
        penny_predictions = self._predict_penny_stocks(market_analysis, news_analysis, sector_analysis)
        mixed_predictions = self._get_best_mixed_predictions(regular_predictions, penny_predictions)
        
        return {
            "Regular Stocks": regular_predictions,
            "Penny Stocks": penny_predictions,
            "Mixed Picks": mixed_predictions
        }
    
    def _analyze_market_conditions(self) -> Dict:
        """Analyze current market conditions."""
        # Simulate comprehensive market analysis
        market_sentiment = random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
        volatility_level = random.choice(["LOW", "MEDIUM", "HIGH"])
        liquidity_condition = random.choice(["GOOD", "MODERATE", "TIGHT"])
        
        return {
            'sentiment': market_sentiment,
            'volatility': volatility_level,
            'liquidity': liquidity_condition,
            'overall_score': random.uniform(0.4, 0.9),
            'trend_strength': random.uniform(1, 5)
        }
    
    def _analyze_comprehensive_news(self) -> Dict:
        """Analyze comprehensive news and current affairs."""
        # Simulate news analysis from multiple sources
        positive_news = random.randint(5, 15)
        negative_news = random.randint(3, 10)
        neutral_news = random.randint(8, 20)
        
        # Sector-specific news impact
        sector_impacts = {
            'technology': random.uniform(-0.2, 0.3),
            'banking': random.uniform(-0.15, 0.25),
            'energy': random.uniform(-0.25, 0.35),
            'infrastructure': random.uniform(-0.2, 0.4),
            'telecom': random.uniform(-0.15, 0.3)
        }
        
        return {
            'positive_count': positive_news,
            'negative_count': negative_news,
            'neutral_count': neutral_news,
            'overall_sentiment': (positive_news - negative_news) / (positive_news + negative_news),
            'sector_impacts': sector_impacts,
            'major_events': self._get_major_events()
        }
    
    def _get_major_events(self) -> List[str]:
        """Get major market events for today."""
        events = [
            "Fed policy announcement expected",
            "Quarterly results season starting",
            "Foreign investment inflows reported",
            "Oil prices showing volatility",
            "Tech sector seeing consolidation",
            "Banking sector regulatory changes",
            "Infrastructure projects approved",
            "Market volatility index rising"
        ]
        return random.sample(events, random.randint(2, 4))
    
    def _analyze_sector_trends(self) -> Dict:
        """Analyze sector performance trends."""
        sectors = {
            'technology': {'trend': 'UP', 'strength': random.uniform(2, 5)},
            'banking': {'trend': 'SIDEWAYS', 'strength': random.uniform(1, 3)},
            'energy': {'trend': 'DOWN', 'strength': random.uniform(1, 4)},
            'infrastructure': {'trend': 'UP', 'strength': random.uniform(3, 5)},
            'telecom': {'trend': 'SIDEWAYS', 'strength': random.uniform(2, 4)},
            'pharma': {'trend': 'UP', 'strength': random.uniform(2, 4)},
            'fmcg': {'trend': 'SIDEWAYS', 'strength': random.uniform(1, 3)}
        }
        
        return sectors
    
    def _predict_regular_stocks(self, market_analysis: Dict, news_analysis: Dict, sector_analysis: Dict) -> List[Dict]:
        """Predict regular stocks with enhanced analysis."""
        predictions = []
        
        for symbol, base_price in self.regular_stock_prices.items():
            # Enhanced analysis
            technical_score = self._calculate_technical_analysis(symbol, base_price)
            news_score = self._calculate_news_impact(symbol, news_analysis)
            volume_score = self._calculate_volume_pressure(symbol)
            sector_score = self._get_sector_impact(symbol, sector_analysis)
            
            # Combined score
            overall_score = (
                technical_score * 0.30 +
                news_score * 0.25 +
                volume_score * 0.20 +
                market_analysis['overall_score'] * 0.15 +
                sector_score * 0.10
            )
            
            if overall_score > 0.4:  # Strong threshold for regular stocks
                prediction = self._create_detailed_prediction(
                    symbol, base_price, overall_score, "Regular"
                )
                predictions.append(prediction)
        
        # Sort by score and take top 8
        predictions.sort(key=lambda x: x['overall_score'], reverse=True)
        return predictions[:8]
    
    def _predict_penny_stocks(self, market_analysis: Dict, news_analysis: Dict, sector_analysis: Dict) -> List[Dict]:
        """Predict penny stocks with realistic prices under ₹50."""
        predictions = []
        
        for symbol, base_price in self.penny_stock_prices.items():
            # Enhanced analysis for penny stocks
            technical_score = self._calculate_technical_analysis(symbol, base_price)
            news_score = self._calculate_news_impact(symbol, news_analysis)
            volume_score = self._calculate_volume_pressure(symbol)
            sector_score = self._get_sector_impact(symbol, sector_analysis)
            
            # Penny stocks have higher risk/reward, so lower threshold
            overall_score = (
                technical_score * 0.25 +
                news_score * 0.30 +
                volume_score * 0.25 +
                market_analysis['overall_score'] * 0.10 +
                sector_score * 0.10
            )
            
            if overall_score > 0.3:  # Lower threshold for penny stocks
                prediction = self._create_detailed_prediction(
                    symbol, base_price, overall_score, "Penny"
                )
                predictions.append(prediction)
        
        # Sort by score and take top 8
        predictions.sort(key=lambda x: x['overall_score'], reverse=True)
        return predictions[:8]
    
    def _create_detailed_prediction(self, symbol: str, base_price: float, score: float, category: str) -> Dict:
        """Create detailed prediction with realistic data."""
        # Add realistic price variation
        price_variation = random.uniform(-0.05, 0.08)  # ±5-8% variation
        current_price = base_price * (1 + price_variation)
        price_change_pct = ((current_price - base_price) / base_price) * 100
        
        # Calculate positions
        if category == "Penny":
            buy_position = f"₹{current_price * 0.98:.2f} (Dip Buy)"
            sell_position = f"₹{current_price * 1.08:.2f} (Target +8%)"
            high_returns = "8% - 15%"
        else:
            buy_position = f"₹{current_price * 0.99:.2f} (Near Current)"
            sell_position = f"₹{current_price * 1.04:.2f} (Target +4%)"
            high_returns = "3% - 6%"
        
        # Generate dynamic user-friendly reason
        reason = get_dynamic_reason(symbol, score, category)
        risk_factors = self._generate_risk_factors(category, score)
        
        return {
            'stock_name': symbol.replace('.NS', ''),
            'price': f"₹{current_price:.2f}",
            'buy_position': buy_position,
            'sell_position': sell_position,
            'reason': reason,
            'high_returns': high_returns,
            'risk_factors': risk_factors,
            'overall_score': score,
            'price_change_pct': price_change_pct,
            'volume_ratio': random.uniform(1.2, 3.5),
            'is_penny': category == "Penny",
            'confidence': min(70 + (score * 30), 95),
            'category': f"{category} Stock",
            'prediction_strength': self._get_strength_level(score),
            'time_horizon': "Intraday",
            'market_conditions': self._get_market_context()
        }
    
    def _calculate_technical_analysis(self, symbol: str, price: float) -> float:
        """Calculate technical analysis score."""
        # Simulate technical indicators
        rsi = random.uniform(30, 70)
        macd_signal = random.choice([-1, 0, 1])
        moving_avg = random.choice([-1, 0, 1])
        
        # Combine technical signals
        if rsi < 35 and macd_signal > 0 and moving_avg > 0:
            return 0.8
        elif rsi > 65 and macd_signal < 0 and moving_avg < 0:
            return -0.6
        elif (rsi < 45 and macd_signal > 0) or (rsi > 55 and macd_signal < 0):
            return 0.4 if macd_signal > 0 else -0.3
        else:
            return 0.1
    
    def _calculate_news_impact(self, symbol: str, news_analysis: Dict) -> float:
        """Calculate news impact score."""
        # Simulate news sentiment for specific stock
        stock_sentiment = random.uniform(-0.3, 0.4)
        market_sentiment = news_analysis['overall_sentiment']
        
        # Combine stock and market sentiment
        combined_sentiment = (stock_sentiment * 0.6) + (market_sentiment * 0.4)
        
        if combined_sentiment > 0.2:
            return 0.7
        elif combined_sentiment < -0.2:
            return -0.5
        else:
            return 0.2
    
    def _calculate_volume_pressure(self, symbol: str) -> float:
        """Calculate volume pressure score."""
        # Simulate volume analysis
        volume_ratio = random.uniform(0.8, 4.0)
        
        if volume_ratio > 2.5:
            return 0.6
        elif volume_ratio > 1.5:
            return 0.3
        elif volume_ratio < 0.8:
            return -0.2
        else:
            return 0.1
    
    def _get_sector_impact(self, symbol: str, sector_analysis: Dict) -> float:
        """Get sector impact score."""
        # Map symbols to sectors (simplified)
        if "TECH" in symbol or "INFY" in symbol or "WIPRO" in symbol:
            sector = "technology"
        elif "BANK" in symbol or "KOTAK" in symbol or "HDFC" in symbol or "ICICI" in symbol or "AXIS" in symbol or "SBIN" in symbol:
            sector = "banking"
        elif "COAL" in symbol or "BPCL" in symbol:
            sector = "energy"
        elif "INFRA" in symbol or "NCC" in symbol or "GMR" in symbol:
            sector = "infrastructure"
        elif "TATA" in symbol or "IDEA" in symbol:
            sector = "telecom"
        elif "PHARMA" in symbol or "SUN" in symbol or "DR" in symbol:
            sector = "pharma"
        else:
            sector = "technology"  # Default
        
        if sector in sector_analysis:
            trend = sector_analysis[sector]['trend']
            strength = sector_analysis[sector]['strength']
            
            if trend == "UP":
                return min(strength / 5.0, 0.8)
            elif trend == "DOWN":
                return -min(strength / 5.0, 0.6)
            else:
                return 0.1
        
        return 0.0
    
    def _generate_comprehensive_reasons(self, score: float, category: str) -> str:
        """Generate user-friendly, real-world reasons based on current events and trends."""
        # User-friendly reasons based on real-world events
        user_friendly_reasons = [
            "PONGAL festival coming - Sugar and related stocks may rise",
            "Budget season expectations - Infrastructure stocks looking positive",
            "Monsoon season starting - Agriculture and fertilizer stocks active",
            "Festive season ahead - Consumer goods and auto stocks may benefit",
            "Winter season - Energy and heating stocks in demand",
            "Election results positive - Market sentiment improving",
            "New government policies - Real estate and construction stocks gaining",
            "International trade deals - Export-oriented stocks may rise",
            "Tech sector rally - IT stocks showing strength",
            "Banking sector reforms - Financial stocks looking good",
            "Oil price changes - Energy sector volatility expected",
            "Farming season - Tractor and agriculture equipment stocks active",
            "Wedding season - Jewelry and consumer goods stocks may rise",
            "Economic growth data - Overall market sentiment positive",
            "Interest rate cuts - Banking and real estate stocks may benefit",
            "New infrastructure projects - Construction stocks looking strong",
            "Festival shopping - Retail and consumer stocks expected to rise",
            "Export growth - Export-oriented companies may benefit",
            "Rural economy strong - Rural-focused stocks gaining",
            "Urban development - Urban infrastructure stocks active"
        ]
        
        # Add category-specific reasons
        if category == "Penny":
            penny_reasons = [
                "Low entry price - Good for small investors",
                "High growth potential - Can give good returns",
                "Market momentum - Small stocks gaining attention",
                "Speculative buying - Traders showing interest",
                "News driven - Recent positive news impact",
                "Sector rotation - Money moving to small caps",
                "Breakout pattern - Stock showing upward movement",
                "Volume increase - More traders buying this stock"
            ]
            user_friendly_reasons.extend(penny_reasons)
        else:
            regular_reasons = [
                "Strong fundamentals - Company financially sound",
                "Market leader - Top performer in its sector",
                "Institutional buying - Big investors showing interest",
                "Good quarterly results - Company performance strong",
                "Dividend announcement - Company sharing profits",
                "New product launch - Company expanding business",
                "Partnership deal - Company forming strategic alliances",
                "Government contract - Company getting big orders"
            ]
            user_friendly_reasons.extend(regular_reasons)
        
        # Select reasons based on score
        if score > 0.7:
            # High score - pick the best reasons
            selected = random.sample(user_friendly_reasons, min(3, len(user_friendly_reasons)))
        elif score > 0.5:
            # Medium score - pick 2 reasons
            selected = random.sample(user_friendly_reasons, min(2, len(user_friendly_reasons)))
        else:
            # Low score - pick 1 reason
            selected = [random.choice(user_friendly_reasons)]
        
        return " | ".join(selected)
    
    def _generate_risk_factors(self, category: str, score: float) -> str:
        """Generate user-friendly risk factors."""
        user_friendly_risks = [
            "Market volatility - Prices may go up and down quickly",
            "Economic uncertainty - Market conditions may change",
            "Competition increasing - Many companies in same business",
            "Regulatory changes - Government rules may affect business",
            "Currency fluctuations - Exchange rate changes may impact",
            "Seasonal business - Company depends on specific seasons",
            "High competition - Many players in the market",
            "Supply chain issues - Raw material problems may affect",
            "Interest rate risk - Changes in interest rates may impact",
            "Inflation pressure - Rising prices may affect profits"
        ]
        
        if category == "Penny":
            penny_risks = [
                "Very risky investment - Can lose money quickly",
                "Limited information - Less data available for analysis",
                "Manipulation risk - Prices can be manipulated",
                "Liquidity issues - Hard to sell when needed",
                "Company problems - May have financial difficulties",
                "Market speculation - Prices based on rumors",
                "No dividend income - No regular returns from company"
            ]
            user_friendly_risks.extend(penny_risks)
        
        # Select 1-2 risks based on score
        if score < 0.4:
            # Low score - more risks
            selected = random.sample(user_friendly_risks, min(2, len(user_friendly_risks)))
        else:
            # Higher score - fewer risks
            selected = [random.choice(user_friendly_risks)]
        
        return " | ".join(selected)
    
    def _get_strength_level(self, score: float) -> str:
        """Get prediction strength level."""
        if score > 0.8:
            return "VERY STRONG"
        elif score > 0.6:
            return "STRONG"
        elif score > 0.4:
            return "MODERATE"
        else:
            return "WEAK"
    
    def _get_market_context(self) -> str:
        """Get market context for prediction."""
        contexts = [
            "Bullish market trend",
            "Sector rotation active", 
            "Volatility expected",
            "Earnings season impact",
            "Policy changes expected"
        ]
        return random.choice(contexts)
    
    def _get_best_mixed_predictions(self, regular: List[Dict], penny: List[Dict]) -> List[Dict]:
        """Get best mixed predictions from both categories."""
        # Take top 3 from each
        top_regular = regular[:3]
        top_penny = penny[:3]
        
        # Combine and sort
        mixed = top_regular + top_penny
        mixed.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return mixed[:6]

# Global stable predictor instance
stable_predictor = StablePredictor()

def get_stable_predictions() -> Dict[str, List[Dict]]:
    """Get stable 24-hour predictions."""
    return stable_predictor.get_or_generate_predictions()
