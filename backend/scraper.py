import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import re


def validate_wikipedia_url(url: str) -> tuple[bool, str]:
    """Validate if the URL is a valid Wikipedia URL."""
    try:
        parsed = urlparse(url)
        # Check if it's a Wikipedia domain
        if 'wikipedia.org' not in parsed.netloc:
            return False, "Please provide a valid Wikipedia URL (e.g., https://en.wikipedia.org/wiki/Article_Name)"
        
        # Check if it has a wiki path
        if not parsed.path.startswith('/wiki/'):
            return False, "Invalid Wikipedia URL format. It should be: https://en.wikipedia.org/wiki/Article_Name"
        
        return True, ""
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def normalize_wikipedia_url(url: str) -> str:
    """Normalize Wikipedia URL (handle spaces, URL encode)."""
    parsed = urlparse(url)
    # Replace spaces with underscores in the path (Wikipedia convention)
    path_parts = parsed.path.split('/')
    if len(path_parts) >= 3 and path_parts[1] == 'wiki':
        # Get the article name
        article_name = '/'.join(path_parts[2:])
        # Replace spaces with underscores (Wikipedia uses underscores, not %20)
        article_name = article_name.replace(' ', '_')
        # Remove multiple consecutive underscores
        article_name = re.sub(r'_+', '_', article_name)
        # Remove leading/trailing underscores
        article_name = article_name.strip('_')
        path_parts[2] = article_name
        parsed = parsed._replace(path='/'.join(path_parts[:2]) + '/' + article_name)
    return urlunparse(parsed)


def scrape_wikipedia(url: str) -> tuple[str, str]:
    """Fetch a Wikipedia article and return (title, clean_text).

    This function aims to extract the main article paragraphs while removing
    reference superscripts, tables and non-content elements.
    """
    # Validate URL
    is_valid, error_msg = validate_wikipedia_url(url)
    if not is_valid:
        raise ValueError(error_msg)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Normalize URL
    normalized_url = normalize_wikipedia_url(url)
    
    try:
        resp = requests.get(normalized_url, headers=headers, timeout=15, allow_redirects=True)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Wikipedia: {str(e)}")
    
    # Check for 404
    if resp.status_code == 404:
        # Try to extract article name for better error message
        article_name = urlparse(normalized_url).path.split('/wiki/')[-1] if '/wiki/' in normalized_url else 'unknown'
        raise ValueError(
            f"Wikipedia article not found: '{article_name}'. "
            f"Please check the URL spelling. Common issues:\n"
            f"• Typos in the article name (e.g., 'kohili' should be 'Kohli')\n"
            f"• Missing capital letters (Wikipedia is case-sensitive)\n"
            f"• Article doesn't exist\n\n"
            f"Try searching for the correct article name on Wikipedia first."
        )
    
    # Check for other HTTP errors
    if resp.status_code != 200:
        raise ValueError(f"Wikipedia returned error {resp.status_code}: {resp.reason}")
    
    # Check if we were redirected (Wikipedia often redirects to the correct article)
    if resp.url != normalized_url:
        # This is fine, Wikipedia redirected us to the correct article
        # no-op: keep original behavior but provide a valid block for Python
        pass
    
    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title_tag = soup.find("h1", id="firstHeading")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Main content area
    content = soup.find(id="mw-content-text") or soup.find("#content")
    if not content:
        # fallback: use body
        content = soup

    # Remove tables, infoboxes, navboxes, and reference lists
    for selector in content.find_all(["table", "sup", "aside", "style", "script"]):
        selector.decompose()

    # Extract text from paragraphs
    paragraphs = content.find_all("p")
    text_parts = []
    for p in paragraphs:
        txt = p.get_text(strip=True)
        if txt and len(txt) > 20:  # Filter out very short paragraphs
            text_parts.append(txt)
    
    if not text_parts:
        raise ValueError("Could not extract content from the Wikipedia article. The page might be empty or have a different structure.")
    
    clean_text = "\n\n".join(text_parts)
    
    if len(clean_text) < 100:
        raise ValueError("The Wikipedia article is too short to generate a quiz. Please try a more detailed article.")
    
    return title, clean_text
