import requests
from datetime import datetime

# ======================== 👇👇👇 替换成你的企业微信Webhook 👇👇👇 ========================
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的机器人完整Webhook地址"
# ======================== 👆👆👆 替换结束 👆👆👆 ========================

def main():
    try:
        # 测试模式：直接构造消息
        gold_type_name = "Au9999（上交所标准金价）"
        message_type = "上涨"
        color = "red"
        current_price = 580.00
        last_price = 575.00
        change = current_price - last_price
        change_percent = round((change / last_price) * 100, 2)

        # 构造纯文本消息（避免Markdown格式问题）
        payload = {
            "msgtype": "text",
            "text": {
                "content": f"测试消息：金价{message_type}！当前价格{current_price:.2f}元/克，较昨日收盘价{last_price:.2f}元/克上涨{abs(change):.2f}元，涨幅{change_percent}%。"
            }
        }

        # 发送消息并打印响应
        response = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
        print(f"📝 企业微信响应：{response.status_code} - {response.text}")
        if response.status_code == 200 and response.json().get("errcode") == 0:
            print("✅ 测试消息发送成功！")
        else:
            print(f"❌ 推送失败：{response.text}")

    except Exception as e:
        print(f"❌ 执行出错：{str(e)}")

if __name__ == "__main__":
    main()
