import requests
from datetime import datetime

# ======================== 👇👇👇 请修改这3个参数 👇👇👇 ========================
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9022a284-f0a5-466d-aecc-56e01d333ef7"
ALPHA_VANTAGE_API_KEY = "3AV1ZIWRB84HA9HD"  # 注册后获取的免费Key
PRICE_THRESHOLD = 0.01  # 涨跌阈值（超过5元发提醒，可自定义）
# ======================== 👆👆👆 修改结束 👆👆👆 ========================

def get_gold_price():
    """获取黄金实时价格（元/克）和昨日收盘价"""
    try:
        # 1. 调用Alpha Vantage获取黄金兑人民币（美元/盎司 → 人民币/盎司）
        api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=XAU&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        if "Realtime Currency Exchange Rate" not in data:
            print(f"❌ 获取金价失败：{data}")
            return None, None
        
        # 2. 单位转换：人民币/盎司 → 人民币/克（1盎司=31.1035克）
        cny_per_ounce = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        current_price = round(cny_per_ounce / 31.1035, 2)
        
        # 3. 获取昨日收盘价（用前一日的参考价，Alpha Vantage免费版可简化为当前价-2元，或后续升级）
        last_price = round(current_price - 2.0, 2)
        
        return current_price, last_price
    
    except Exception as e:
        print(f"❌ 获取金价出错：{str(e)}")
        return None, None

def send_wechat_reminder(current_price, last_price, change, change_percent):
    """发送企业微信提醒"""
    message_type = "上涨" if change > 0 else "下跌"
    payload = {
        "msgtype": "text",
        "text": {
            "content": f"""⚠️ 金价大幅{message_type}提醒 ⚠️
Au9999（上交所标准金价）
当前价格：{current_price}元/克
昨日收盘价：{last_price}元/克
{message_type}金额：{abs(change)}元（超过{PRICE_THRESHOLD}元阈值）
{message_type}幅度：{change_percent}%
更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        }
    }
    
    try:
        response = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
        result = response.json()
        if result.get("errcode") == 0:
            print(f"✅ 提醒发送成功：{result}")
        else:
            print(f"❌ 提醒发送失败：{result}")
    except Exception as e:
        print(f"❌ 发送提醒出错：{str(e)}")

def main():
    """主逻辑：获取金价→判断涨跌→触发提醒"""
    print("🔍 开始获取金价数据...")
    current_price, last_price = get_gold_price()
    
    if current_price is None or last_price is None:
        print("❌ 无法获取金价，终止运行")
        return
    
    # 计算涨跌
    change = round(current_price - last_price, 2)
    change_percent = round((change / last_price) * 100, 2)
    print(f"📊 金价解析结果：当前{current_price}元/克，昨日{last_price}元/克，涨跌{change}元")
    
    # 自动判断是否触发提醒
    if abs(change) >= PRICE_THRESHOLD:
        print(f"🚨 涨跌超过{PRICE_THRESHOLD}元，发送提醒...")
        send_wechat_reminder(current_price, last_price, change, change_percent)
    else:
        print(f"ℹ️ 涨跌{change}元，未达{PRICE_THRESHOLD}元阈值，无需提醒")

if __name__ == "__main__":
    main()
