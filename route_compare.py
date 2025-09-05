import requests
import time
import json

# ====================== 配置参数 ======================
AMAP_KEY = ""  # 高德API密钥
END_POINT = ""               # 固定终点
STRATEGY = 0                                   # 路线策略：0=最快路线（驾车）

# 批量起点列表
START_POINTS = [
    ]

# ====================== 工具函数 ======================
def geocode(address, key):
    """
    调用高德地理编码API，返回 (lng, lat) 经纬度字符串（保留6位小数）
    """
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": key,
        "address": address,
        "output": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = json.loads(response.text)
        if data.get("status") == "1" and len(data.get("geocodes", [])) > 0:
            location = data["geocodes"][0]["location"]  # "lng,lat"
            lng, lat = location.split(",")
            print(f"[地理编码成功] 地址 「{address}」 经纬度 {float(lng):.6f},{float(lat):.6f}")

            # 保留6位小数
            return f"{float(lng):.6f},{float(lat):.6f}"
        else:
            print(f"{data.get('status')=}\n{data.get('geocodes')=}\n")
            print(f"[地理编码失败] 地址「{address}」：{data.get('info', '未知错误')}")
            return None
    except Exception as e:
        print(f"[地理编码异常] 地址「{address}」：{str(e)}")
        return None

def get_driving_duration(origin_lnglat, dest_lnglat, key, strategy):
    """
    调用高德驾车路径规划API，返回耗时（秒）
    origin_lnglat: "lng,lat"
    dest_lnglat: "lng,lat"
    """
    url = "https://restapi.amap.com/v3/direction/driving"
    params = {
        "key": key,
        "origin": origin_lnglat,
        "destination": dest_lnglat,
        "strategy": strategy,
        "output": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = json.loads(response.text)
        if data.get("status") == "1" and len(data.get("route", {}).get("paths", [])) > 0:
            duration = int(data["route"]["paths"][0]["duration"])
            return duration
        else:
            print(f"[路径规划失败]：{data.get('info', '未知错误')}")
            return None
    except Exception as e:
        print(f"[路径规划异常]：{str(e)}")
        return None

# ====================== 主程序 ======================
def main():
    print("=== 开始地址转经纬度并计算最快路线 ===")
    
    # 先编码终点
    dest_lnglat = geocode(END_POINT, AMAP_KEY)
    if not dest_lnglat:
        print("终点地址解析失败，程序退出。")
        return

    result = []
    for addr in START_POINTS:
        time.sleep(0.5)
        lnglat = geocode(addr, AMAP_KEY)
        if not lnglat:
            continue
        duration = get_driving_duration(lnglat, dest_lnglat, AMAP_KEY, STRATEGY)
        if duration is not None:
            result.append( (duration, addr, lnglat) )
    print(result)
    # 按耗时升序排序
    result.sort(key=lambda x: x[0])

    if not result:
        print("未获取到任何有效路线。")
        return

    print("\n=== 最快路线对比结果（按耗时升序排列）===")
    for i, (rtime, addr, lnglat) in enumerate(result, 1):
        minutes = rtime // 60
        seconds = rtime % 60
        print(f"{i}. {addr} (经纬度: {lnglat}) → 预计耗时：{minutes}分{seconds}秒")

    print("\n=== 注：耗时基于高德API实时路况估算，实际以导航为准 ===")

if __name__ == "__main__":
    main()
