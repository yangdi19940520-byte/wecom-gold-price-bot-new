# gold_price_bot.py - 修复三引号语法错误版
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

                # 4. 构造消息（修复三引号闭合问题）
                markdown_content = f"""⚠️ **金价大幅{message_type}提醒** ⚠️

**{gold_type_name}**
当前价格：<font color=\"{color}\">{current_price:.2f}元/克</font>
昨日收盘价：{last_price:.2f}元/克
{message_type}金额：<font color=\"{color}\">{abs(change):.2f}元</font>（超过{PRICE_THRESHOLD}元阈值）
{message_type}幅度：<font color=\"{color}\">{change_percent}%</font>

更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源：新浪财经官方API
"""

                # 5. 发送到企业微信群
                payload = {
                    "msgtype": "markdown",
                    "markdown": {"content": markdown_content}
                }
                requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
                print(f"✅ 提醒发送成功：{gold_type_name}{message_type}{abs(change):.2f}元")
            else:
                print(f"ℹ️ 无需提醒：涨跌{change:.2f}元，未达{PRICE_THRESHOLD}元阈值")
        else:
            print("❌ 解析失败：未获取到有效金价数据")
    except Exception as e:
        print(f"❌ 执行出错：{str(e)}")

if __name__ == "__main__":
    main()
