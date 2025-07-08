import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load the CSV file
csv_filename = 'scraped_articles8.csv'

def get_datetime_not_in_figure(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        time_tags = [t for t in soup.find_all('time') if not t.find_parent('figure')]
        time_tag = time_tags[0] if time_tags else None
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']
        else:
            return None
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def main():
    try:
        df = pd.read_csv(csv_filename)
    except FileNotFoundError:
        print(f"❌ File {csv_filename} not found!")
        return
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    # Filter rows where 'date' starts with 'PT'
    mask = df['date'].astype(str).str.startswith('PT')
    pt_rows = df[mask]

    if pt_rows.empty:
        print("No rows with 'date' starting with 'PT'.")
    else:
        print("Updating datetime values for rows with 'date' starting with 'PT':")
        for idx in pt_rows.index:
            url = df.at[idx, 'url']
            print(f"\nURL: {url}")
            new_datetime = get_datetime_not_in_figure(url)
            if new_datetime:
                print(f"  Updated datetime: {new_datetime}")
                df.at[idx, 'date'] = new_datetime
            else:
                print("  No valid <time> tag found (not inside <figure>) or no datetime attribute. Keeping original value.")

        # Save the updated DataFrame back to CSV
        df.to_csv(csv_filename, index=False)
        print(f"\n✅ Updated DataFrame saved to {csv_filename}")

if __name__ == "__main__":
    main()
