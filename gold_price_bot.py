import requests
import re
from datetime import datetime

WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9022a284-f0a5-466d-aecc-56e01d333ef7"
PRICE_THRESHOLD = 0

def main():
    try:
        # 新浪财经接口（优化请求头）
        api_url = "https://hq.sinajs.cn/list=au9999"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://finance.sina.com.cn/"
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        response.encoding = "gbk"
        data = response.text
        print(f"📝 新浪财经返回：{data}")

        # 解析数据
        data_match = re.search(r'var hq_str_au9999="([^"]+)"', data)
        if data_match:
            data_arr = data_match.group(1).split(',')
            if len(data_arr) >= 2:
                current_price = float(data_arr[0])
                last_price = float(data_arr[1])
                change = current_price - last_price
                change_percent = round((change / last_price) * 100, 2)

                if abs(change) >= PRICE_THRESHOLD:
                    message_type = "上涨" if change > 0 else "下跌"
                    payload = {
                        "msgtype": "text",
                        "text": {
                            "content": f"⚠️ 金价大幅{message_type}提醒 ⚠️\nAu9999（上交所标准金价）\n当前价格：{current_price:.2f}元/克\n昨日收盘价：{last_price:.2f}元/克\n{message_type}金额：{abs(change):.2f}元\n{message_type}幅度：{change_percent}%\n更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    }
                    push_response = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
                    print(f"✅ 提醒发送成功：{push_response.text}")
                else:
                    print(f"ℹ️ 无需提醒：涨跌{change:.2f}元，未达阈值")
            else:
                print("❌ 解析失败：数据字段不足")
        else:
            print("❌ 解析失败：未获取到有效数据")

    except Exception as e:
        print(f"❌ 执行出错：{str(e)}")

if __name__ == "__main__":
    main()
