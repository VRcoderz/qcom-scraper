#!/usr/bin/env python3
"""
Quick Commerce Industry News Scraper
Collects news articles about quick commerce, q-commerce, and ultra-fast delivery
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re
import os
from typing import List, Dict, Optional
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickCommerceNewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Enhanced quick commerce related keywords for Indian market
        self.keywords = [
            'quick commerce', 'q-commerce', 'quick-commerce', 'qcommerce',
            'blinkit', 'zepto', 'swiggy instamart', 'instamart', 'swiggy instant',
            'amazon now', 'flipkart minutes', 'myntra rapid', 'bigbasket now',
            'dunzo', 'grofers', 'milk basket', 'nature\'s basket express',
            'fresh to home instant', 'licious express', 'country delight rapid',
            'gopuff', 'getir', 'gorillas', 'flink', 'jokr', 'weezy',
            'ultra fast delivery', '10 minute delivery', '15 minute delivery', '30 minute delivery',
            'instant grocery', 'instant delivery', 'rapid delivery', 'express delivery',
            'dark store', 'dark stores', 'micro fulfillment', 'micro-fulfillment',
            'on-demand delivery', 'hyperlocal delivery', 'last mile delivery',
            'grocery delivery', 'food delivery instant', 'medicine delivery instant',
            'delivery hero', 'talabat', 'foodpanda instant', 'ubereats instant',
            'gojek instant', 'grab instant', 'ola instant', 'rapido instant'
        ]
        
        # News sources with RSS feeds and search URLs
        self.news_sources = {
            'TechCrunch': {
                'search_url': 'https://search.techcrunch.com/search?query={}&order=new',
                'base_url': 'https://techcrunch.com'
            },
            'Bloomberg': {
                'search_url': 'https://www.bloomberg.com/search?query={}&sort=time:desc',
                'base_url': 'https://www.bloomberg.com'
            },
            'Reuters': {
                'search_url': 'https://www.reuters.com/site-search/?query={}',
                'base_url': 'https://www.reuters.com'
            },
            'Business Standard': {
                'search_url': 'https://www.business-standard.com/search?q={}',
                'base_url': 'https://www.business-standard.com'
            },
            'Economic Times': {
                'search_url': 'https://economictimes.indiatimes.com/searchresult.cms?query={}',
                'base_url': 'https://economictimes.indiatimes.com'
            },
            'YourStory': {
                'search_url': 'https://yourstory.com/search?q={}',
                'base_url': 'https://yourstory.com'
            },
            'MediaNama': {
                'search_url': 'https://www.medianama.com/?s={}',
                'base_url': 'https://www.medianama.com'
            }
        }
        
        # Google News RSS for quick commerce
        self.google_news_rss = "https://news.google.com/rss/search?q=quick+commerce+OR+q-commerce+OR+blinkit+OR+zepto+OR+instamart&hl=en-US&gl=US&ceid=US:en"

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]"\'/@#$%&*+=<>{}|\\`~]', '', text)
        return text

    def extract_article_content(self, url: str) -> Dict[str, str]:
        """Extract full article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()
            
            # Try to find article title
            title = ""
            for selector in ['h1', 'title', '.headline', '.article-title', '.entry-title']:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    break
            
            # Try to find article content
            content = ""
            content_selectors = [
                'article', '.article-content', '.entry-content', '.post-content',
                '.article-body', '.story-body', '.content', '.main-content',
                '[data-module="ArticleBody"]', '.article-wrap'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Get all paragraph text
                    paragraphs = content_elem.find_all(['p', 'div'], string=True)
                    content_text = []
                    for p in paragraphs:
                        text = self.clean_text(p.get_text())
                        if len(text) > 50:  # Only include substantial paragraphs
                            content_text.append(text)
                    content = '\n\n'.join(content_text)
                    break
            
            # Fallback: get all paragraph text from the page
            if not content:
                paragraphs = soup.find_all('p')
                content_text = []
                for p in paragraphs:
                    text = self.clean_text(p.get_text())
                    if len(text) > 50:
                        content_text.append(text)
                content = '\n\n'.join(content_text[:10])  # Limit to first 10 paragraphs
            
            return {
                'title': title or 'No title found',
                'content': content or 'No content extracted',
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return {
                'title': 'Error extracting title',
                'content': f'Error extracting content: {str(e)}',
                'url': url
            }

    def search_google_news(self) -> List[Dict[str, str]]:
        """Search Google News RSS for quick commerce articles"""
        articles = []
        try:
            response = self.session.get(self.google_news_rss, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items[:20]:  # Limit to 20 most recent articles
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                description = item.find('description')
                
                if title and link:
                    article_data = {
                        'title': self.clean_text(title.get_text()),
                        'url': link.get_text(),
                        'source': 'Google News',
                        'published_date': pub_date.get_text() if pub_date else '',
                        'description': self.clean_text(description.get_text()) if description else ''
                    }
                    
                    # Extract full content
                    full_content = self.extract_article_content(article_data['url'])
                    article_data['content'] = full_content['content']
                    
                    articles.append(article_data)
                    
                    # Rate limiting
                    time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error searching Google News: {str(e)}")
        
        return articles

    def search_news_api(self, query: str, days_back: int = 7) -> List[Dict[str, str]]:
        """Search using NewsAPI (requires API key)"""
        articles = []
        api_key = os.getenv('NEWS_API_KEY')
        
        if not api_key:
            logger.warning("NEWS_API_KEY not found in environment variables")
            return articles
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            url = f"https://newsapi.org/v2/everything"
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': api_key,
                'pageSize': 50
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            for article in data.get('articles', []):
                if article.get('url'):
                    article_data = {
                        'title': self.clean_text(article.get('title', '')),
                        'url': article.get('url'),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_date': article.get('publishedAt', ''),
                        'description': self.clean_text(article.get('description', ''))
                    }
                    
                    # Extract full content
                    full_content = self.extract_article_content(article_data['url'])
                    article_data['content'] = full_content['content']
                    
                    articles.append(article_data)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
        except Exception as e:
            logger.error(f"Error with NewsAPI: {str(e)}")
        
        return articles

    def scrape_all_news(self, days_back: int = 7) -> List[Dict[str, str]]:
        """Main method to scrape all news sources"""
        all_articles = []
        
        # Search Google News RSS
        logger.info("Searching Google News RSS...")
        google_articles = self.search_google_news()
        all_articles.extend(google_articles)
        logger.info(f"Found {len(google_articles)} articles from Google News")
        
        # Search using NewsAPI if available
        logger.info("Searching NewsAPI...")
        for keyword in ['quick commerce', 'blinkit', 'zepto', 'swiggy instamart']:
            news_api_articles = self.search_news_api(keyword, days_back)
            all_articles.extend(news_api_articles)
            time.sleep(2)  # Rate limiting
        
        logger.info(f"Found {len([a for a in all_articles if a.get('source') != 'Google News'])} articles from NewsAPI")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"Total unique articles found: {len(unique_articles)}")
        return unique_articles

    def save_to_text_file(self, articles: List[Dict[str, str]], filename: str = None):
        """Save articles to a text file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quick_commerce_news_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("QUICK COMMERCE INDUSTRY NEWS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total articles: {len(articles)}\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"ARTICLE {i}\n")
                f.write(f"{'='*80}\n\n")
                f.write(f"TITLE: {article.get('title', 'No title')}\n\n")
                f.write(f"SOURCE: {article.get('source', 'Unknown')}\n\n")
                f.write(f"URL: {article.get('url', '')}\n\n")
                f.write(f"PUBLISHED: {article.get('published_date', 'Unknown')}\n\n")
                
                if article.get('description'):
                    f.write(f"DESCRIPTION:\n{article['description']}\n\n")
                
                f.write(f"FULL CONTENT:\n")
                f.write("-" * 40 + "\n")
                f.write(f"{article.get('content', 'No content available')}\n")
                f.write("-" * 40 + "\n\n")
        
        logger.info(f"Articles saved to {filename}")
        return filename

    def save_to_json(self, articles: List[Dict[str, str]], filename: str = None):
        """Save articles to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quick_commerce_news_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_articles': len(articles),
                'articles': articles
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Articles saved to {filename}")
        return filename

    def save_to_text_file(self, articles: List[Dict[str, str]], filename: str = None):
        """Save articles to a text file with timeframe info"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timeframe_label = self.timeframe.replace('h', 'hours').replace('d', 'days')
            filename = f"quick_commerce_news_{timeframe_label}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("QUICK COMMERCE INDUSTRY NEWS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Timeframe: {self.timeframe_options[self.timeframe]['description']}\n")
            f.write(f"Date range: {self.start_date.strftime('%Y-%m-%d %H:%M')} to {self.end_date.strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total articles: {len(articles)}\n\n")
            
            # Group articles by source for better organization
            from collections import defaultdict
            articles_by_source = defaultdict(list)
            for article in articles:
                articles_by_source[article.get('source', 'Unknown')].append(article)
            
            f.write("ARTICLES BY SOURCE:\n")
            for source, source_articles in articles_by_source.items():
                f.write(f"• {source}: {len(source_articles)} articles\n")
            f.write("\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"ARTICLE {i}\n")
                f.write(f"{'='*80}\n\n")
                f.write(f"TITLE: {article.get('title', 'No title')}\n\n")
                f.write(f"SOURCE: {article.get('source', 'Unknown')}\n\n")
                f.write(f"URL: {article.get('url', '')}\n\n")
                f.write(f"PUBLISHED: {article.get('published_date', 'Unknown')}\n\n")
                
                if article.get('description'):
                    f.write(f"DESCRIPTION:\n{article['description']}\n\n")
                
                f.write(f"FULL CONTENT:\n")
                f.write("-" * 40 + "\n")
                f.write(f"{article.get('content', 'No content available')}\n")
                f.write("-" * 40 + "\n\n")
        
        logger.info(f"Articles saved to {filename}")
        return filename

    def save_to_json(self, articles: List[Dict[str, str]], filename: str = None):
        """Save articles to JSON file with timeframe info"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timeframe_label = self.timeframe.replace('h', 'hours').replace('d', 'days')
            filename = f"quick_commerce_news_{timeframe_label}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timeframe': self.timeframe_options[self.timeframe]['description'],
                'date_range': {
                    'start': self.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': self.end_date.strftime('%Y-%m-%d %H:%M:%S')
                },
                'total_articles': len(articles),
                'articles': articles
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Articles saved to {filename}")
        return filename

def parse_timeframe_argument():
    """Parse timeframe from command line arguments or environment variables"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Commerce News Scraper')
    parser.add_argument(
        '--timeframe', '-t',
        choices=['6h', '12h', '24h', '2d', '3d', '7d', '14d', '30d', '60d', '90d', 'custom'],
        default=os.getenv('SCRAPE_TIMEFRAME', '7d'),
        help='Timeframe for news scraping (default: 7d)'
    )
    parser.add_argument(
        '--custom-days',
        type=int,
        default=int(os.getenv('CUSTOM_DAYS_BACK', 7)),
        help='Number of days for custom timeframe (default: 7)'
    )
    parser.add_argument(
        '--list-timeframes',
        action='store_true',
        help='List all available timeframe options'
    )
    
    args = parser.parse_args()
    
    if args.list_timeframes:
        print("Available timeframe options:")
        scraper = QuickCommerceNewsScraper()
        for code, info in scraper.timeframe_options.items():
            print(f"  {code:6} - {info['description']}")
        exit(0)
    
    # Set custom days if using custom timeframe
    if args.timeframe == 'custom':
        os.environ['CUSTOM_DAYS_BACK'] = str(args.custom_days)
    
    return args.timeframe

def main():
    """Main function to run the scraper with timeframe selection"""
    
    # Parse timeframe from arguments or environment
    timeframe = parse_timeframe_argument()
    
    scraper = QuickCommerceNewsScraper(timeframe=timeframe)
    
    logger.info(f"Starting quick commerce news scraping...")
    logger.info(f"Timeframe: {scraper.timeframe_options[timeframe]['description']}")
    
    try:
        # Scrape all news
        articles = scraper.scrape_all_news()
        
        if articles:
            # Save to text file (main requirement)
            text_filename = scraper.save_to_text_file(articles)
            
            # Also save to JSON for structured data
            json_filename = scraper.save_to_json(articles)
            
            print(f"\n✅ Successfully scraped {len(articles)} articles!")
            print(f"📅 Timeframe: {scraper.timeframe_options[timeframe]['description']}")
            print(f"📄 Text file: {text_filename}")
            print(f"📊 JSON file: {json_filename}")
            
        else:
            logger.warning("No articles found for the specified timeframe")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
