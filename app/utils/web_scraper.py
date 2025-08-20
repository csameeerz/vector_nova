import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebScraper:
    """Utility for web scraping and content extraction"""
    
    def __init__(self, max_depth: int = 2, max_pages: int = 100):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls = set()
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single URL and extract content"""
        try:
            if url in self.visited_urls:
                return None
            
            self.visited_urls.add(url)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: status {response.status}")
                    return None
                
                content = await response.text()
                
                # Parse HTML
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract content
                extracted_data = {
                    'url': url,
                    'title': self._extract_title(soup),
                    'text': self._extract_text(soup),
                    'links': self._extract_links(soup, url),
                    'metadata': self._extract_metadata(soup),
                    'timestamp': asyncio.get_event_loop().time()
                }
                
                logger.info(f"Successfully scraped {url}")
                return extracted_data
                
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return None
    
    async def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        """Crawl a website starting from a given URL"""
        try:
            scraped_pages = []
            urls_to_visit = [start_url]
            current_depth = 0
            
            while urls_to_visit and len(scraped_pages) < self.max_pages and current_depth < self.max_depth:
                current_urls = urls_to_visit.copy()
                urls_to_visit = []
                
                for url in current_urls:
                    if len(scraped_pages) >= self.max_pages:
                        break
                    
                    page_data = await self.scrape_url(url)
                    if page_data:
                        scraped_pages.append(page_data)
                        
                        # Add new links to visit (only for first level)
                        if current_depth == 0:
                            for link in page_data['links']:
                                if link not in self.visited_urls and self._should_crawl(link, start_url):
                                    urls_to_visit.append(link)
                
                current_depth += 1
            
            logger.info(f"Crawled {len(scraped_pages)} pages from {start_url}")
            return scraped_pages
            
        except Exception as e:
            logger.error(f"Website crawling failed: {str(e)}")
            return []
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return ""
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text from main content areas
        main_content = ""
        
        # Try to find main content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '#content',
            '#main',
            '.post-content',
            '.entry-content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                main_content = content.get_text()
                break
        
        # If no main content found, get all text
        if not main_content:
            main_content = soup.get_text()
        
        # Clean up text
        text = re.sub(r'\s+', ' ', main_content)
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Only include HTTP/HTTPS URLs
            if absolute_url.startswith(('http://', 'https://')):
                links.append(absolute_url)
        
        return list(set(links))  # Remove duplicates
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the page"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Open Graph tags
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content')
            if property_name and content:
                metadata[f'og_{property_name}'] = content
        
        return metadata
    
    def _should_crawl(self, url: str, base_url: str) -> bool:
        """Determine if a URL should be crawled"""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Only crawl same domain
            if parsed_url.netloc != parsed_base.netloc:
                return False
            
            # Skip certain file types
            skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip certain URL patterns
            skip_patterns = [
                r'/admin',
                r'/login',
                r'/logout',
                r'/api/',
                r'#',
                r'\?',
                r'/search'
            ]
            
            for pattern in skip_patterns:
                if re.search(pattern, url):
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def extract_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract article content specifically"""
        try:
            page_data = await self.scrape_url(url)
            if not page_data:
                return None
            
            # Try to extract article-specific content
            soup = BeautifulSoup(page_data.get('content', ''), 'html.parser')
            
            article_data = {
                'url': url,
                'title': page_data['title'],
                'content': self._extract_article_text(soup),
                'author': self._extract_author(soup),
                'published_date': self._extract_published_date(soup),
                'metadata': page_data['metadata']
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"Article extraction failed for {url}: {str(e)}")
            return None
    
    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        """Extract article text content"""
        # Look for article-specific selectors
        article_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.story-content',
            '.article-body'
        ]
        
        for selector in article_selectors:
            content = soup.select_one(selector)
            if content:
                return self._extract_text(BeautifulSoup(str(content), 'html.parser'))
        
        # Fallback to general text extraction
        return self._extract_text(soup)
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        author_selectors = [
            '.author',
            '.byline',
            '[rel="author"]',
            '.post-author',
            '.article-author'
        ]
        
        for selector in author_selectors:
            author = soup.select_one(selector)
            if author:
                return author.get_text().strip()
        
        return ""
    
    def _extract_published_date(self, soup: BeautifulSoup) -> str:
        """Extract article published date"""
        date_selectors = [
            '.published-date',
            '.post-date',
            '.article-date',
            'time',
            '[datetime]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                return date_elem.get('datetime') or date_elem.get_text().strip()
        
        return ""
