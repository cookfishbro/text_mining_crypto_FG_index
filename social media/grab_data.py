import praw
import datetime
import time
import random
import csv
import os
from dotenv import load_dotenv
from config import USER_AGENT

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=USER_AGENT
)

subreddit = reddit.subreddit("all")  # 搜全站

# 時間範圍
start_date = datetime.datetime(2024, 10, 1)
end_date   = datetime.datetime(2025, 9, 30)
start_ts = start_date.timestamp()
end_ts   = end_date.timestamp()

# 關鍵字
subreddits = ["ethereum", "ethtrader", "CryptoCurrency", "cryptomarkets"]
keywords = ["Ethereum", "ETH"]

# 建立 CSV
file_name = "ETH_2024-10_2025-09.csv"

with open(file_name, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
         "subreddit","id","created_at","title","text","author",
         "upvotes","num_comments","url","permalink"
    ])

     # ===== 去重集合 =====
    seen_ids = set()

    # ===== 迴圈架構 =====
    count = 0
    for sub_name in subreddits:           # 逐板塊
        subreddit = reddit.subreddit(sub_name)
        for kw in keywords:
            # 搜尋關鍵字貼文，抓最新貼文
            for post in subreddit.search(kw, sort="relevance", limit=2000):
                # 篩選時間
                if start_ts <= post.created_utc <= end_ts:
                    # 去重
                    if post.id in seen_ids:
                        continue
                    seen_ids.add(post.id)

                    # 寫入 CSV
                    writer.writerow([
                        post.subreddit.display_name,
                        post.id,
                        datetime.datetime.fromtimestamp(post.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        post.title,
                        (post.selftext or "").replace("\n", " ").replace("\r", " "),
                        post.author,
                        post.score,
                        post.num_comments,
                        post.url,
                        f"https://www.reddit.com{post.permalink}"
                    ])
                    count += 1
            time.sleep(random.randint(2, 5)) 

print(f"✅ 已儲存 {count} 篇貼文")
