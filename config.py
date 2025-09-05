"""
高德地图API配置参数
"""

# 高德API密钥
AMAP_KEY = ""

# 固定终点
END_POINT = ""

# 批量起点列表
START_POINTS = [

]

# 出行方式及其对应的策略
TRAFFIC_MODES = {
    1: {"name": "驾车", "strategy": 0},  # 0=最快路线
    2: {"name": "公交", "strategy": 0},  # 0=最快捷模式
    3: {"name": "骑行", "strategy": 0},  # 0=推荐路线
    4: {"name": "步行", "strategy": 0}   # 0=推荐路线
}