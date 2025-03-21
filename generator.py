import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from googlesearch import search
import pprint
import random
from slugify import slugify
import os
import shutil

subfolder_name = 'openings'

def scrape_openings(url):

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find('div', class_="elementor-element elementor-element-7f0d9d87 elementor-widget elementor-widget-shortcode")

    if not container:
        return []
    
    openings = []
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

    return random.sample(openings, 10)

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
            
    return filename

def make_page_for_opening(opening):
    title = opening['title']
    slug = slugify(title)
    inner_folder = os.path.join(subfolder_name, slug)
    os.makedirs(inner_folder, exist_ok=True)
    image_name = download_image(slug, opening['image_url']) if opening['image_url'] else None
    opening['image_name'] = image_name
    image_md = f"![{title}](/{image_name})\n\n" if image_name else ""

    content = f'''---
layout: default
title: "{title}"
permalink: /openings/{slug}/
---
# {title}\n\n
{image_md}
{opening['descr']}\n\n
## Official Documentation\n[Source]({opening['url']})\n
'''
    
    path = os.path.join(inner_folder, "index.md")
    with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

def try_geting_details(query):
    scraped_sites = [url for url in search(query, num_results=2)]
    info = []
    for url in scraped_sites:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract text (modify tag selection if needed)
            paragraphs = soup.find_all("p")
            text = "\n".join([para.get_text() for para in paragraphs])
            info.append(text[:1000] + f"\n\n [Complete description]({url})")
        except Exception:
            pass
    
    return random.choice(info) if info else "No Description online found"

def generate_homepage(openings):
    print("Making homepage")
    homepage_content = """---
layout: default
title: Chess Openings Catalog
---

"""
        
    for opening in openings:
        title = opening['title']
        slug = slugify(title)
        opening_subfolder = f"{subfolder_name}/{slug}"
        image_md = f"![{title}](/{opening_subfolder}/{opening['image_name']})\n\n" if opening['image_url'] else ""
        info = try_geting_details(title + " definition site:wikipedia.org")

        homepage_content += f"""## [{title}]({{{{ "/{opening_subfolder}/" | relative_url }}}})\n
{image_md}\n
{info}\n
"""
        print(f"\tserved the {title}")
    
    with open("index.md", "w", encoding="utf-8") as f:
        f.write(homepage_content)

def main():
    shutil.rmtree(subfolder_name)
    url = "https://www.thechesswebsite.com/chess-openings/"
    openings = scrape_openings(url)
    os.makedirs("openings", exist_ok=True)
    for opening in openings:
        opening['descr'] = scrape_details(opening['url'])
        make_page_for_opening(opening)
        print(f"Finished makeing {opening['title']}")
    generate_homepage(openings)

if __name__ == "__main__":
    main()