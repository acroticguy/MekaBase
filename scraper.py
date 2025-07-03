import requests
from bs4 import BeautifulSoup
from scraper_tools import GeminiClient
import pandas as pd
import time

def get_all_wiki_pages(wiki_url):
    """
    Scrapes all page links from a MediaWiki's "All Pages" page.

    Args:
        wiki_url (str): The base URL of the wiki.

    Returns:
        list: A list of full URLs to all pages on the wiki.
    """
    all_pages_url = f"{wiki_url}/wiki/Special:AllPages"
    page_links = set()

    while all_pages_url:
        try:
            response = requests.get(all_pages_url)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {all_pages_url}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all page links in the main content area
        # In MediaWiki, these are typically in a div with the class 'mw-allpages-body'
        content = soup.find('div', class_='mw-allpages-body')
        if content:
            for a_tag in content.find_all('a', href=True):
                page_title = a_tag['title']
                page_url = f"{wiki_url}{a_tag['href']}"
                page_links.add(page_url)
                print(f"Found page: {page_title} - {page_url}")


        # Find the "Next page" link to handle pagination
        next_page_link = soup.find('div', class_='mw-allpages-nav').find('a')
        if next_page_link and next_page_link['href'] and 'Next page' in next_page_link.text:
            all_pages_url = f"{wiki_url}{next_page_link['href']}"
        else:
            all_pages_url = None # No more pages

    return page_links

def scrape_wiki_pages(urls):
    """
    Scrapes a list of wiki pages and returns a list of dictionaries
    containing the title, text content, and title of each page.

    Args:
        urls: A list of URLs to scrape.

    Returns:
        A list of dictionaries, where each dictionary has the
        following format: {'title': title_text, 'text': all_text, 'page': page_name}
    """

    pages_data = []
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')

            soup = soup.find('div', id='innerbodycontent') if soup else None
            title = soup.find('h1', id='firstHeading').get_text()

            content_div = soup.find('div', id='mw-content-text')
            titles =  [title.get_text() for title in content_div.find_all('h2')] if content_div else []
            titles.insert(0, title)  # Include the main title as the first item
            text = content_div.get_text(strip=True) if content_div else ''

            client = GeminiClient()
            res = client.generate_chunks(soup.text, titles)
            for chunk in res:
                chunk['page'] = title

            #add all responses to pages_data
            pages_data.extend(res)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except AttributeError as e:
            print(f"Error parsing {url}: {e}. Check if the page structure is as expected.")

        time.sleep(5)  # Be polite and avoid overwhelming the server with requests
    return pages_data

if __name__ == "__main__":
    mekanism_wiki_url = "https://wiki.aidancbrady.com"
    all_pages = get_all_wiki_pages(mekanism_wiki_url)
    print(f"\nFound a total of {len(all_pages)} pages.")

    # Scrape the pages and get the data
    scraped_data = scrape_wiki_pages(all_pages)
    # Save all scraped data to a CSV file
    df = pd.DataFrame(scraped_data)
    print(df.head())  # Display the first few rows of the DataFrame
    df.to_csv('scraped_wiki_data.csv', index=True)