# gold_price_bot.py - 企业微信金价提醒核心脚本
import requests
import re
from datetime import datetime

# ======================== 👇👇👇 替换成你的企业微信Webhook 👇👇👇 ========================
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9022a284-f0a5-466d-aecc-56e01d333ef7"
# ======================== 👆👆👆 替换结束 👆👆👆 ========================

GOLD_TYPE = "au9999"
PRICE_THRESHOLD = 5

def main():
    try:
        # 1. 获取金价数据
        api_url = f"http://hq.sinajs.cn/list={GOLD_TYPE}"
        response = requests.get(api_url, timeout=10)
        response.encoding = "gbk"
        data = response.text

        # 2. 解析数据
        data_match = re.search(r'"(.*?)"', data)
        if data_match:
            data_arr = data_match.group(1).split(',')
            current_price = float(data_arr[8])
            last_price = float(data_arr[7])
            change = current_price - last_price
            change_percent = round((change / last_price) * 100, 2)

            # 3. 判断是否触发提醒
            if abs(change) >= PRICE_THRESHOLD:
                gold_type_name = {"au9999":"Au9999（上交所标准金价）","agtdAu":"黄金T+D"}.get(GOLD_TYPE, GOLD_TYPE)
                message_type = "上涨" if change > 0 else "下跌"
                color = "red" if change > 0 else "green"

                # 4. 构造消息
                markdown_content = f"""
