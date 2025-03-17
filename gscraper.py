from googlesearch import search


for result in search("site:bbc.com news", num_results=1, unique=True, advanced=True, sleep_interval=2, region="us", start_date="2022-01-01", end_date="2022-12-31"):
    print(f"\n{result}\n")
