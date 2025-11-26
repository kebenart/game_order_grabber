#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动抢单模块
"""

import requests
import time
from typing import List, Dict
from datetime import datetime


class OrderGrabber:
    """订单抢购器"""
    
    def __init__(self, session: requests.Session, log_callback=None):
        self.session = session
        self.is_running = False
        self.log_callback = log_callback  # GUI日志回调函数
        # SteamPy API地址
        self.sale_list_url = "https://steampy.com/xboot/steamKeySale/listSale"  # 销售列表API
        self.pay_order_url = "https://steampy.com/xboot/steamKeyOrder/payOrder"  # 支付下单API
    
    def _log(self, message: str, level: str = "INFO"):
        """输出日志"""
        if self.log_callback:
            self.log_callback(message, level)
        else:
            print(message)
    
    def start(self, games: List[Dict]):
        """
        开始抢单
        
        Args:
            games: 要抢单的游戏列表
        """
        self.is_running = True
        success_count = 0
        fail_count = 0
        
        self._log(f"开始监控 {len(games)} 个游戏...")
        
        while self.is_running:
            for game in games:
                if not self.is_running:
                    break
                
                game_name = game.get('name', '未知游戏')
                game_id = game.get('id')
                
                try:
                    # 检查游戏是否可购买
                    if self._check_availability(game):
                        self._log(f"✓ {game_name} 可购买，正在抢单...")
                        
                        # 尝试抢单
                        if self._grab_order(game):
                            success_count += 1
                            self._log(f"✓✓✓ 成功抢到: {game_name}", "SUCCESS")
                            
                            # 抢单成功后，可以选择继续或退出
                            # 这里选择继续监控其他游戏
                        else:
                            fail_count += 1
                            self._log(f"✗ 抢单失败: {game_name}", "ERROR")
                    else:
                        # 游戏不可购买，继续监控（GUI模式下减少输出频率）
                        if not self.log_callback:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ {game_name} 暂不可购买，继续监控...", end='\r')
                
                except Exception as e:
                    self._log(f"✗ 处理 {game_name} 时出错: {e}", "ERROR")
                    fail_count += 1
                
                # 短暂延迟，避免请求过于频繁
                time.sleep(1)
            
            # 一轮检查完成后的延迟
            if self.is_running:
                time.sleep(2)
        
        self._log(f"\n抢单统计: 成功 {success_count} 个，失败 {fail_count} 个")
    
    def stop(self):
        """停止抢单"""
        self.is_running = False
    
    def get_sale_list(self, game_id: str) -> List[Dict]:
        """
        获取游戏销售列表
        
        Args:
            game_id: 游戏ID
            
        Returns:
            销售列表，按价格排序（第一条为最低价）
        """
        try:
            params = {
                'pageNumber': 1,
                'pageSize': 20,
                'sort': 'keyPrice',
                'order': 'asc',
                'startDate': '',
                'endDate': '',
                'gameId': game_id
            }
            
            # 记录请求信息（listSale接口 - 查询销售列表）
            full_url = f"{self.sale_list_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            self._log("=" * 80, "INFO")
            self._log(f"[listSale请求] URL: {self.sale_list_url}", "INFO")
            self._log(f"[listSale请求] Method: GET", "INFO")
            self._log(f"[listSale请求] Headers: {dict(self.session.headers)}", "INFO")
            self._log(f"[listSale请求] Params: {params}", "INFO")
            self._log(f"[listSale请求] Full URL: {full_url}", "INFO")
            self._log("=" * 80, "INFO")
            
            response = self.session.get(
                self.sale_list_url,
                params=params,
                timeout=10
            )
            
            # 记录响应信息
            self._log("=" * 80, "INFO")
            self._log(f"[listSale响应] 状态码: {response.status_code}", "INFO")
            self._log(f"[listSale响应] Headers: {dict(response.headers)}", "INFO")
            
            response.raise_for_status()
            data = response.json()
            
            # 记录响应内容
            import json as json_module
            response_json_str = json_module.dumps(data, ensure_ascii=False, indent=2)
            if len(response_json_str) > 2000:
                self._log(f"[listSale响应] Body (前2000字符):\n{response_json_str[:2000]}...", "INFO")
                self._log(f"[listSale响应] Body (完整内容，共{len(response_json_str)}字符):\n{response_json_str}", "INFO")
            else:
                self._log(f"[listSale响应] Body:\n{response_json_str}", "INFO")
            
            # 解析并打印关键信息
            success = data.get('success', False)
            code = data.get('code', '')
            message = data.get('message', '')
            self._log(f"[listSale响应] success: {success}", "INFO")
            self._log(f"[listSale响应] code: {code}", "INFO")
            self._log(f"[listSale响应] message: {message}", "INFO")
            
            if success:
                result = data.get('result', {})
                content = result.get('content', [])
                self._log(f"[listSale响应] 销售记录数量: {len(content)}", "INFO")
                if content:
                    lowest_sale = content[0]
                    sale_id = lowest_sale.get('saleId') or lowest_sale.get('id', '')
                    self._log(f"[listSale响应] 最低价: ¥{lowest_sale.get('keyPrice', 0)}, saleId: {sale_id}", "INFO")
            
            self._log("=" * 80, "INFO")
            
            if not data.get('success', False):
                error_msg = data.get('message', '未知错误')
                code = data.get('code', '')
                self._log(f"获取销售列表失败: {error_msg} (code: {code})", "ERROR")
                return []
            
            result = data.get('result', {})
            content = result.get('content', [])
            
            # 解析销售列表
            sales = []
            for item in content:
                # listSale返回的数据中，saleId字段可能直接是saleId，也可能是id
                sale_id = item.get('saleId') or item.get('id')
                sale_info = {
                    'saleId': sale_id,
                    'keyPrice': item.get('keyPrice'),
                    'seller': item.get('seller'),
                    'keyTx': item.get('keyTx', 0)
                }
                sales.append(sale_info)
            
            self._log(f"[HTTP请求] 成功获取 {len(sales)} 条销售记录", "INFO")
            return sales
            
        except requests.exceptions.RequestException as e:
            error_msg = f"获取销售列表请求失败: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" (状态码: {e.response.status_code})"
                try:
                    error_body = e.response.text[:500]
                    self._log(f"[HTTP错误响应] {error_body}", "ERROR")
                except:
                    pass
            self._log(error_msg, "ERROR")
            return []
        except Exception as e:
            import traceback
            error_msg = f"获取销售列表失败: {str(e)}\n{traceback.format_exc()}"
            self._log(error_msg, "ERROR")
            return []
    
    def _check_availability(self, game: Dict) -> bool:
        """
        检查游戏是否可购买（通过销售列表）
        
        Args:
            game: 游戏信息
            
        Returns:
            是否可购买
        """
        try:
            game_id = game.get('id')
            sales = self.get_sale_list(game_id)
            return len(sales) > 0
        except Exception as e:
            error_msg = f"检查可用性失败: {str(e)}"
            self._log(error_msg, "ERROR")
            return False
    
    def _grab_order(self, game: Dict, sale_id: str) -> bool:
        """
        抢单（支付下单）
        
        Args:
            game: 游戏信息
            sale_id: 销售ID
            
        Returns:
            是否成功
        """
        try:
            # 准备表单参数
            data = {
                'saleId': sale_id,
                'payType': 'AL',  # 支付宝
                'promoCodeId': '',
                'walletFlag': ''
            }
            
            # 记录请求信息
            self._log("=" * 80, "INFO")
            self._log(f"[payOrder请求] URL: {self.pay_order_url}", "INFO")
            self._log(f"[payOrder请求] Method: POST", "INFO")
            self._log(f"[payOrder请求] Headers: {dict(self.session.headers)}", "INFO")
            self._log(f"[payOrder请求] Form Data: {data}", "INFO")
            self._log(f"[payOrder请求] saleId: {sale_id}", "INFO")
            self._log(f"[payOrder请求] payType: AL (支付宝)", "INFO")
            self._log("=" * 80, "INFO")
            
            response = self.session.post(
                self.pay_order_url,
                data=data,  # 使用form data
                timeout=10
            )
            
            # 记录响应信息
            self._log("=" * 80, "INFO")
            self._log(f"[payOrder响应] 状态码: {response.status_code}", "INFO")
            self._log(f"[payOrder响应] Headers: {dict(response.headers)}", "INFO")
            
            response.raise_for_status()
            result = response.json()
            
            # 记录完整响应内容
            import json as json_module
            response_json_str = json_module.dumps(result, ensure_ascii=False, indent=2)
            if len(response_json_str) > 2000:
                self._log(f"[payOrder响应] Body (前2000字符):\n{response_json_str[:2000]}...", "INFO")
                self._log(f"[payOrder响应] Body (完整内容，共{len(response_json_str)}字符，已保存到日志)", "INFO")
                # 如果内容过长，也打印完整内容（但可能被截断）
                self._log(f"[payOrder响应] Body (完整):\n{response_json_str}", "INFO")
            else:
                self._log(f"[payOrder响应] Body:\n{response_json_str}", "INFO")
            
            # 解析并打印关键信息
            success = result.get('success', False)
            code = result.get('code', '')
            message = result.get('message', '')
            self._log(f"[payOrder响应] success: {success}", "INFO")
            self._log(f"[payOrder响应] code: {code}", "INFO")
            self._log(f"[payOrder响应] message: {message}", "INFO")
            
            if success:
                result_data = result.get('result', {})
                order_id = result_data.get('orderId', '')
                pay_price = result_data.get('payPrice', 0)
                self._log(f"[payOrder响应] orderId: {order_id}", "INFO")
                self._log(f"[payOrder响应] payPrice: {pay_price}", "INFO")
            
            self._log("=" * 80, "INFO")
            
            if not result.get('success', False):
                error_msg = result.get('message', '未知错误')
                code = result.get('code', '')
                self._log(f"抢单失败: {error_msg} (code: {code})", "ERROR")
                return False
            
            # 抢单成功
            order_id = result.get('result', {}).get('orderId', '')
            pay_price = result.get('result', {}).get('payPrice', 0)
            self._log(f"抢单成功！订单号: {order_id}, 支付金额: ¥{pay_price}", "SUCCESS")
            
            # 这里可以处理支付表单（如果需要自动支付）
            form_html = result.get('result', {}).get('form', '')
            if form_html:
                self._log("已生成支付表单，请完成支付", "INFO")
            
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = f"抢单请求失败: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" (状态码: {e.response.status_code})"
                try:
                    # 记录错误响应的内容
                    error_body = e.response.text[:500]
                    self._log(f"[HTTP错误响应] {error_body}", "ERROR")
                    # 尝试解析JSON
                    try:
                        error_json = e.response.json()
                        self._log(f"[HTTP错误响应] JSON: {error_json}", "ERROR")
                    except:
                        pass
                except:
                    pass
            self._log(error_msg, "ERROR")
            import traceback
            self._log(f"[异常堆栈] {traceback.format_exc()}", "ERROR")
            return False
        except requests.exceptions.HTTPError as e:
            error_msg = f"抢单HTTP错误: {e.response.status_code} - {str(e)}"
            try:
                error_body = e.response.text[:500]
                self._log(f"[HTTP错误响应] {error_body}", "ERROR")
            except:
                pass
            self._log(error_msg, "ERROR")
            return False
        except Exception as e:
            import traceback
            error_msg = f"抢单过程出错: {str(e)}\n{traceback.format_exc()}"
            self._log(error_msg, "ERROR")
            return False

