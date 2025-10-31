
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

# 讀取資料
emotion_index = pd.read_csv("emotion_index_normalized.csv", parse_dates=['date']).rename(columns={'date': 'Date'})
price = pd.read_csv("eth-usd-max.csv", parse_dates=['date']).rename(columns={'date': 'Date'})
# 將兩者統一為無時區格式
# 統一欄名（第一欄多半是日期）
emotion_index.rename(columns={emotion_index.columns[0]: 'Date'}, inplace=True)
price.rename(columns={price.columns[0]: 'Date'}, inplace=True)

# 將日期轉成 datetime 格式並移除時區
emotion_index['Date'] = pd.to_datetime(emotion_index['Date'], errors='coerce').dt.tz_localize(None)
price['Date'] = pd.to_datetime(price['Date'], errors='coerce').dt.tz_localize(None)

# 設成 index
emotion_index = emotion_index.set_index('Date')
price = price.set_index('Date')

# 統一成每日資料頻率
emotion_index = emotion_index.resample('D').interpolate()
price = price.resample('D').ffill()

# 移除不必要的欄位
price.drop(columns = ['market_cap', 'total_volume'], inplace=True)

# 執行標準化（安全版：使用 z-score，避免 2D reshape 問題）
def zscore(series):
    s = pd.to_numeric(series, errors='coerce')
    return (s - s.mean()) / s.std(ddof=0)
emotion_index['Greed_Fear_Score'] = zscore(emotion_index['Greed_Fear_Score'])
price['price'] = zscore(price['price'])

# 繪製趨勢線
coefficients = np.polyfit(mdates.date2num(emotion_index.index), emotion_index['Greed_Fear_Score'], 1)
p = np.poly1d(coefficients)
plt.plot(emotion_index.index, p(mdates.date2num(emotion_index.index)), color='orange', linestyle='--', label='Trendline', alpha=0.5)

# correlation
merged = pd.merge(emotion_index, price, left_index=True, right_index=True)
corr = merged['Greed_Fear_Score'].corr(merged['price'])
print(f"Correlation (daily): {corr:.4f}")

# 疊合 Price 與 Greed-Fear 指數
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())        # 主刻度：每個月
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # 格式化顯示「年-月」
plt.plot(price.index, price['price'], label='price', linewidth=2)
plt.plot(emotion_index.index, emotion_index['Greed_Fear_Score'], label='Greed - Fear Score', color='red', linewidth=2, alpha=0.7)
plt.title(f"Price vs Greed-Fear Index (corr={corr:.2f})", fontsize=14)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Standardized score", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
