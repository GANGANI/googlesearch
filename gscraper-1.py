from googlesearch import search

for result in search("site:en.wikipedia.org adn.com", num_results=50, unique=True, advanced=True, sleep_interval=5, region="us"):
    print(f"\n{result.url}\n")

