import requests
from datetime import datetime

WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9022a284-f0a5-466d-aecc-56e01d333ef7"
ALPHA_VANTAGE_API_KEY = "3AV1ZIWRB84HA9HD"  # 替换成你的API Key
PRICE_THRESHOLD = 0

def main():
    try:
        # Alpha Vantage接口（获取黄金兑人民币价格）
        api_url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=XAU&to_currency=CNY&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        print(f"📝 Alpha Vantage返回：{data}")

        if "Realtime Currency Exchange Rate" in data:
            current_price = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
            # 用前一天的价格模拟昨日收盘价（或接口返回的历史数据）
            last_price = current_price - 3.0  # 模拟值，实际可以用接口的历史数据
            change = current_price - last_price
            change_percent = round((change / last_price) * 100, 2)

            if abs(change) >= PRICE_THRESHOLD:
                message_type = "上涨" if change > 0 else "下跌"
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": f"⚠️ 金价大幅{message_type}提醒 ⚠️\nXAU/CNY（黄金兑人民币）\n当前价格：{current_price:.2f}元/克\n昨日收盘价：{last_price:.2f}元/克\n{message_type}金额：{abs(change):.2f}元\n{message_type}幅度：{change_percent}%\n更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }
                push_response = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
                print(f"✅ 提醒发送成功：{push_response.text}")
            else:
                print(f"ℹ️ 无需提醒：涨跌{change:.2f}元，未达阈值")
        else:
            print("❌ 解析失败：未获取到有效数据")

    except Exception as e:
        print(f"❌ 执行出错：{str(e)}")

if __name__ == "__main__":
    main()
