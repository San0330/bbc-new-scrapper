import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

start_url = [
    {
        "category": "नेपाल",
        "url": "https://www.bbc.com/nepali/topics/cyx5k2yzyj6t?page={}",
        "page": 40
    },
    {
        "category": "विश्व",
        "url": "https://www.bbc.com/nepali/topics/cy5nkr41gx6t?page={}",
        "page": 40
    },
    {
        "category": "स्वास्थ्य",
        "url": "https://www.bbc.com/nepali/topics/c2dwqjg83q0t?page={}",
        "page": 40
    },
    {
        "category": "विज्ञान तथा प्रविधि",
        "url": "https://www.bbc.com/nepali/topics/c9de5jl3967t?page={}",
        "page": 29
    }
]

csv_filename = 'scraped_articles.csv'

# Load existing CSV if available
try:
    df = pd.read_csv(csv_filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=['id', 'url', 'category', 'date', 'title', 'summary', 'text'])

# Track already seen URLs
seen = set(df['url'].tolist())

# Start crawling
for url_config in start_url:
    category = url_config['category']
    base_url = url_config['url']
    total_pages = url_config['page']

    for page_number in range(1, total_pages + 1):
        url = base_url.format(page_number)
        print(f"\n🔍 Crawling: {url}")
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            print(f"❌ Failed to fetch page {url}: {e}")
            continue

        grid = soup.find('div', attrs={'data-testid': 'curation-grid-normal'})
        if not grid:
            print("⚠️ curation-grid-normal not found.")
            continue

        links = grid.find_all('a', href=True)
        print(f"🔗 Found {len(links)} article links.")

        for a in links:
            link = a['href']
            if '/nepali/live/' in link:
                print(f"❌ Skipping: {link}")
                continue

            full_url = link

            if full_url in seen:
                print(f"🔁 Already exists: {full_url}")
                row_index = df.index[df['url'] == full_url].tolist()
                if row_index:
                    existing_categories = df.at[row_index[0], 'category']
                    if category not in existing_categories.split(', '):
                        df.at[row_index[0], 'category'] = existing_categories + ', ' + category
                continue

            try:
                print(f"📰 Scraping: {full_url}")
                art_res = requests.get(full_url)
                art_soup = BeautifulSoup(art_res.text, 'html.parser')

                article_id = link.split('/')[-1]
                title = art_soup.find('h1').text.strip()

                # Extract date
                date = ''
                # Find all <time> tags that are NOT inside a <figure>
                time_tags = [t for t in art_soup.find_all('time') if not t.find_parent('figure')]
                time_tag = time_tags[0] if time_tags else None
                if time_tag and time_tag.get('datetime'):
                    date = time_tag['datetime']

                # Extract summary
                paragraphs = art_soup.find_all('p')
                summary = 'Summary not found'
                for i, p in enumerate(paragraphs):
                    if p.find('b'):
                        
                        # Apply the same filtering conditions to summary extraction
                        if not p.find_parent('figure') and not p.find_parent('footer'):
                            if p.get('id') != 'end-of-recommendations':                                
                                potential_summary = p.text.strip()
                                # Skip if summary starts with social media promotion text
                                if not potential_summary.startswith("बीबीसी न्यूज नेपाली यूट्यूबमा पनि छ"):
                                    summary = potential_summary
                                    paragraphs.pop(i)
                                    break

                # Filter main content paragraphs
                filtered_paragraphs = []
                for p in paragraphs:
                    if not p.find_parent('figure') and not p.find_parent('footer'):
                        if p.get('id') != 'end-of-recommendations':                            
                            filtered_paragraphs.append(p)

                full_text = ' '.join([p.text.strip() for p in filtered_paragraphs])
                
                # Remove everything after "बीबीसी न्यूज नेपाली यूट्यूबमा पनि छ।" if found
                cutoff_text = "बीबीसी न्यूज नेपाली यूट्यूबमा पनि छ।"
                if cutoff_text in full_text:
                    full_text = full_text.split(cutoff_text)[0].strip()

                # Add to DataFrame
                new_row = {
                    'id': article_id,
                    'url': full_url,
                    'category': category,
                    'date': date,
                    'title': title,
                    'summary': summary,
                    'text': full_text
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                seen.add(full_url)

                # Save to CSV every 50 rows
                if len(df) % 50 == 0:
                    df.to_csv(csv_filename, index=False)
                    print(f"💾 Saved {len(df)} articles to {csv_filename}")

                time.sleep(1)


            except Exception as e:
                print(f"❌ Error scraping article {full_url}: {e}")

        # Print 5 random samples from existing DataFrame at the end of each page
        # if len(df) > 0:
        #     print(f"\n📊 Random 5 samples from current dataset (Total: {len(df)} articles):")
        #     random_samples = df.sample(min(5, len(df)))
        #     for idx, row in random_samples.iterrows():
        #         print(f"  • {row['title'][:50]}... | Category: {row['category']} | ID: {row['id']}")
        #     print()

# Save updated CSV
df.to_csv(csv_filename, index=False)
print(f"\n✅ Scraping complete. Data saved to {csv_filename}")
