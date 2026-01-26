import requests
import re
from datetime import datetime

# ======================== 👇👇👇 替换成你的企业微信Webhook 👇👇👇 ========================
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9022a284-f0a5-466d-aecc-56e01d333ef7"
# ======================== 👆👆👆 替换结束 👆👆👆 ========================

GOLD_TYPE = "au9999"
PRICE_THRESHOLD = 0

def main():
    try:
        # 1. 获取金价数据（新浪财经接口）
        api_url = f"http://hq.sinajs.cn/list={GOLD_TYPE}"
        response = requests.get(api_url, timeout=10)
        response.encoding = "gbk"
        data = response.text
        print(f"📝 新浪财经原始返回：{data}")  # 打印原始数据，方便排查

        # 2. 解析数据（修复版，适配新浪财经格式）
        data_match = re.search(r'var hq_str_[^=]+="([^"]+)"', data)
        if data_match:
            data_arr = data_match.group(1).split(',')
            if len(data_arr) >= 2:
                # 新浪财经格式：最新价格是第1个字段，昨日收盘价是第2个字段
                current_price = float(data_arr[0])
                last_price = float(data_arr[1])
                change = current_price - last_price
                change_percent = round((change / last_price) * 100, 2)
                print(f"📊 解析成功：当前价格{current_price:.2f}元/克，昨日收盘价{last_price:.2f}元/克，涨跌{change:.2f}元")

                # 3. 判断是否触发提醒
                if abs(change) >= PRICE_THRESHOLD:
                    gold_type_name = {"au9999":"Au9999（上交所标准金价）","agtdAu":"黄金T+D"}.get(GOLD_TYPE, GOLD_TYPE)
                    message_type = "上涨" if change > 0 else "下跌"
                    color = "red" if change > 0 else "green"

                    # 4. 构造消息（纯文本格式，避免Markdown问题）
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
                print("❌ 解析失败：数据字段不足")
        else:
            print("❌ 解析失败：未获取到有效金价数据")

    except Exception as e:
        print(f"❌ 执行出错：{str(e)}")

if __name__ == "__main__":
    main()
