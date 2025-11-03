import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

# -------------------------------
# 文字清理函數
# -------------------------------
def clean_post(text):
    """
    前處理貼文文字：
    - 合併標題與內容
    - 轉小寫
    - 移除網址、標點符號、特殊字元
    - 去除停用字
    """
    if pd.isna(text):
        return ""
    
    # 轉小寫
    text = text.lower()
    
    # 移除網址
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # 移除標點與特殊符號
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # 移除多餘空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 去除停用字
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [w for w in words if w not in stop_words]
    
    return ' '.join(words)

# -------------------------------
# 主程式
# -------------------------------
def process_reddit_csv(input_csv, output_csv):
    # 讀取 CSV
    df = pd.read_csv(input_csv)
    
    # 合併 title 與 text
    df['full_text'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
    
    # 清理文字
    df['clean_text'] = df['full_text'].apply(clean_post)
    
    # 情感分析
    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df['clean_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    
    # 計算影響力分數（加權 upvotes 與 num_comments）
    df['influence'] = df['sentiment'] * np.log1p(df['upvotes'] + df['num_comments'])
    
    # 寫入新 CSV
    df.to_csv(output_csv, index=False)
    print(f"已生成新 CSV：{output_csv}")

# -------------------------------
# 範例使用
# -------------------------------
if __name__ == "__main__":

    input_csv = "ETH_2024-10_2025-09.csv"
    output_csv = "ETH_with_sentiment.csv"
    process_reddit_csv(input_csv, output_csv)
