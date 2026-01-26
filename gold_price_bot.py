import requests
import re
from datetime import datetime

# ======================== 👇👇👇 替换成你的企业微信Webhook 👇👇👇 ========================
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9022a284-f0a5-466d-aecc-56e01d333ef7"
# ======================== 👆👆👆 替换结束 👆👆👆 ========================

PRICE_THRESHOLD = 5

def main():
    try:
        # 1. 使用更稳定的数据源（上海黄金交易所公开接口）
        api_url = "https://www.sge.com.cn/sgeweb/quotation!showQuotation.action"
        # 添加浏览器请求头，模拟正常访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.sge.com.cn/"
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        data = response.text
        print(f"📝 上金所原始返回：{data[:200]}...")  # 打印前200字符，方便排查

        # 2. 解析上金所数据（适配HTML格式）
        # 提取Au9999的最新价格和昨日收盘价
        current_price_match = re.search(r'<td class="last">(\d+\.\d+)</td>', data)
        last_price_match = re.search(r'<td class="prevClose">(\d+\.\d+)</td>', data)

        if current_price_match and last_price_match:
            current_price = float(current_price_match.group(1))
            last_price = float(last_price_match.group(1))
            change = current_price - last_price
            change_percent = round((change / last_price) * 100, 2)
            print(f"📊 解析成功：当前价格{current_price:.2f}元/克，昨日收盘价{last_price:.2f}元/克，涨跌{change:.2f}元")

            # 3. 判断是否触发提醒
            if abs(change) >= PRICE_THRESHOLD:
                gold_type_name = "Au9999（上交所标准金价）"
                message_type = "上涨" if change > 0 else "下跌"

                # 4. 构造纯文本消息
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": f"⚠️ 金价大幅{message_type}提醒 ⚠️\n{gold_type_name}\n当前价格：{current_price:.2f}元/克\n昨日收盘价：{last_price:.2f}元/克\n{message_type}金额：{abs(change):.2f}元（超过{PRICE_THRESHOLD}元阈值）\n{message_type}幅度：{change_percent}%\n更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }

                # 5. 发送到企业微信群
                push_response = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
                print(f"📝 企业微信响应：{push_response.status_code} - {push_response.text}")
                if push_response.status_code == 200 and push_response.json().get("errcode") == 0:
                    print(f"✅ 提醒发送成功：{gold_type_name}{message_type}{abs(change):.2f}元")
                else:
                    print(f"❌ 推送失败：{push_response.text}")
            else:
                print(f"ℹ️ 无需提醒：涨跌{change:.2f}元，未达{PRICE_THRESHOLD}元阈值")
        else:
            print("❌ 解析失败：未获取到有效金价数据")

    except Exception as e:
        print(f"❌ 执行出错：{str(e)}")

if __name__ == "__main__":
    main()
