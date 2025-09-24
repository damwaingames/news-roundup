import requests
from datetime import datetime, timedelta
import time
import json
import random
import feedparser

# --- Configuration and Data ---

# Target news websites and their RSS feed URLs
RSS_FEEDS = {
    "Charity Today": "https://www.charitytoday.co.uk/feed/",
    "Third Sector": "https://www.thirdsector.co.uk/rss/news",
    "BBC News (Charity Topic)": "https://feeds.bbci.co.uk/news/topics/c9z6w63q5elt/rss.xml"
}

# Clients of particular interest (for keyword-based filtering)
CLIENTS = []
with open("data/torchbox-clients.json") as f:
    CLIENTS = json.load(f)

def get_recent_articles(url, source_name):
    """
    Fetches and parses an RSS feed for articles from the last 7 days.
    Returns a list of dictionaries with article data.
    """
    # Use a random user-agent to mimic a real browser and a short delay to be polite.
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]
    headers = {'User-Agent': random.choice(user_agents)}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed from {url}: {e}")
        return []

    feed = feedparser.parse(response.content)
    articles = []
    
    # Define a time threshold for the last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)

    # Iterate through each entry in the RSS feed
    for entry in feed.entries:
        try:
            # Parse the publication date from the entry
            if 'published_parsed' in entry:
                pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif 'updated_parsed' in entry:
                pub_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            else:
                continue # Skip if no date can be found

            # Check if the article is within the last 7 days
            if pub_date > seven_days_ago:
                articles.append({
                    'source': source_name,
                    'title': entry.title,
                    'link': entry.link,
                    'date': pub_date.strftime('%Y-%m-%d')
                })
        except Exception as e:
            print(f"Error parsing entry from {source_name}: {e}")
            continue
    
    return articles

def generate_slack_message(articles):
    """
    Generates a Slack-friendly summary of the top 10 most important news items.
    Importance is based on keywords and client names.
    """
    # Keywords for importance scoring
    keywords = ['funding', 'grant', 'staffing', 'redundancies', 'changes', 'appointments', 'trend', 'report', 'research', 'partnership']
    client_keywords = [client.get("name").lower() for client in CLIENTS]

    def score_article(article):
        score = 0
        title_lower = article['title'].lower()
        
        # Boost score for keywords
        for keyword in keywords:
            if keyword in title_lower:
                score += 2
        
        # Boost score for client mentions
        for client in client_keywords:
            if client in title_lower:
                score += 5
        
        return score

    # Score and sort the articles
    scored_articles = sorted(articles, key=score_article, reverse=True)
    top_articles = scored_articles[:10]

    # Format the Slack message
    summary_text = "*Weekly UK Charity Sector News Roundup* :bell:\n\n"
    if not top_articles:
        summary_text += "No high-priority news found in the past seven days.\n"
        summary_text += "_All links from the past week are provided below for your reference._\n"
    else:
        summary_text += "Here are the top news items from the past week:\n\n"
        for i, article in enumerate(top_articles, 1):
            summary_text += f"{i}. <{article['link']}|{article['title']}>\n"
        summary_text += "\n_See the full roundup below for more stories and sources._"
    
    return summary_text

def main():
    """
    Main function to run the news roundup.
    """
    all_articles = []
    print("Beginning the UK charity news roundup...")
    for source_name, url in RSS_FEEDS.items():
        print(f"Fetching and parsing RSS feed from {source_name}...")
        articles = get_recent_articles(url, source_name)
        all_articles.extend(articles)
        # Be a good web citizen: pause between requests
        time.sleep(random.uniform(1, 3))

    # Sort all articles by date, from newest to oldest
    all_articles.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

    # --- Output to Slack Canvas Format (Markdown) ---

    print("\n\n--- Full Weekly News Roundup ---\n\n")

    # Group articles by source
    grouped_articles = {}
    for article in all_articles:
        source = article['source']
        if source not in grouped_articles:
            grouped_articles[source] = []
        grouped_articles[source].append(article)

    # Print the grouped, markdown-formatted links
    for source, articles in grouped_articles.items():
        print(f"### {source}")
        if not articles:
            print("No recent articles found.")
        else:
            for article in articles:
                print(f"- [{article['title']}]({article['link']}) ({article['date']})")
        print("\n")

    # --- Output the Slack message summary ---
    slack_summary = generate_slack_message(all_articles)
    print("\n\n--- Slack Message Summary ---")
    print(slack_summary)

if __name__ == "__main__":
    main()
