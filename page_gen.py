import requests
from bs4 import BeautifulSoup
import markdown2
import os
from duckduckgo_search import DDGS

def scrape_chess_openings(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    openings = []
    for link in soup.select('#cb-container a'):
        name = link.text.strip()
        href = link['href']
        img_tag = link.find_next('img')
        img_url = img_tag['src'] if img_tag else ""
        openings.append({"name": name, "url": url + href, "image": img_url})
    
    return openings

def search_additional_info(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
        return results[0]['body'] if results else "No additional information found."

def generate_markdown(openings):
    content = "# Chess Openings\n\n"
    for opening in openings:
        description = search_additional_info(opening['name'] + " chess opening")
        img_md = f'![{opening["name"]}]({opening["image"]})' if opening['image'] else ""
        content += f"## {opening['name']}\n\n{img_md}\n\n[More info]({opening['url']})\n\n{description}\n\n"
    
    return content

def save_markdown(content, filename='chess_openings.md'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_html_from_markdown(md_file, html_file='index.html'):
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_content = markdown2.markdown(md_content)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(f"""<html><head><title>Chess Openings</title></head><body>{html_content}</body></html>""")

def main():
    url = "https://www.thechesswebsite.com/chess-openings/"
    openings = scrape_chess_openings(url)
    md_content = generate_markdown(openings)
    save_markdown(md_content)
    generate_html_from_markdown('chess_openings.md')
    print("Static website generated as index.html")

if __name__ == "__main__":
    main()
