from googlesearch import search
import requests
from bs4 import BeautifulSoup

# Define the search query
query = "Python web scraping site:geeksforgeeks.org"

# Get search results (only top 3 to avoid too many requests)
links = [url for url in search(query, num_results=2)]

# Function to extract text from a webpage
def extract_text(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text (modify tag selection if needed)
        paragraphs = soup.find_all("p")
        text = "\n".join([para.get_text() for para in paragraphs])

        return text[:1000]  # Limiting to first 1000 characters for readability
    except Exception as e:
        return f"Error extracting {url}: {e}"

# Loop through search results and extract text
for link in links:
    print(f"\nExtracting from: {link}\n")
    print(extract_text(link))