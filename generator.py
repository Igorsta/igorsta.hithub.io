import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # To handle relative URLs
import pprint
from slugify import slugify
import os

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
            title_text = title.get_text(strip=True) if title else None
            
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
    path = os.path.join(slug, filename)
    
    with open(path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
            
    return path

def make_page_for_opening(opening):
    title = opening['title']
    slug = slugify(title)
    os.makedirs(slug, exist_ok=True)
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
## Official Documentation\n[Source]({opening['url']})
'''
    
    path = os.path.join(slug, "index.md")
    with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    url = "https://www.thechesswebsite.com/chess-openings/"
    openings = scrape_openings(url)
    for opening in openings:
        opening['descr'] = scrape_details(opening['url'])
        make_page_for_opening(opening)


if __name__ == "__main__":
    main()