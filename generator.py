import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # To handle relative URLs
from duckduckgo_search import DDGS  # Correct import
import pprint
import random
from slugify import slugify
import os
import time

subfolder_name = 'openings'

def scrape_openings(url):

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find('div', class_="elementor-element elementor-element-7f0d9d87 elementor-widget elementor-widget-shortcode")

    openings = []
    if container:
        for link in container.find_all('a', href=True):
            if link.find('span') != None:
                continue

            full_url = urljoin(url, link['href'])
        
            title = link.find('h5')
            title_text = title.get_text(strip=True) if title else 'Untitled'
            
            img_tag = link.find('img')
            image_url = urljoin(url, img_tag['src']) if img_tag else None
            
            openings.append({
                'title': title_text,
                'url': full_url,
                'image_url': image_url
            })

    return openings[:10]

def scrape_details(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    main_content = soup.find('div', class_='cb-post-grid')
    if not main_content:
        return ""
    
    for element in main_content.select('.ad-container, script, ins, .comments'):
        element.decompose()
    
    sections = []
    current = main_content.h1.find_next()
    while current and current.name != 'hr':
        if current.name in ['p', 'ul', 'ol']:
            text = current.get_text()
            if text:
                sections.append(text)
        current = current.find_next_sibling()
    
    return '\n\n'.join(sections)

def download_image(slug, url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    if response.headers['Content-Type'] not in ['image/jpeg', 'image/png']:
        print(f"Invalid image type: {url}")
        return None
        
    ext = 'png' if 'png' in response.headers['Content-Type'] else 'jpg'
    filename = f"{slug}.{ext}"
    path = os.path.join(subfolder_name, slug, filename)
    
    with open(path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
            
    return path

def make_page_for_opening(opening):
    title = opening['title']
    slug = slugify(title)
    inner_folder = os.path.join(subfolder_name, slug)
    os.makedirs(inner_folder, exist_ok=True)
    image_path = download_image(slug, opening['image_url']) if opening['image_url'] else None
    image_var = f"image: {image_path}\n" if image_path else ""
    image_md = f"![{title}]({image_path})\n\n" if image_path else ""

    content = f'''---
layout: default
title: "{title}"
permalink: /openings/{slug}/
{image_var}
---# {title}\n\n
{image_md}
{opening['descr']}\n\n
## Official Documentation\n[Source]({opening['url']})\n
'''
    
    path = os.path.join(inner_folder, "index.md")
    with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

def generate_homepage(openings):
    homepage_content = """---
layout: default
title: Chess Openings
---

# Chess Openings Catalog

"""
    search = DDGS()
    for opening in openings:
        title = opening['title']
        slug = slugify(title)
        image_path = f"{slug}/{slug}.jpg" if opening['image_url'] else ""
        image_md = f"![{title}]({image_path})\n\n" if opening['image_url'] else ""
        print(title)
        query = "what is "+ title
        print(query)
        info = list(search.text(keywords=query, timelimit='d', max_results=1))
        print(info)
        time.sleep(random.uniform(20, 30))
        info = info[0]['body'] if info else "No description found online."

        homepage_content += f"""## [{title}]({slug}/)\n
{image_md}\n
{info}\n
[Read more]({slug}/)\n
"""
    
    with open("index.md", "w", encoding="utf-8") as f:
        f.write(homepage_content)

def main():
    url = "https://www.thechesswebsite.com/chess-openings/"
    openings = scrape_openings(url)
    os.makedirs("openings", exist_ok=True)
    generate_homepage(openings)
    for opening in openings:
        opening['descr'] = scrape_details(opening['url'])
        make_page_for_opening(opening)

if __name__ == "__main__":
    main()