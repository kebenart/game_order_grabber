#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏搜索模块
"""

import requests
from typing import List, Dict
import time
from urllib.parse import quote


class GameSearcher:
    """游戏搜索器"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        # SteamPy搜索API
        self.search_url = "https://steampy.com/xboot/steamGame/keyByName"
    
    def search(self, keyword: str) -> List[Dict]:
        """
        搜索游戏
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            游戏列表
        """
        try:
            # 准备请求参数
            params = {
                'pageNumber': 1,
                'pageSize': 30,
                'sort': 'keyTx',
                'order': 'asc',
                'startDate': '',
                'endDate': '',
                'gameName': keyword,  # 游戏名称，API会自动处理URL编码
                'gameUrl': ''
            }
            
            # 发送请求
            response = self.session.get(
                self.search_url,
                params=params,
                timeout=10
            )
            
            # 检查响应状态
            response.raise_for_status()
            data = response.json()
            
            # 检查API返回状态
            if not data.get('success', False):
                error_msg = data.get('message', '未知错误')
                code = data.get('code', 0)
                full_error = f"API返回错误 (code: {code}): {error_msg}"
                print(f"✗ {full_error}")
                # 如果有关联的GUI，记录到日志
                if hasattr(self.session, '_gui_log_callback'):
                    self.session._gui_log_callback(full_error, "ERROR")
                if code == 401:
                    auth_error = "未登录，请检查accesstoken是否正确"
                    print(f"✗ {auth_error}")
                    if hasattr(self.session, '_gui_log_callback'):
                        self.session._gui_log_callback(auth_error, "ERROR")
                return []
            
            # 解析搜索结果
            return self._parse_search_results(data)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"搜索请求失败: {str(e)}"
            print(f"✗ {error_msg}")
            # 如果有关联的GUI，记录到日志
            if hasattr(self.session, '_gui_log_callback'):
                self.session._gui_log_callback(error_msg, "ERROR")
            return []
        except requests.exceptions.HTTPError as e:
            error_msg = f"搜索HTTP错误: {e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'} - {str(e)}"
            print(f"✗ {error_msg}")
            if hasattr(self.session, '_gui_log_callback'):
                self.session._gui_log_callback(error_msg, "ERROR")
            return []
        except Exception as e:
            error_msg = f"搜索过程出错: {str(e)}"
            print(f"✗ {error_msg}")
            # 如果有关联的GUI，记录到日志
            if hasattr(self.session, '_gui_log_callback'):
                self.session._gui_log_callback(error_msg, "ERROR")
            return []
    
    def _parse_search_results(self, data: Dict) -> List[Dict]:
        """解析搜索结果"""
        games = []
        
        # 检查返回数据结构
        if not data.get('success', False):
            return games
        
        result = data.get('result', {})
        if not result:
            return games
        
        content = result.get('content', [])
        if not content:
            return games
        
        # 解析每个游戏
        for item in content:
            # 获取游戏ID
            game_id = item.get('id', '')
            
            # 获取游戏名称（优先使用中文名）
            # 处理None值：如果字段值为None，使用空字符串，然后去除空白
            game_name_cn = (item.get('gameNameCn') or '').strip()
            game_name = (item.get('gameName') or '').strip()
            name = game_name_cn if game_name_cn else game_name
            if not name:
                name = '未知游戏'
            
            # 获取价格（优先使用keyPrice，如果没有则使用gamePrice）
            key_price = item.get('keyPrice')
            game_price = item.get('gamePrice')
            
            # 格式化价格
            if key_price is not None:
                price = f"¥{key_price:.2f}"
            elif game_price is not None:
                price = f"¥{game_price:.2f}"
            else:
                price = "N/A"
            
            # 判断是否可购买（gameStatus为"1"表示可购买）
            game_status = item.get('gameStatus', '')
            available = game_status == "1"
            
            # 获取其他信息
            app_id = item.get('appId') or ''
            game_url = item.get('gameUrl') or ''
            key_tx = item.get('keyTx') or 0  # 交易数量
            
            # 获取图片URL
            game_ava = item.get('gameAva') or ''
            game_ava_lib = item.get('gameAvaLib') or ''
            image_url = game_ava or game_ava_lib
            
            # 构建游戏信息字典
            game_info = {
                'id': game_id,
                'name': name,
                'price': price,
                'url': game_url,
                'available': available,
                'appId': app_id,
                'keyTx': key_tx,
                'gameStatus': game_status,
                'keyPrice': key_price,
                'gamePrice': game_price,
                'gameName': game_name or '',
                'gameNameCn': game_name_cn or '',
                'gameAva': game_ava,
                'gameAvaLib': game_ava_lib,
                'imageUrl': image_url
            }
            
            games.append(game_info)
        
        return games
