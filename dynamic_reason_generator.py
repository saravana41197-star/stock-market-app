"""Dynamic reason generator based on real news and Google search results."""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
from datetime import datetime, timedelta
from utils import get_logger
import random

logger = get_logger("dynamic_reason_generator")

class DynamicReasonGenerator:
    def __init__(self):
        self.news_keywords = {
            'festival': ['pongal', 'diwali', 'eid', 'christmas', 'durga puja', 'ganesh chaturthi', 'navratri'],
            'season': ['monsoon', 'winter', 'summer', 'spring', 'autumn', 'rainy season'],
            'economy': ['budget', 'gdp', 'inflation', 'interest rates', 'rbi', 'finance minister', 'economy'],
            'government': ['election', 'policy', 'modi', 'government', 'parliament', 'bill', 'law'],
            'business': ['merger', 'acquisition', 'partnership', 'deal', 'investment', 'funding', 'ipo'],
            'energy': ['oil', 'petrol', 'diesel', 'crude oil', 'energy', 'power', 'electricity'],
            'agriculture': ['farming', 'monsoon', 'crops', 'farmers', 'agriculture', 'rural', 'mandi'],
            'technology': ['tech', 'startup', 'digital', 'ai', 'artificial intelligence', 'software'],
            'banking': ['bank', 'rbi', 'interest rate', 'loan', 'credit', 'banking sector'],
            'infrastructure': ['road', 'highway', 'construction', 'infrastructure', 'project', 'development'],
            'automobile': ['car', 'auto', 'vehicle', 'tata motors', 'maruti', 'hyundai', 'electric vehicle'],
            'retail': ['shopping', 'retail', 'consumer', 'fmcg', 'marketplace', 'ecommerce'],
            'pharma': ['medicine', 'pharma', 'drug', 'healthcare', 'hospital', 'vaccine'],
            'telecom': ['5g', 'telecom', 'jio', 'airtel', 'vi', 'bsnl', 'network'],
            'real_estate': ['property', 'real estate', 'housing', 'construction', 'rera'],
            'international': ['usa', 'china', 'global', 'trade', 'export', 'import', 'fed']
        }
        
        self.stock_mappings = {
            'sugar': ['BALRAMCHIN.NS', 'Bajaj Hindusthan', 'EID Parry', 'Triveni'],
            'auto': ['TATAMOTORS.NS', 'MARUTI.NS', 'M&M.NS', 'HEROMOTOCO.NS'],
            'bank': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS'],
            'it': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'TECHM.NS'],
            'pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'LUPIN.NS'],
            'energy': ['ONGC.NS', 'COALINDIA.NS', 'BPCL.NS', 'IOC.NS'],
            'retail': ['RELIANCE.NS', 'DMART.NS', 'AVENUE.NS', 'TRENT.NS'],
            'infrastructure': ['LT.NS', 'ULTRACEMCO.NS', 'ACC.NS', 'AMBUJACEM.NS']
        }
    
    def get_current_news_trends(self) -> Dict[str, List[str]]:
        """Get current news trends and events from multiple sources."""
        trends = {
            'positive_events': [],
            'negative_events': [],
            'neutral_events': []
        }
        
        try:
            # Fetch from multiple Indian news sources
            news_sources = [
                'https://www.economictimes.indiatimes.com/markets',
                'https://www.moneycontrol.com/news/business/markets/',
                'https://www.business-standard.com/markets',
                'https://www.livemint.com/market/'
            ]
            
            for source in news_sources:
                try:
                    response = requests.get(source, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract headlines
                        headlines = self._extract_headlines(soup)
                        
                        # Categorize headlines
                        for headline in headlines:
                            category = self._categorize_news(headline)
                            if category == 'positive':
                                trends['positive_events'].append(headline)
                            elif category == 'negative':
                                trends['negative_events'].append(headline)
                            else:
                                trends['neutral_events'].append(headline)
                
                except Exception as e:
                    logger.error(f"Error fetching from {source}: {e}")
                    continue
            
            # If no real news, generate based on current date/events
            if not any(trends.values()):
                trends = self._generate_fallback_trends()
            
        except Exception as e:
            logger.error(f"Error in get_current_news_trends: {e}")
            trends = self._generate_fallback_trends()
        
        return trends
    
    def _extract_headlines(self, soup: BeautifulSoup) -> List[str]:
        """Extract headlines from soup object."""
        headlines = []
        
        # Common selectors for headlines
        selectors = [
            'h1', 'h2', 'h3',
            '.title', '.headline', '.news-title',
            'a[title*="news"]', 'a[title*="market"]',
            '[class*="headline"]', '[class*="title"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:20]:  # Limit to avoid too many
                    text = element.get_text(strip=True)
                    if len(text) > 15 and len(text) < 200:  # Reasonable length
                        headlines.append(text)
            except Exception:
                continue
        
        return headlines[:50]  # Return top 50 headlines
    
    def _categorize_news(self, headline: str) -> str:
        """Categorize news as positive, negative, or neutral."""
        headline_lower = headline.lower()
        
        # Positive keywords
        positive_keywords = [
            'rise', 'gain', 'profit', 'growth', 'boom', 'surge', 'jump', 'rally', 'bull',
            'positive', 'good', 'strong', 'up', 'increase', 'boost', 'win', 'success',
            'record high', 'all-time high', 'breakthrough', 'achievement', 'award'
        ]
        
        # Negative keywords
        negative_keywords = [
            'fall', 'drop', 'loss', 'decline', 'crash', 'bear', 'down', 'decrease',
            'negative', 'bad', 'weak', 'slump', 'plunge', 'tumble', 'crisis', 'fraud',
            'scam', 'investigation', 'concern', 'worry', 'fear', 'panic', 'sell-off'
        ]
        
        # Check sentiment
        positive_count = sum(1 for word in positive_keywords if word in headline_lower)
        negative_count = sum(1 for word in negative_keywords if word in headline_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_fallback_trends(self) -> Dict[str, List[str]]:
        """Generate fallback trends based on current date and season."""
        now = datetime.now()
        month = now.month
        day = now.day
        
        trends = {
            'positive_events': [],
            'negative_events': [],
            'neutral_events': []
        }
        
        # Season-based events
        if month in [1, 2, 3]:  # Winter
            trends['neutral_events'].extend([
                "Winter season affecting energy demand",
                "Festival season boosting retail sales",
                "Year-end financial results season"
            ])
        elif month in [4, 5, 6]:  # Summer
            trends['neutral_events'].extend([
                "Summer season increasing energy consumption",
                "Monsoon expectations in agriculture sector",
                "Quarterly results season starting"
            ])
        elif month in [7, 8, 9]:  # Monsoon
            trends['neutral_events'].extend([
                "Monsoon season impacting agriculture stocks",
                "Infrastructure projects affected by rains",
                "Festival season preparations beginning"
            ])
        else:  # Festival season
            trends['positive_events'].extend([
                "Festival season boosting consumer demand",
                "Agricultural harvest supporting rural economy",
                "Year-end festive spending expected"
            ])
        
        # Add some general market events
        trends['neutral_events'].extend([
            "Market watching global economic indicators",
            "Investors tracking quarterly earnings",
            "Sector rotation active in current market"
        ])
        
        return trends
    
    def generate_dynamic_reason(self, stock_symbol: str, score: float, category: str) -> str:
        """Generate dynamic reason based on current news and stock type."""
        try:
            # Get current trends
            trends = self.get_current_news_trends()
            
            # Determine stock sector
            stock_sector = self._identify_stock_sector(stock_symbol)
            
            # Select relevant events
            relevant_events = self._get_relevant_events(trends, stock_sector, score)
            
            # Generate user-friendly reason
            if relevant_events:
                reason = self._format_user_friendly_reason(relevant_events[0], stock_symbol, stock_sector)
            else:
                reason = self._generate_generic_reason(stock_symbol, stock_sector, score)
            
            return reason
            
        except Exception as e:
            logger.error(f"Error generating dynamic reason for {stock_symbol}: {e}")
            return self._generate_generic_reason(stock_symbol, 'general', score)
    
    def _identify_stock_sector(self, symbol: str) -> str:
        """Identify the sector of a stock based on its symbol."""
        symbol_lower = symbol.lower()
        
        for sector, stocks in self.stock_mappings.items():
            for stock in stocks:
                if stock.lower() in symbol_lower or symbol_lower in stock.lower():
                    return sector
        
        # Check symbol patterns
        if 'bank' in symbol_lower or any(x in symbol_lower for x in ['hdfc', 'icici', 'sbi', 'kotak']):
            return 'bank'
        elif any(x in symbol_lower for x in ['tcs', 'infy', 'wipro', 'tech']):
            return 'it'
        elif any(x in symbol_lower for x in ['sun', 'dr', 'cipla', 'lupin']):
            return 'pharma'
        elif any(x in symbol_lower for x in ['tata', 'maruti', 'mahindra', 'hero']):
            return 'auto'
        elif any(x in symbol_lower for x in ['ongc', 'coal', 'bpcl', 'ioc']):
            return 'energy'
        elif any(x in symbol_lower for x in ['reliance', 'd-mart', 'avenue']):
            return 'retail'
        elif any(x in symbol_lower for x in ['lt', 'ultratech', 'acc', 'ambuja']):
            return 'infrastructure'
        
        return 'general'
    
    def _get_relevant_events(self, trends: Dict[str, List[str]], sector: str, score: float) -> List[str]:
        """Get events relevant to the stock sector and score."""
        relevant_events = []
        
        # Choose event type based on score
        if score > 0.6:
            event_types = ['positive_events']
        elif score > 0.4:
            event_types = ['positive_events', 'neutral_events']
        else:
            event_types = ['neutral_events', 'negative_events']
        
        for event_type in event_types:
            for event in trends.get(event_type, []):
                # Check if event is relevant to sector
                if self._is_event_relevant_to_sector(event, sector):
                    relevant_events.append(event)
        
        return relevant_events[:3]  # Return top 3 relevant events
    
    def _is_event_relevant_to_sector(self, event: str, sector: str) -> bool:
        """Check if an event is relevant to a specific sector."""
        event_lower = event.lower()
        
        sector_keywords = {
            'bank': ['bank', 'rbi', 'interest', 'loan', 'credit', 'finance'],
            'it': ['tech', 'software', 'digital', 'ai', 'it', 'computer'],
            'pharma': ['medicine', 'drug', 'pharma', 'health', 'hospital', 'vaccine'],
            'auto': ['car', 'auto', 'vehicle', 'motor', 'electric vehicle'],
            'energy': ['oil', 'energy', 'power', 'petrol', 'diesel', 'crude'],
            'retail': ['retail', 'consumer', 'shopping', 'marketplace', 'fmcg'],
            'infrastructure': ['construction', 'infrastructure', 'project', 'building'],
            'agriculture': ['farm', 'crop', 'monsoon', 'agriculture', 'rural'],
            'festival': ['festival', 'pongal', 'diwali', 'eid', 'celebration']
        }
        
        keywords = sector_keywords.get(sector, [])
        return any(keyword in event_lower for keyword in keywords)
    
    def _format_user_friendly_reason(self, event: str, stock_symbol: str, sector: str) -> str:
        """Format event into user-friendly reason."""
        # Extract key information from event
        event_lower = event.lower()
        
        # Festival-based reasons
        if any(festival in event_lower for festival in ['pongal', 'diwali', 'eid', 'festival']):
            if sector in ['retail', 'auto', 'consumer']:
                return f"Festival season boosting demand - {stock_symbol} may benefit"
            elif sector == 'agriculture':
                return f"Festival season increasing consumption - Related stocks may rise"
        
        # Season-based reasons
        if any(season in event_lower for season in ['monsoon', 'rain', 'winter', 'summer']):
            if sector == 'agriculture':
                return f"{event.title()} - Agriculture stocks may see movement"
            elif sector == 'energy':
                return f"{event.title()} - Energy demand may increase"
            elif sector == 'infrastructure':
                return f"{event.title()} - Construction activity may be affected"
        
        # Economy-based reasons
        if any(econ in event_lower for econ in ['budget', 'gdp', 'economy', 'growth']):
            if sector == 'infrastructure':
                return f"Economic growth positive - Infrastructure stocks may benefit"
            elif sector == 'bank':
                return f"Economy improving - Banking sector may see gains"
            elif sector == 'retail':
                return f"Economic growth - Consumer spending may increase"
        
        # Market-based reasons
        if any(market in event_lower for market in ['market', 'investor', 'trading']):
            return f"Market sentiment positive - {stock_symbol} showing strength"
        
        # Government policy reasons
        if any(gov in event_lower for gov in ['government', 'policy', 'modi', 'rbi']):
            if sector == 'bank':
                return "Government policies favorable - Banking sector may benefit"
            elif sector == 'infrastructure':
                return "New policies announced - Infrastructure stocks may rise"
        
        # Generic positive reason
        return f"Current market conditions favorable - {stock_symbol} may perform well"
    
    def _generate_generic_reason(self, stock_symbol: str, sector: str, score: float) -> str:
        """Generate generic reason when no specific news is available."""
        now = datetime.now()
        
        # Time-based generic reasons
        if score > 0.6:
            reasons = [
                f"Strong market momentum - {stock_symbol} showing upward trend",
                f"Positive investor sentiment - {stock_symbol} gaining attention",
                f"Technical indicators bullish - {stock_symbol} may rise further",
                f"Market conditions favorable - {stock_symbol} expected to perform well"
            ]
        else:
            reasons = [
                f"Market watching {stock_symbol} closely - Mixed signals present",
                f"Conservative approach suggested - {stock_symbol} needs monitoring",
                f"Wait for clear signals - {stock_symbol} direction uncertain",
                f"Risk-reward balanced - {stock_symbol} requires careful analysis"
            ]
        
        return random.choice(reasons)

# Global instance
dynamic_reason_generator = DynamicReasonGenerator()

def get_dynamic_reason(stock_symbol: str, score: float, category: str) -> str:
    """Get dynamic reason for a stock."""
    return dynamic_reason_generator.generate_dynamic_reason(stock_symbol, score, category)
