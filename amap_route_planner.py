import requests
import time
import json
import csv

# ====================== 导入配置 ======================
from config import AMAP_KEY, END_POINT, START_POINTS, TRAFFIC_MODES

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
    """获取驾车路线耗时（秒）"""
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
            distance = int(data["route"]["paths"][0]["distance"])
            return duration, distance
        else:
            print(f"[驾车路线规划失败]：{data.get('info', '未知错误')}")
            return None, None
    except Exception as e:
        print(f"[驾车路线规划异常]：{str(e)}")
        return None, None

def get_transit_duration(origin_lnglat, dest_lnglat, key, strategy):
    """获取公交路线耗时（秒）"""
    url = "https://restapi.amap.com/v3/direction/transit/integrated"
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
        if data.get("status") == "1" and len(data.get("route", {}).get("transits", [])) > 0:
            duration = int(data["route"]["transits"][0]["duration"])
            distance = int(data["route"]["transits"][0]["distance"])
            return duration, distance
        else:
            print(f"[公交路线规划失败]：{data.get('info', '未知错误')}")
            return None, None
    except Exception as e:
        print(f"[公交路线规划异常]：{str(e)}")
        return None, None

def get_bicycling_duration(origin_lnglat, dest_lnglat, key, strategy):
    """获取骑行路线耗时（秒）"""
    url = "https://restapi.amap.com/v4/direction/bicycling"
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
        if data.get("status") == "1" and len(data.get("data", {}).get("paths", [])) > 0:
            duration = int(data["data"]["paths"][0]["duration"])
            distance = int(data["data"]["paths"][0]["distance"])
            return duration, distance
        else:
            print(f"[骑行路线规划失败]：{data.get('info', '未知错误')}")
            return None, None
    except Exception as e:
        print(f"[骑行路线规划异常]：{str(e)}")
        return None, None

def get_walking_duration(origin_lnglat, dest_lnglat, key, strategy):
    """获取步行路线耗时（秒）"""
    url = "https://restapi.amap.com/v3/direction/walking"
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
            distance = int(data["route"]["paths"][0]["distance"])
            return duration, distance
        else:
            print(f"[步行路线规划失败]：{data.get('info', '未知错误')}")
            return None, None
    except Exception as e:
        print(f"[步行路线规划异常]：{str(e)}")
        return None, None

# 根据出行方式获取对应的函数
def get_duration_function(mode):
    if mode == 1:
        return get_driving_duration
    elif mode == 2:
        return get_transit_duration
    elif mode == 3:
        return get_bicycling_duration
    elif mode == 4:
        return get_walking_duration
    else:
        return None

# ====================== 主程序 ======================
def main():
    print("=== 开始地址转经纬度并计算路线 ===")
    
    # 显示出行方式选项
    print("\n请选择出行方式：")
    for key, value in TRAFFIC_MODES.items():
        print(f"{key}. {value['name']}")
    
    # 获取用户选择
    while True:
        try:
            choice = int(input("请输入选项 (1-4): "))
            if choice in TRAFFIC_MODES:
                break
            else:
                print("请输入有效的选项 (1-4)")
        except ValueError:
            print("请输入有效的数字")
    
    # 获取选择的出行方式信息
    selected_mode = TRAFFIC_MODES[choice]
    print(f"\n您选择的是：{selected_mode['name']}")
    
    # 先编码终点
    dest_lnglat = geocode(END_POINT, AMAP_KEY)
    if not dest_lnglat:
        print("终点地址解析失败，程序退出。")
        return

    # 获取对应的路线规划函数
    duration_func = get_duration_function(choice)
    if not duration_func:
        print("无效的出行方式，程序退出。")
        return

    result = []
    for addr in START_POINTS:
        time.sleep(0.5)  # 避免请求过于频繁
        lnglat = geocode(addr, AMAP_KEY)
        if not lnglat:
            continue
        duration, distance = duration_func(lnglat, dest_lnglat, AMAP_KEY, selected_mode["strategy"])
        if duration is not None and distance is not None:
            result.append( (duration, distance, addr, lnglat) )

    # 按耗时升序排序
    result.sort(key=lambda x: x[0])

    if not result:
        print("未获取到任何有效路线。")
        return

    print(f"\n=== {selected_mode['name']}路线对比结果（按耗时升序排列）===")
    csv_str = """序号,地址,经纬度,耗时,距离\n"""
    for i, (rtime, distance, addr, lnglat) in enumerate(result, 1):
        # 格式化时间
        hours = rtime // 3600
        minutes = (rtime % 3600) // 60
        seconds = rtime % 60
        
        # 格式化距离
        if distance >= 1000:
            distance_str = f"{distance/1000:.1f}公里"
        else:
            distance_str = f"{distance}米"
            
        # 输出结果
        time_str = ""
        if hours > 0:
            time_str += f"{hours}小时"
        if minutes > 0:
            time_str += f"{minutes}分"
        time_str += f"{seconds}秒"
        csv_str += f"{i},{addr},{lnglat},{time_str},{distance_str}\n"
        print(f"{i}. {addr} (经纬度: {lnglat}) → 预计耗时：{time_str}，距离：{distance_str}")
    # 将结果导出到CSV文件
    with open(f'{time.strftime("%Y%m%d%H%M%S")} route_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(csv_str)
    print(f"\n=== 注：结果基于高德API估算，实际以导航为准 ===")

if __name__ == "__main__":
    main()
