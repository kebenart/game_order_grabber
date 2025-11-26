#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏抢单系统GUI界面 - PySide6版本
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QMessageBox, QFileDialog, QHeaderView, QCheckBox, QScrollArea,
    QListWidget, QListWidgetItem, QFrame, QSpinBox, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QUrl
from PySide6.QtGui import QColor, QPixmap, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import threading
import os
import json
import smtplib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.header import Header
import requests
from game_searcher import GameSearcher
from order_grabber import OrderGrabber
import appdirs

# 设置应用数据目录
APP_NAME = "game_order_grabber"
APP_AUTHOR = "GameOrderGrabber"
DATA_DIR = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
CONFIG_DIR = os.path.join(DATA_DIR, "config")

# 确保配置目录存在
os.makedirs(CONFIG_DIR, exist_ok=True)


class ImageLoadThread(QThread):
    """图片加载线程"""
    image_loaded = Signal(object, QPixmap)  # widget, pixmap
    
    def __init__(self, session, image_url, widget, game_name):
        super().__init__()
        self.session = session
        self.image_url = image_url
        self.widget = widget
        self.game_name = game_name
    
    def run(self):
        try:
            # 检查是否被中断
            if self.isInterruptionRequested():
                return
            
            response = self.session.get(self.image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            # 再次检查是否被中断
            if self.isInterruptionRequested():
                return
            
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content) and not pixmap.isNull():
                    if not self.isInterruptionRequested():
                        self.image_loaded.emit(self.widget, pixmap)
        except Exception as e:
            pass  # 静默失败，避免日志过多


class GameItemWidget(QWidget):
    """游戏项自定义Widget"""
    grab_clicked = Signal(dict)  # 发送游戏数据
    
    def __init__(self, game_data: Dict, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.image_thread = None  # 图片加载线程引用
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        layout.setSpacing(8)  # 减小间距
        
        # 游戏图片（缩小到原来的1/2）
        self.image_label = QLabel()
        self.image_label.setFixedSize(60, 80)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("加载中...")
        layout.addWidget(self.image_label)
        
        # 游戏信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        # 游戏名称（缩小字体）
        name_label = QLabel(self.game_data.get('name', '未知游戏'))
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)  # 允许换行
        info_layout.addWidget(name_label)
        
        # 价格（缩小字体）
        price_label = QLabel(f"价格: {self.game_data.get('price', 'N/A')}")
        price_font = QFont()
        price_font.setPointSize(10)
        price_label.setFont(price_font)
        price_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        info_layout.addWidget(price_label)
        
        # 状态（缩小字体）
        status = self.game_data.get('available', False)
        status_text = "可购买" if status else "不可购买"
        status_label = QLabel(f"状态: {status_text}")
        status_label.setStyleSheet(f"color: {'green' if status else 'gray'}; font-size: 9pt;")
        info_layout.addWidget(status_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout, stretch=1)
        
        # 抢单按钮（缩小）
        self.grab_btn = QPushButton("抢单")
        self.grab_btn.setFixedSize(60, 30)
        self.grab_btn.setEnabled(status)  # 只有可购买的游戏才能抢单
        self.grab_btn.clicked.connect(lambda: self.grab_clicked.emit(self.game_data))
        layout.addWidget(self.grab_btn)
    
    def set_image(self, pixmap: QPixmap):
        """设置游戏图片"""
        if pixmap.isNull():
            self.image_label.setText("加载失败")
            return
        scaled_pixmap = pixmap.scaled(60, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")  # 清除"加载中..."文本


class SearchThread(QThread):
    """搜索游戏线程"""
    finished = Signal(list)
    error = Signal(str)
    
    def __init__(self, game_searcher, keyword):
        super().__init__()
        self.game_searcher = game_searcher
        self.keyword = keyword
    
    def run(self):
        try:
            games = self.game_searcher.search(self.keyword)
            self.finished.emit(games)
        except Exception as e:
            self.error.emit(str(e))


class DonateDialog(QDialog):
    """捐赠对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("捐赠支持")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("感谢您的支持！")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #4caf50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 项目信息
        project_info = QLabel(
            "<b>项目信息</b><br>"
            "游戏抢单系统 - 自动监控游戏价格并抢单<br>"
            "支持多游戏并发监控，价格达到目标时自动抢单<br>"
            "项目开源，持续更新中..."
        )
        project_info.setWordWrap(True)
        project_info.setStyleSheet("color: #333; font-size: 12pt; padding: 15px; background-color: #f5f5f5; border-radius: 5px;")
        layout.addWidget(project_info)
        
        # 捐赠感言
        donate_message = QLabel(
            "<b>捐赠感言</b><br>"
            "如果您觉得这个项目对您有帮助，欢迎捐赠支持！<br>"
            "您的支持是我持续开发和维护的动力。<br>"
            "感谢每一位支持者的慷慨捐赠！🙏"
        )
        donate_message.setWordWrap(True)
        donate_message.setStyleSheet("color: #333; font-size: 12pt; padding: 15px; background-color: #fff3e0; border-radius: 5px;")
        layout.addWidget(donate_message)
        
        # 二维码图片
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setStyleSheet("border: 2px solid #ddd; border-radius: 5px; padding: 10px; background-color: white;")
        
        # 尝试加载二维码图片 - 打包后的路径处理
        if getattr(sys, 'frozen', False):
            # 打包后的exe
            base_path = sys._MEIPASS
        else:
            # 开发环境
            base_path = os.path.dirname(__file__)
        qr_image_path = os.path.join(base_path, "donate_qr.png")
        if os.path.exists(qr_image_path):
            pixmap = QPixmap(qr_image_path)
            if not pixmap.isNull():
                # 限制二维码大小
                scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                qr_label.setPixmap(scaled_pixmap)
            else:
                qr_label.setText("二维码图片加载失败\n请确保 donate_qr.png 文件存在且格式正确")
                qr_label.setStyleSheet("border: 2px solid #ddd; border-radius: 5px; padding: 20px; background-color: white; color: #999;")
        else:
            qr_label.setText(
                "二维码图片未找到\n\n"
                "请将二维码图片保存为 donate_qr.png\n"
                "并放置在项目根目录下"
            )
            qr_label.setStyleSheet("border: 2px solid #ddd; border-radius: 5px; padding: 20px; background-color: white; color: #999;")
        
        layout.addWidget(qr_label)
        
        # 提示文字
        tip_label = QLabel("请使用支付宝扫描上方二维码进行捐赠")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("color: #666; font-size: 11pt;")
        layout.addWidget(tip_label)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 10px; font-size: 12pt; border-radius: 5px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class GrabbingItemWidget(QWidget):
    """抢单列表项Widget"""
    stop_clicked = Signal(dict)  # 发送游戏数据
    pause_clicked = Signal(dict)  # 暂停信号
    resume_clicked = Signal(dict)  # 恢复信号
    target_price_changed = Signal(dict, float)  # 目标价格改变信号
    finish_clicked = Signal(dict)  # 完成按钮点击信号（删除本条记录）
    
    def __init__(self, game_data: Dict, grab_price: str, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.grab_price = grab_price  # 加入时的价格
        self.current_min_price = grab_price  # 当前最低价
        self.status = "正在抢单"  # 状态：暂停/正在抢单/抢单成功
        self.image_thread = None
        self.init_ui()
    
    def get_target_price(self) -> float:
        """获取目标价格，如果为空则返回0（表示使用30%规则）"""
        text = self.target_price_input.text().strip()
        if not text:
            return 0
        try:
            return float(text)
        except:
            return 0
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 游戏图片
        self.image_label = QLabel()
        self.image_label.setFixedSize(60, 80)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("加载中...")
        layout.addWidget(self.image_label)
        
        # 游戏信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # 游戏名称
        name_label = QLabel(self.game_data.get('name', '未知游戏'))
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # 加入时价格
        grab_price_label = QLabel(f"加入时价格: {self.grab_price}")
        grab_price_label.setStyleSheet("color: #666; font-size: 9pt;")
        info_layout.addWidget(grab_price_label)
        
        # 目标价格设置
        target_price_layout = QHBoxLayout()
        target_price_label = QLabel("目标价格:")
        target_price_label.setStyleSheet("color: #666; font-size: 9pt;")
        target_price_label.setFixedWidth(70)
        target_price_layout.addWidget(target_price_label)
        
        self.target_price_input = QLineEdit()
        self.target_price_input.setPlaceholderText("留空则使用默认百分比")
        self.target_price_input.setFixedWidth(80)
        self.target_price_input.setStyleSheet("font-size: 9pt;")
        # 从game_data中获取目标价格
        target_price = self.game_data.get('target_price', '')
        if target_price:
            self.target_price_input.setText(str(target_price))
        # 当目标价格改变时，更新game_data并发送信号
        self.target_price_input.textChanged.connect(self._on_target_price_changed)
        target_price_layout.addWidget(self.target_price_input)
        target_price_layout.addStretch()
        info_layout.addLayout(target_price_layout)
        
        # 当前最低价
        self.min_price_label = QLabel(f"当前最低价: {self.current_min_price}")
        self.min_price_label.setStyleSheet("color: #d32f2f; font-size: 9pt; font-weight: bold;")
        info_layout.addWidget(self.min_price_label)
        
        # 抢单状态
        self.status_label = QLabel(f"状态: {self.status}")
        self.status_label.setStyleSheet("color: #2196F3; font-size: 9pt; font-weight: bold;")
        info_layout.addWidget(self.status_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout, stretch=1)
        
        # 控制按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(5)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setFixedSize(60, 25)
        self.pause_btn.clicked.connect(lambda: self.pause_clicked.emit(self.game_data))
        btn_layout.addWidget(self.pause_btn)
        
        self.resume_btn = QPushButton("继续")
        self.resume_btn.setFixedSize(60, 25)
        self.resume_btn.setStyleSheet("background-color: #4caf50; color: white;")
        self.resume_btn.clicked.connect(lambda: self.resume_clicked.emit(self.game_data))
        self.resume_btn.hide()  # 初始隐藏
        btn_layout.addWidget(self.resume_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFixedSize(60, 25)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(lambda: self.stop_clicked.emit(self.game_data))
        btn_layout.addWidget(self.stop_btn)
        
        # 完成按钮（抢单成功时显示）
        self.finish_btn = QPushButton("完成")
        self.finish_btn.setFixedSize(60, 25)
        self.finish_btn.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
        self.finish_btn.clicked.connect(lambda: self.finish_clicked.emit(self.game_data))
        self.finish_btn.hide()  # 初始隐藏
        btn_layout.addWidget(self.finish_btn)
        
        layout.addLayout(btn_layout)
    
    def set_image(self, pixmap: QPixmap):
        """设置游戏图片"""
        if pixmap.isNull():
            self.image_label.setText("加载失败")
            return
        scaled_pixmap = pixmap.scaled(60, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")
    
    def update_status(self, status: str):
        """更新抢单状态"""
        self.status = status
        color_map = {
            "暂停": "#ff9800",
            "正在抢单": "#2196F3",
            "抢单成功": "#4caf50"
        }
        color = color_map.get(status, "#666")
        self.status_label.setText(f"状态: {status}")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 9pt; font-weight: bold;")
        
        # 更新按钮显示
        if status == "抢单成功":
            # 抢单成功时，隐藏暂停/继续/停止按钮，显示完成按钮
            self.pause_btn.hide()
            self.resume_btn.hide()
            self.stop_btn.hide()
            self.finish_btn.show()
            # 禁用目标价格输入
            self.target_price_input.setEnabled(False)
        elif status == "暂停":
            # 暂停时，显示继续和停止按钮
            self.pause_btn.hide()
            self.resume_btn.show()
            self.stop_btn.show()
            self.finish_btn.hide()
            self.target_price_input.setEnabled(True)
        else:
            # 正在抢单时，显示暂停和停止按钮
            self.pause_btn.show()
            self.resume_btn.hide()
            self.stop_btn.show()
            self.finish_btn.hide()
            self.target_price_input.setEnabled(True)
    
    def update_min_price(self, price: str):
        """更新当前最低价"""
        self.current_min_price = price
        self.min_price_label.setText(f"当前最低价: {price}")
    
    def _on_target_price_changed(self):
        """目标价格改变时的回调"""
        target_price = self.get_target_price()
        self.game_data['target_price'] = target_price if target_price > 0 else ''
        self.target_price_changed.emit(self.game_data, target_price)


class GrabThread(QThread):
    """抢单线程"""
    log_message = Signal(str, str)  # message, level
    status_update = Signal(dict, str)  # game_data, status
    price_update = Signal(dict, str)  # game_data, price
    grab_success = Signal(dict)  # game_data
    
    def __init__(self, order_grabber, game_data, widget_ref, request_interval=3, target_price_percentage=70):
        super().__init__()
        self.order_grabber = order_grabber
        self.game_data = game_data
        self.widget_ref = widget_ref  # 保持Widget引用
        self.is_paused = False
        self.request_interval = request_interval  # 请求间隔（秒）
        self.target_price_percentage = max(10, min(100, target_price_percentage))  # 目标价格百分比，限制在10-100之间
    
    def pause(self):
        """暂停抢单"""
        self.is_paused = True
        self.status_update.emit(self.game_data, "暂停")
    
    def resume(self):
        """恢复抢单"""
        self.is_paused = False
        self.status_update.emit(self.game_data, "正在抢单")
    
    def update_percentage(self, percentage: int):
        """更新目标价格百分比"""
        self.target_price_percentage = max(10, min(100, percentage))
    
    def run(self):
        try:
            # 创建日志回调函数
            def log_callback(message: str, level: str = "INFO"):
                self.log_message.emit(message, level)
            
            self.order_grabber.log_callback = log_callback
            self.status_update.emit(self.game_data, "正在抢单")
            
            # 获取加入时的价格（用于比较）
            grab_price_str = self.game_data.get('grab_price', self.game_data.get('price', '0'))
            # 提取数字部分
            try:
                grab_price = float(grab_price_str.replace('¥', '').replace(',', '').strip())
            except:
                grab_price = 0
            
            # 开始抢单循环
            while not self.isInterruptionRequested():
                if self.is_paused:
                    self.msleep(1000)
                    continue
                
                try:
                    game_id = self.game_data.get('id')
                    if not game_id:
                        self.log_message.emit("游戏ID不存在", "ERROR")
                        break
                    
                    # 获取销售列表
                    sales = self.order_grabber.get_sale_list(game_id)
                    
                    if not sales:
                        self.log_message.emit(f"⏳ {self.game_data.get('name', '未知')} 暂无销售，继续监控...", "INFO")
                        self.msleep(self.request_interval * 1000)
                        continue
                    
                    # 获取最低价（第一条）
                    lowest_sale = sales[0]
                    lowest_price = lowest_sale.get('keyPrice', 0)
                    sale_id = lowest_sale.get('saleId', '')
                    
                    # 调试日志：检查sale_id
                    self.log_message.emit(
                        f"[调试] {self.game_data.get('name', '未知')} - 最低价: ¥{lowest_price:.2f}, saleId: {sale_id}",
                        "INFO"
                    )
                    
                    # 更新当前最低价显示
                    price_str = f"¥{lowest_price:.2f}"
                    self.price_update.emit(self.game_data, price_str)
                    
                    # 获取目标价格（优先从widget实时获取，否则从game_data）
                    target_price_value = 0
                    if hasattr(self.widget_ref, 'get_target_price'):
                        # 从widget实时获取目标价格
                        target_price_value = self.widget_ref.get_target_price()
                    else:
                        # 从game_data获取
                        target_price_value = self.game_data.get('target_price', 0)
                        if isinstance(target_price_value, str):
                            try:
                                target_price_value = float(target_price_value) if target_price_value else 0
                            except:
                                target_price_value = 0
                        elif not isinstance(target_price_value, (int, float)):
                            target_price_value = 0
                    
                    # 同时更新game_data中的目标价格（保持同步）
                    if target_price_value > 0:
                        self.game_data['target_price'] = target_price_value
                    else:
                        self.game_data['target_price'] = ''
                    
                    # 计算目标百分比价格
                    percentage_decimal = self.target_price_percentage / 100.0
                    price_threshold = grab_price * percentage_decimal if grab_price > 0 else 0
                    
                    # 调试日志：价格比较信息
                    self.log_message.emit(
                        f"[调试] {self.game_data.get('name', '未知')} - 加入价: ¥{grab_price:.2f}, "
                        f"当前价: ¥{lowest_price:.2f}, 目标价: {'¥' + str(target_price_value) if target_price_value > 0 else '未设置'}, "
                        f"{self.target_price_percentage}%价: ¥{price_threshold:.2f}",
                        "INFO"
                    )
                    
                    # 判断是否满足抢单条件：低于目标价格 OR 低于或等于加入价格的配置百分比
                    should_grab = False
                    grab_reason = ""
                    
                    if target_price_value > 0 and lowest_price <= target_price_value:
                        # 使用自定义目标价格
                        should_grab = True
                        grab_reason = f"当前价: ¥{lowest_price:.2f} <= 目标价: ¥{target_price_value:.2f}"
                    elif price_threshold > 0 and lowest_price <= price_threshold:
                        # 使用配置的百分比规则
                        should_grab = True
                        grab_reason = f"当前价: ¥{lowest_price:.2f} <= {self.target_price_percentage}%价: ¥{price_threshold:.2f}"
                    
                    # 调试日志：判断结果
                    self.log_message.emit(
                        f"[调试] {self.game_data.get('name', '未知')} - should_grab: {should_grab}, sale_id存在: {bool(sale_id)}",
                        "INFO"
                    )
                    
                    if should_grab:
                        self.log_message.emit(
                            f"✓ {self.game_data.get('name', '未知')} 价格满足条件！{grab_reason}，开始抢单...",
                            "INFO"
                        )
                        
                        # 检查sale_id是否存在
                        if not sale_id:
                            self.log_message.emit(
                                f"✗ {self.game_data.get('name', '未知')} saleId为空，无法抢单！",
                                "ERROR"
                            )
                            self.is_paused = True
                            self.status_update.emit(self.game_data, "暂停")
                            break
                        
                        # 尝试抢单
                        success_price_candidate = lowest_price
                        self.log_message.emit(
                            f"[调试] 准备调用payOrder接口，saleId: {sale_id}",
                            "INFO"
                        )
                        if self.order_grabber._grab_order(self.game_data, sale_id):
                            self.game_data['last_success_price'] = success_price_candidate
                            self.log_message.emit(f"✓✓✓ 成功抢到: {self.game_data.get('name', '未知')}", "SUCCESS")
                            self.status_update.emit(self.game_data, "抢单成功")
                            self.grab_success.emit(self.game_data)
                            break
                        else:
                            self.log_message.emit(f"✗ 抢单失败: {self.game_data.get('name', '未知')}，已暂停抢单", "ERROR")
                            # 抢单失败后暂停
                            self.is_paused = True
                            self.status_update.emit(self.game_data, "暂停")
                            break
                    else:
                        # 价格不满足条件，继续监控
                        if target_price_value > 0:
                            target_display = f"目标: ≤¥{target_price_value:.2f}"
                        else:
                            target_display = f"目标: ≤¥{price_threshold:.2f} ({self.target_price_percentage}%)"
                        # 减少日志输出频率，避免日志过多
                        # self.log_message.emit(
                        #     f"⏳ {self.game_data.get('name', '未知')} 价格: ¥{lowest_price:.2f} "
                        #     f"({target_display})，继续监控...",
                        #     "INFO"
                        # )
                    
                    # 使用配置的请求间隔
                    self.msleep(self.request_interval * 1000)
                except requests.exceptions.RequestException as e:
                    error_msg = f"抢单请求错误: {str(e)}"
                    if hasattr(e, 'response') and e.response is not None:
                        error_msg += f" (状态码: {e.response.status_code})"
                    self.log_message.emit(error_msg, "ERROR")
                    self.msleep(self.request_interval * 1000)
                except Exception as e:
                    error_msg = f"抢单过程出错: {str(e)}"
                    self.log_message.emit(error_msg, "ERROR")
                    self.msleep(self.request_interval * 1000)
        except Exception as e:
            error_msg = f"抢单线程出错: {str(e)}"
            self.log_message.emit(error_msg, "ERROR")


class GameOrderGrabberGUI(QMainWindow):
    """游戏抢单系统GUI主类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("游戏抢单系统")
        self.setGeometry(100, 100, 900, 700)
        
        # 初始化变量
        self.token_file = os.path.join(CONFIG_DIR, "accesstoken.txt")  # 改为保存access token
        self.access_token = None
        self.cookies = {}
        self.session = requests.Session()
        self.game_searcher = None
        self.order_grabber = None
        self.is_grabbing = False
        self.grab_thread = None
        self.start_btn = None
        self.stop_btn = None
        self.search_thread = None
        self.selected_games = []
        self.games_data = {}  # 存储游戏完整数据
        self.grabbing_games = []  # 正在抢单的游戏列表
        self.game_widgets = []  # 游戏Widget列表 [(frame, widget, game_data), ...]
        self.grabbing_widgets = []  # 正在抢单的Widget列表 [(frame, widget, game_data), ...]
        self.grab_threads = {}  # 抢单线程字典 {game_id: GrabThread}
        self.grabbing_file = os.path.join(CONFIG_DIR, "grabbing_list.json")  # 抢单列表持久化文件
        self.config_file = os.path.join(CONFIG_DIR, "config.json")  # 配置文件
        self.request_interval = 3  # 默认请求间隔（秒）
        self.notification_email = ""
        self.smtp_host = ""
        self.smtp_port = 465
        self.smtp_username = ""
        self.smtp_password = ""
        self.smtp_use_ssl = True
        self.target_price_percentage = 70  # 默认低于或等于70%
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
        
        # 尝试加载登录信息
        self.load_access_token()
        
        # 加载抢单列表
        self.load_grabbing_list()
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. 顶部区域（登录信息和配置）
        top_layout = QHBoxLayout()
        
        # 登录信息区域
        login_group = QGroupBox("登录信息")
        login_layout = QVBoxLayout()
        login_group.setLayout(login_layout)
        
        login_input_layout = QHBoxLayout()
        login_input_layout.addWidget(QLabel("AccessToken:"))
        
        self.token_entry = QLineEdit()
        self.token_entry.setPlaceholderText("请输入AccessToken...")
        login_input_layout.addWidget(self.token_entry)
        
        login_btn_layout = QHBoxLayout()
        load_btn = QPushButton("加载")
        load_btn.clicked.connect(self.load_access_token)
        login_btn_layout.addWidget(load_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_access_token)
        login_btn_layout.addWidget(save_btn)
        
        login_input_layout.addLayout(login_btn_layout)
        login_layout.addLayout(login_input_layout)
        
        # 登录信息状态显示
        self.login_status_label = QLabel("未设置")
        self.login_status_label.setStyleSheet("color: gray;")
        login_layout.addWidget(self.login_status_label)
        
        # 通知邮箱配置（在token下方）
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("通知邮箱:"))
        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText("请输入要接收通知的邮箱...")
        self.email_entry.editingFinished.connect(self.on_email_changed)
        email_layout.addWidget(self.email_entry)
        login_layout.addLayout(email_layout)
        
        top_layout.addWidget(login_group, stretch=2)
        
        # 配置区域（只显示请求间隔）
        config_group = QGroupBox("配置")
        config_layout = QVBoxLayout()
        config_group.setLayout(config_layout)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("请求间隔(秒):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(self.request_interval)
        self.interval_spinbox.valueChanged.connect(self.on_interval_changed)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()
        config_layout.addLayout(interval_layout)
        
        # 目标价百分比配置
        percentage_layout = QHBoxLayout()
        percentage_layout.addWidget(QLabel("目标价百分比:"))
        self.percentage_spinbox = QSpinBox()
        self.percentage_spinbox.setRange(10, 100)
        self.percentage_spinbox.setValue(self.target_price_percentage)
        self.percentage_spinbox.setSuffix("%")
        self.percentage_spinbox.setToolTip("当前价低于或等于加入价的该百分比时触发抢单 (10-100%)")
        self.percentage_spinbox.valueChanged.connect(self.on_percentage_changed)
        percentage_layout.addWidget(self.percentage_spinbox)
        percentage_layout.addStretch()
        config_layout.addLayout(percentage_layout)
        
        # 捐赠按钮
        donate_btn = QPushButton("💝 捐赠支持")
        donate_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 8px; font-size: 11pt; border-radius: 5px; font-weight: bold;")
        donate_btn.clicked.connect(self.show_donate_dialog)
        config_layout.addWidget(donate_btn)
        
        top_layout.addWidget(config_group, stretch=1)
        main_layout.addLayout(top_layout)
        
        # 2. 游戏搜索区域
        search_group = QGroupBox("游戏搜索")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)
        
        search_layout.addWidget(QLabel("游戏名:"))
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("请输入游戏名称...")
        self.search_entry.returnPressed.connect(self.search_games)
        search_layout.addWidget(self.search_entry)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search_games)
        search_layout.addWidget(search_btn)
        
        main_layout.addWidget(search_group)
        
        # 3. 游戏列表区域（使用分割视图）
        split_layout = QHBoxLayout()
        
        # 左侧：搜索结果
        list_group = QGroupBox("搜索结果")
        list_layout = QVBoxLayout()
        list_group.setLayout(list_layout)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        # 创建容器Widget
        self.search_container = QWidget()
        self.search_layout = QVBoxLayout(self.search_container)
        self.search_layout.setAlignment(Qt.AlignTop)
        self.search_layout.setSpacing(10)
        
        scroll_area.setWidget(self.search_container)
        list_layout.addWidget(scroll_area)
        
        # 清空按钮
        clear_btn = QPushButton("清空搜索结果")
        clear_btn.clicked.connect(self.clear_game_list)
        list_layout.addWidget(clear_btn)
        
        split_layout.addWidget(list_group, stretch=2)
        
        # 右侧：正在抢单列表
        grabbing_group = QGroupBox("正在抢单")
        grabbing_layout = QVBoxLayout()
        grabbing_group.setLayout(grabbing_layout)
        
        # 创建滚动区域
        grabbing_scroll = QScrollArea()
        grabbing_scroll.setWidgetResizable(True)
        grabbing_scroll.setMinimumHeight(300)
        
        # 创建容器Widget
        self.grabbing_container = QWidget()
        self.grabbing_layout = QVBoxLayout(self.grabbing_container)
        self.grabbing_layout.setAlignment(Qt.AlignTop)
        self.grabbing_layout.setSpacing(10)
        
        grabbing_scroll.setWidget(self.grabbing_container)
        grabbing_layout.addWidget(grabbing_scroll)
        
        # 停止所有按钮
        stop_all_btn = QPushButton("停止所有")
        stop_all_btn.clicked.connect(self.stop_all_grabbing)
        grabbing_layout.addWidget(stop_all_btn)
        
        split_layout.addWidget(grabbing_group, stretch=1)
        
        main_layout.addLayout(split_layout, stretch=2)
        
        # 4. 状态标签区域（去除控制按钮）
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        main_layout.addLayout(status_layout)
        
        # 5. 日志输出区域
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        # 限制日志行数（通过document设置）
        self.log_text.document().setMaximumBlockCount(1000)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group, stretch=1)
    
    def log(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # 根据级别设置颜色
        if level == "ERROR":
            color = "red"
        elif level == "SUCCESS":
            color = "green"
        else:
            color = "black"
        
        self.log_text.append(f'<span style="color: {color};">{log_message}</span>')
    
    def load_access_token(self):
        """加载AccessToken信息"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token_str = f.read().strip()
                    if token_str:
                        self.access_token = token_str
                        self._update_session_headers()
                        self.token_entry.setText(token_str)
                        self.login_status_label.setText("✓ 登录信息已加载")
                        self.login_status_label.setStyleSheet("color: green;")
                        self.log("登录信息已从文件加载")
                        return True
            except Exception as e:
                self.log(f"加载登录信息失败: {e}", "ERROR")
                self.login_status_label.setText(f"✗ 加载失败: {e}")
                self.login_status_label.setStyleSheet("color: red;")
        
        if not self.access_token:
            self.login_status_label.setText("未设置")
            self.login_status_label.setStyleSheet("color: gray;")
        return False
    
    def save_access_token(self):
        """保存AccessToken信息"""
        token_str = self.token_entry.text().strip()
        
        if not token_str:
            QMessageBox.warning(self, "警告", "AccessToken不能为空")
            return False
        
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                f.write(token_str)
            
            self.access_token = token_str
            self._update_session_headers()
            self.login_status_label.setText("✓ 登录信息已保存")
            self.login_status_label.setStyleSheet("color: green;")
            self.log("登录信息已保存")
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存登录信息失败: {e}")
            self.log(f"保存登录信息失败: {e}", "ERROR")
            return False
    
    def import_access_token_from_file(self):
        """从文件导入AccessToken"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择AccessToken文件",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    token_str = f.read().strip()
                    self.token_entry.setText(token_str)
                    self.save_access_token()
                    QMessageBox.information(self, "成功", "登录信息已从文件导入并保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入登录信息失败: {e}")
                self.log(f"导入登录信息失败: {e}", "ERROR")
    
    def _update_session_headers(self):
        """更新session的请求头，添加accesstoken"""
        if self.access_token:
            # 将access token添加到请求头中
            self.session.headers.update({'accesstoken': self.access_token})
            self.log("已更新请求头，添加accesstoken")
    
    def search_games(self):
        """搜索游戏"""
        keyword = self.search_entry.text().strip()
        
        if not keyword:
            QMessageBox.warning(self, "警告", "请输入游戏名")
            return
        
        if not self.access_token:
            QMessageBox.warning(self, "警告", "请先设置登录信息")
            return
        
        # 清空之前的搜索结果
        self.clear_game_list()
        
        # 更新状态
        self.log(f"开始搜索游戏: {keyword}")
        self.status_label.setText("搜索中...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        # 确保请求头已更新
        self._update_session_headers()
        
        # 创建搜索线程
        if not self.game_searcher:
            self.game_searcher = GameSearcher(self.session)
        
        self.search_thread = SearchThread(self.game_searcher, keyword)
        self.search_thread.finished.connect(self.update_game_list)
        self.search_thread.error.connect(lambda e: self.on_search_error(e))
        self.search_thread.start()
    
    def on_search_error(self, error_msg: str):
        """搜索错误处理"""
        self.log(f"搜索失败: {error_msg}", "ERROR")
        self.status_label.setText("搜索失败")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def update_game_list(self, games: List[Dict]):
        """更新游戏列表"""
        # 清空现有列表
        self.clear_game_widgets()
        
        if not games:
            self.log("未找到相关游戏")
            self.status_label.setText("未找到游戏")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
            return
        
        # 添加游戏到列表
        for game in games:
            game_widget = GameItemWidget(game)
            game_widget.grab_clicked.connect(self.on_grab_button_clicked)
            
            # 添加容器（无边框）
            frame = QFrame()
            frame.setStyleSheet("margin: 2px;")  # 只保留边距，去除边框
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.addWidget(game_widget)
            
            self.search_layout.addWidget(frame)
            self.game_widgets.append((frame, game_widget, game))
            
            # 加载图片
            self.load_game_image(game_widget, game)
        
        self.log(f"找到 {len(games)} 个相关游戏")
        self.status_label.setText(f"找到 {len(games)} 个游戏")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def load_game_image(self, widget: GameItemWidget, game: Dict):
        """加载游戏图片 - 优先使用gameAvaLib"""
        # 优先使用gameAvaLib，然后是gameAva，最后是imageUrl
        image_url = game.get('gameAvaLib') or game.get('gameAva') or game.get('imageUrl') or ''
        if not image_url:
            return
        
        # 使用QThread加载图片
        image_thread = ImageLoadThread(self.session, image_url, widget, game.get('name', '未知'))
        image_thread.image_loaded.connect(self._on_image_loaded)
        image_thread.finished.connect(image_thread.deleteLater)
        image_thread.start()
        widget.image_thread = image_thread  # 保持引用避免被垃圾回收
    
    def _on_image_loaded(self, widget: GameItemWidget, pixmap: QPixmap):
        """图片加载完成回调"""
        try:
            widget.set_image(pixmap)
        except Exception as e:
            pass
    
    def on_grab_button_clicked(self, game_data: Dict):
        """处理抢单按钮点击"""
        try:
            if not self.access_token:
                QMessageBox.warning(self, "警告", "请先设置登录信息")
                return
            
            # 添加到正在抢单列表（会自动开始抢单）
            self.add_to_grabbing_list(game_data)
        except Exception as e:
            error_msg = f"抢单按钮点击出错: {str(e)}"
            self.log(error_msg, "ERROR")
            QMessageBox.critical(self, "错误", error_msg)
    
    def add_to_grabbing_list(self, game_data: Dict):
        """添加到正在抢单列表"""
        game_id = game_data.get('id')
        if any(g.get('id') == game_id for g in self.grabbing_games):
            return  # 已经存在
        
        # 获取加入时的价格
        grab_price = game_data.get('price', 'N/A')
        
        # 添加游戏数据，包含加入时价格
        game_data_with_price = game_data.copy()
        game_data_with_price['grab_price'] = grab_price
        game_data_with_price['grab_time'] = datetime.now().isoformat()
        
        self.grabbing_games.append(game_data_with_price)
        
        # 创建抢单列表Widget
        grabbing_widget = GrabbingItemWidget(game_data, grab_price)
        grabbing_widget.stop_clicked.connect(self.remove_from_grabbing_list)
        grabbing_widget.pause_clicked.connect(self.pause_grabbing)
        grabbing_widget.resume_clicked.connect(self.resume_grabbing)
        grabbing_widget.finish_clicked.connect(self.remove_from_grabbing_list)
        
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("border: 1px solid #ff9800; border-radius: 3px; margin: 2px; background-color: #fff3e0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(grabbing_widget)
        
        self.grabbing_layout.addWidget(frame)
        self.grabbing_widgets.append((frame, grabbing_widget, game_data_with_price))
        
        # 加载图片
        self.load_game_image(grabbing_widget, game_data)
        
        # 保存抢单列表
        self.save_grabbing_list()
        
        # 开始抢单
        self.start_single_grabbing(game_data_with_price, grabbing_widget)
        
        self.log(f"已添加到抢单列表: {game_data.get('name', '未知')} (价格: {grab_price})")
    
    def remove_from_grabbing_list(self, game_data: Dict):
        """从正在抢单列表移除"""
        game_id = game_data.get('id')
        
        # 停止抢单线程
        if game_id in self.grab_threads:
            thread = self.grab_threads[game_id]
            if thread.isRunning():
                thread.requestInterruption()
                thread.quit()
                thread.wait(1000)
            del self.grab_threads[game_id]
        
        self.grabbing_games = [g for g in self.grabbing_games if g.get('id') != game_id]
        
        # 移除Widget
        for i, (frame, widget, data) in enumerate(self.grabbing_widgets):
            if data.get('id') == game_id:
                self.grabbing_layout.removeWidget(frame)
                frame.deleteLater()
                self.grabbing_widgets.pop(i)
                break
        
        # 保存抢单列表
        self.save_grabbing_list()
        
        self.log(f"已从抢单列表移除: {game_data.get('name', '未知')}")
    
    def pause_grabbing(self, game_data: Dict):
        """暂停抢单"""
        game_id = game_data.get('id')
        if game_id in self.grab_threads:
            self.grab_threads[game_id].pause()
            self.log(f"已暂停抢单: {game_data.get('name', '未知')}")
    
    def resume_grabbing(self, game_data: Dict):
        """恢复抢单"""
        game_id = game_data.get('id')
        if game_id in self.grab_threads:
            thread = self.grab_threads[game_id]
            if thread and thread.isRunning():
                thread.resume()
                self.log(f"已恢复抢单: {game_data.get('name', '未知')}")
            else:
                # 线程不存在或已停止，需要重新启动
                self.log(f"抢单线程不存在，正在重新启动: {game_data.get('name', '未知')}", "INFO")
                # 找到对应的widget
                for frame, widget, data in self.grabbing_widgets:
                    if data.get('id') == game_id and isinstance(widget, GrabbingItemWidget):
                        self.start_single_grabbing(game_data, widget)
                        break
        else:
            # 线程不存在，需要启动
            self.log(f"抢单线程不存在，正在启动: {game_data.get('name', '未知')}", "INFO")
            # 找到对应的widget
            for frame, widget, data in self.grabbing_widgets:
                if data.get('id') == game_id and isinstance(widget, GrabbingItemWidget):
                    self.start_single_grabbing(game_data, widget)
                    break
    
    def _on_target_price_changed(self, game_data: Dict, target_price: float):
        """目标价格更新回调"""
        game_id = game_data.get('id')
        normalized_price = target_price if target_price > 0 else ''
        
        # 更新内存中的数据
        for stored_game in self.grabbing_games:
            if stored_game.get('id') == game_id:
                stored_game['target_price'] = normalized_price
                break
        
        # 记录日志并持久化
        display_price = f"¥{normalized_price:.2f}" if normalized_price else "自动(70%)"
        self.log(f"已更新 {game_data.get('name', '未知')} 的目标价格: {display_price}")
        self.save_grabbing_list()
    
    def on_interval_changed(self, value: int):
        """请求间隔改变"""
        self.request_interval = value
        self.save_config()
        self.log(f"请求间隔已更新为: {value}秒")
    
    def on_percentage_changed(self, value: int):
        """目标价百分比改变"""
        self.target_price_percentage = value
        self.save_config()
        self.log(f"默认目标价百分比已更新为: {value}% (当前价低于或等于加入价的{value}%时触发抢单)")
        
        # 更新所有运行中的抢单线程的百分比
        updated_count = 0
        for thread in self.grab_threads.values():
            if thread and thread.isRunning():
                thread.update_percentage(value)
                updated_count += 1
        
        if updated_count > 0:
            self.log(f"已更新 {updated_count} 个运行中的抢单线程的百分比设置", "INFO")
    
    def on_email_changed(self):
        """通知邮箱改变"""
        self.save_config()
        email = self.email_entry.text().strip()
        if email:
            self.log(f"通知邮箱已更新: {email}")
    
    def show_donate_dialog(self):
        """显示捐赠对话框"""
        dialog = DonateDialog(self)
        dialog.exec()
    
    def load_config(self):
        """加载配置 - 只加载用户可配置的项"""
        # 内置SMTP配置（用户不可修改）
        self.smtp_host = 'smtp.qq.com'
        self.smtp_port = 587
        self.smtp_username = '发件邮箱'
        self.smtp_password = 'qq邮箱授权码'
        self.smtp_use_ssl = True
        
        # 从配置文件加载用户可配置项
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.request_interval = config.get('request_interval', 3)
                self.notification_email = config.get('notification_email', '')
                self.target_price_percentage = config.get('target_price_percentage', 70)
            except Exception as e:
                self.log(f"加载配置失败: {e}", "ERROR")
                self.request_interval = 3
                self.notification_email = ''
                self.target_price_percentage = 70
        else:
            self.request_interval = 3
            self.notification_email = ''
            self.target_price_percentage = 70  # 默认低于或等于70%
        
        # 确保百分比在合理范围内
        self.target_price_percentage = max(10, min(100, self.target_price_percentage))
        
        # 更新UI
        if hasattr(self, 'interval_spinbox'):
            self.interval_spinbox.setValue(self.request_interval)
        if hasattr(self, 'email_entry'):
            self.email_entry.setText(self.notification_email)
        if hasattr(self, 'percentage_spinbox'):
            self.percentage_spinbox.setValue(self.target_price_percentage)
    
    
    
    def save_config(self):
        """保存配置 - 只保存用户可配置的项"""
        try:
            if hasattr(self, 'interval_spinbox'):
                self.request_interval = self.interval_spinbox.value()
            if hasattr(self, 'email_entry'):
                self.notification_email = self.email_entry.text().strip()
            if hasattr(self, 'percentage_spinbox'):
                self.target_price_percentage = self.percentage_spinbox.value()
            
            # 只保存用户可配置的项
            config = {
                'request_interval': self.request_interval,
                'notification_email': self.notification_email,
                'target_price_percentage': self.target_price_percentage
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存配置失败: {e}", "ERROR")

    def _parse_price_value(self, value) -> float:
        """解析价格字符串为浮点数"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            text = str(value)
            text = text.replace('¥', '').replace(',', '').strip()
            if not text:
                return 0.0
            return float(text)
        except Exception:
            return 0.0

    def send_email_notification(self, game_data: Dict):
        """发送抢单成功邮件通知"""
        if not self.notification_email:
            self.log("未配置通知邮箱，跳过邮件通知", "INFO")
            return
        if not self.smtp_host:
            self.log("未配置SMTP服务器，无法发送邮件通知", "ERROR")
            return
        
        # 如果SMTP主机为空、无效或是示例地址，尝试自动配置
        invalid_hosts = ['', 'smtp.example.com', 'example.com']
        if not self.smtp_host or self.smtp_host.strip() == '' or self.smtp_host in invalid_hosts:
            self.log(f"检测到无效的SMTP服务器地址，尝试自动配置...", "INFO")
            self._auto_configure_smtp()
            if not self.smtp_host or self.smtp_host.strip() == '' or self.smtp_host in invalid_hosts:
                self.log(f"无法自动配置SMTP服务器（邮箱: {self.notification_email}），请手动在config.json中配置正确的SMTP服务器地址", "ERROR")
                return
        
        game_name = game_data.get('name', '未知')
        success_price = self._parse_price_value(game_data.get('last_success_price'))
        if success_price == 0:
            success_price = self._parse_price_value(game_data.get('price'))
        
        join_price = self._parse_price_value(game_data.get('grab_price'))
        price_diff = join_price - success_price if join_price else 0
        # 折扣率 = (节省金额 / 原价) * 100，例如100变成99就是1%
        discount = ((join_price - success_price) / join_price * 100) if join_price and join_price > 0 else 0
        
        now = datetime.now()
        release_time = now + timedelta(minutes=15)
        
        # HTML格式的邮件内容
        html_body = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>抢单成功通知</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <!-- 头部 -->
        <div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 30px 20px; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                🎉 抢单成功！
            </h1>
        </div>
        
        <!-- 内容区域 -->
        <div style="padding: 30px 20px;">
            <!-- 游戏名称 -->
            <div style="margin-bottom: 25px; text-align: center;">
                <h2 style="margin: 0; color: #333333; font-size: 22px; font-weight: 600; border-bottom: 2px solid #4caf50; padding-bottom: 10px; display: inline-block;">
                    {game_name}
                </h2>
            </div>
            
            <!-- 价格信息卡片 -->
            <div style="background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%); border-left: 4px solid #ff9800; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <span style="color: #666666; font-size: 14px; font-weight: 500;">当前价格</span>
                    <span style="color: #d32f2f; font-size: 24px; font-weight: bold;">¥{success_price:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <span style="color: #666666; font-size: 14px; font-weight: 500;">加入时最低价</span>
                    <span style="color: #333333; font-size: 18px; font-weight: 600;">¥{join_price:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <span style="color: #666666; font-size: 14px; font-weight: 500;">节省金额</span>
                    <span style="color: #4caf50; font-size: 20px; font-weight: bold;">¥{price_diff:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #666666; font-size: 14px; font-weight: 500;">折扣率</span>
                    <span style="background-color: #4caf50; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-size: 16px; font-weight: bold;">
                        {discount:.2f}%
                    </span>
                </div>
            </div>
            
            <!-- 状态信息 -->
            <div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="color: #2e7d32; font-size: 16px; font-weight: 600; margin-right: 10px;">✓</span>
                    <span style="color: #2e7d32; font-size: 16px; font-weight: 600;">状态: 抢单成功</span>
                </div>
            </div>
            
            <!-- 时间信息 -->
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <div style="margin-bottom: 12px;">
                    <div style="color: #999999; font-size: 12px; margin-bottom: 5px;">抢单时间</div>
                    <div style="color: #333333; font-size: 15px; font-weight: 500;">{now.strftime('%Y年%m月%d日 %H:%M:%S')}</div>
                </div>
                <div>
                    <div style="color: #999999; font-size: 12px; margin-bottom: 5px;">预计放出时间</div>
                    <div style="color: #333333; font-size: 15px; font-weight: 500;">{release_time.strftime('%Y年%m月%d日 %H:%M:%S')}</div>
                </div>
            </div>
            
            <!-- 提示信息 -->
            <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; border-radius: 6px; text-align: center;">
                <p style="margin: 0; color: #e65100; font-size: 14px; line-height: 1.6;">
                    ⏰ 请及时完成支付，支付超时时间为 <strong>15分钟</strong>，预计在 <strong>{release_time.strftime('%H:%M')}</strong> 左右放出激活码
                </p>
            </div>
        </div>
        
        <!-- 底部 -->
        <div style="background-color: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
            <p style="margin: 0; color: #999999; font-size: 12px;">
                此邮件由游戏抢单系统自动发送
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        subject = f"🎉 抢单成功通知 - {game_name}"
        sender = self.smtp_username or self.notification_email
        
        try:
            # 检查SMTP配置（包括示例地址）
            invalid_hosts = ['', 'smtp.example.com', 'example.com']
            if not self.smtp_host or self.smtp_host.strip() == '' or self.smtp_host in invalid_hosts:
                self.log(f"SMTP服务器地址无效（{self.smtp_host}），尝试自动配置...", "WARNING")
                # 尝试自动配置
                if self.notification_email:
                    self._auto_configure_smtp()
                    if self.smtp_host in invalid_hosts:
                        self.log(f"无法自动配置SMTP服务器，请手动在config.json中配置正确的SMTP服务器地址", "ERROR")
                        return
                else:
                    self.log(f"SMTP服务器地址无效且未配置通知邮箱，无法发送邮件", "ERROR")
                    return
            
            self.log(f"[邮件发送] 准备发送邮件到 {self.notification_email}", "INFO")
            self.log(f"[邮件发送] SMTP服务器: {self.smtp_host}:{self.smtp_port}, SSL: {self.smtp_use_ssl}", "INFO")
            
            msg = MIMEText(html_body, "html", "utf-8")
            msg['Subject'] = Header(subject, "utf-8")
            msg['From'] = sender
            msg['To'] = self.notification_email
            
            self.log(f"[邮件发送] 正在连接SMTP服务器...", "INFO")
            # 根据端口选择连接方式：
            # 端口465：使用SMTP_SSL（直接SSL连接）
            # 端口587：使用SMTP + starttls()（先普通连接，再升级到SSL）
            # 其他端口：根据smtp_use_ssl配置决定
            if self.smtp_port == 465:
                # 端口465必须使用SMTP_SSL
                self.log(f"[邮件发送] 使用SMTP_SSL连接（端口465）", "INFO")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            elif self.smtp_port == 587:
                # 端口587必须使用SMTP + starttls()
                self.log(f"[邮件发送] 使用SMTP连接（端口587），将使用STARTTLS", "INFO")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            else:
                # 其他端口根据配置决定
                if self.smtp_use_ssl:
                    self.log(f"[邮件发送] 使用SMTP_SSL连接", "INFO")
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
                else:
                    self.log(f"[邮件发送] 使用SMTP连接", "INFO")
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            
            self.log(f"[邮件发送] SMTP连接成功", "INFO")
            
            if self.smtp_username:
                # 对于端口587或其他非SSL端口，需要启动STARTTLS
                if self.smtp_port == 587 or (not self.smtp_use_ssl and self.smtp_port != 465):
                    try:
                        self.log(f"[邮件发送] 启动STARTTLS...", "INFO")
                        server.starttls()
                        self.log(f"[邮件发送] STARTTLS成功", "INFO")
                    except Exception as e:
                        self.log(f"[邮件发送] STARTTLS失败: {e}", "WARNING")
                        # STARTTLS失败时，某些服务器可能仍然允许登录，继续尝试
                
                # 设置更长的超时时间
                server.timeout = 30
                
                self.log(f"[邮件发送] 正在登录SMTP服务器...", "INFO")
                self.log(f"[邮件发送] 用户名: {self.smtp_username}", "INFO")
                
                try:
                    # 尝试登录，增加错误处理
                    server.login(self.smtp_username, self.smtp_password)
                    self.log(f"[邮件发送] SMTP登录成功", "INFO")
                except smtplib.SMTPAuthenticationError as e:
                    error_msg = f"SMTP认证失败: {str(e)}"
                    self.log(f"发送邮件通知失败: {error_msg}", "ERROR")
                    self.log(f"提示: 请检查用户名和密码是否正确。QQ邮箱需要使用授权码而不是登录密码。", "ERROR")
                    server.quit()
                    return
                except smtplib.SMTPServerDisconnected as e:
                    error_msg = f"SMTP连接被服务器关闭: {str(e)}"
                    self.log(f"发送邮件通知失败: {error_msg}", "ERROR")
                    self.log(f"提示: 可能是密码错误、需要授权码，或服务器拒绝了连接。", "ERROR")
                    try:
                        server.quit()
                    except:
                        pass
                    return
                except Exception as e:
                    error_msg = f"SMTP登录过程出错: {str(e)}"
                    self.log(f"发送邮件通知失败: {error_msg}", "ERROR")
                    try:
                        server.quit()
                    except:
                        pass
                    return
            
            self.log(f"[邮件发送] 正在发送邮件...", "INFO")
            try:
                server.sendmail(sender, [self.notification_email], msg.as_string())
                self.log(f"✓ 已成功发送抢单成功邮件给 {self.notification_email}", "SUCCESS")
            except Exception as e:
                error_msg = f"发送邮件时出错: {str(e)}"
                self.log(f"发送邮件通知失败: {error_msg}", "ERROR")
                raise
            
            try:
                server.quit()
            except:
                pass
        except smtplib.SMTPException as e:
            error_msg = f"SMTP错误: {str(e)}"
            self.log(f"发送邮件通知失败: {error_msg}", "ERROR")
            import traceback
            self.log(f"[邮件发送错误详情] {traceback.format_exc()}", "ERROR")
        except Exception as e:
            error_msg = f"发送邮件通知失败: {str(e)}"
            self.log(error_msg, "ERROR")
            import traceback
            self.log(f"[邮件发送错误详情] {traceback.format_exc()}", "ERROR")
    
    def clear_game_widgets(self):
        """清空游戏Widget列表"""
        for frame, widget, game in self.game_widgets:
            self.search_layout.removeWidget(frame)
            frame.deleteLater()
        self.game_widgets.clear()
    
    def clear_game_list(self):
        """清空游戏列表"""
        self.clear_game_widgets()
        self.selected_games = []
        self.games_data.clear()
    
    def stop_all_grabbing(self):
        """停止所有抢单"""
        for game_data in self.grabbing_games[:]:
            self.remove_from_grabbing_list(game_data)
        self.stop_grabbing()
    
    def start_single_grabbing(self, game_data: Dict, widget: GrabbingItemWidget):
        """开始单个游戏抢单"""
        game_id = game_data.get('id')
        
        if not game_id:
            self.log("游戏ID不存在，无法启动抢单", "ERROR")
            return
        
        # 如果已有线程在运行，先停止
        if game_id in self.grab_threads:
            old_thread = self.grab_threads[game_id]
            if old_thread and old_thread.isRunning():
                old_thread.requestInterruption()
                old_thread.quit()
                old_thread.wait(1000)
                if old_thread.isRunning():
                    old_thread.terminate()
                    old_thread.wait(500)
        
        # 确保请求头已更新
        self._update_session_headers()
        
        try:
            # 创建抢单线程
            if not self.order_grabber:
                self.order_grabber = OrderGrabber(self.session, log_callback=self.log)
            
            grab_thread = GrabThread(self.order_grabber, game_data, widget, self.request_interval, self.target_price_percentage)
            grab_thread.log_message.connect(self.log)
            grab_thread.status_update.connect(lambda g, s: self._update_grabbing_status(g, s))
            grab_thread.price_update.connect(lambda g, p: self._update_grabbing_price(g, p))
            grab_thread.grab_success.connect(self.on_grab_success)
            grab_thread.finished.connect(lambda: self.on_single_grab_finished(game_data))
            
            self.grab_threads[game_id] = grab_thread
            grab_thread.start()
            self.log(f"已启动抢单线程: {game_data.get('name', '未知')}", "INFO")
        except Exception as e:
            import traceback
            error_msg = f"启动抢单失败: {str(e)}"
            full_error = f"{error_msg}\n{traceback.format_exc()}"
            self.log(full_error, "ERROR")
            QMessageBox.critical(self, "错误", error_msg)
    
    def _update_grabbing_status(self, game_data: Dict, status: str):
        """更新抢单状态"""
        game_id = game_data.get('id')
        # 更新 game_data 中的状态
        game_data['status'] = status
        for frame, widget, data in self.grabbing_widgets:
            if data.get('id') == game_id and isinstance(widget, GrabbingItemWidget):
                widget.update_status(status)
                break
        # 保存状态到文件
        self.save_grabbing_list()
    
    def _update_grabbing_price(self, game_data: Dict, price: str):
        """更新抢单价格"""
        game_id = game_data.get('id')
        for frame, widget, data in self.grabbing_widgets:
            if data.get('id') == game_id and isinstance(widget, GrabbingItemWidget):
                widget.update_min_price(price)
                break
    
    def on_grab_success(self, game_data: Dict):
        """抢单成功"""
        self.log(f"🎉 抢单成功: {game_data.get('name', '未知')}", "SUCCESS")
        # 邮件通知
        self.send_email_notification(game_data)
    
    def on_single_grab_finished(self, game_data: Dict):
        """单个游戏抢单完成"""
        game_id = game_data.get('id')
        if game_id in self.grab_threads:
            del self.grab_threads[game_id]
    
    def save_grabbing_list(self):
        """保存抢单列表到文件"""
        try:
            # 准备保存的数据（排除不可序列化的对象）
            save_data = []
            for game_data in self.grabbing_games:
                save_item = {
                    'id': game_data.get('id'),
                    'name': game_data.get('name'),
                    'grab_price': game_data.get('grab_price', game_data.get('price', 'N/A')),
                    'grab_time': game_data.get('grab_time', datetime.now().isoformat()),
                    'gameAvaLib': game_data.get('gameAvaLib'),
                    'gameAva': game_data.get('gameAva'),
                    'url': game_data.get('url'),
                    'appId': game_data.get('appId'),
                    'price': game_data.get('price'),
                    'available': game_data.get('available', True),
                    'target_price': game_data.get('target_price', ''),
                    'status': game_data.get('status', '正在抢单')  # 保存状态
                }
                save_data.append(save_item)
            
            with open(self.grabbing_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存抢单列表失败: {e}", "ERROR")
    
    def load_grabbing_list(self):
        """从文件加载抢单列表"""
        if not os.path.exists(self.grabbing_file):
            return
        
        try:
            with open(self.grabbing_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            for item in save_data:
                # 使用保存的数据重建游戏信息
                game_data = item.copy()
                game_data['available'] = game_data.get('available', True)
                if 'grab_price' not in game_data:
                    game_data['grab_price'] = game_data.get('price', 'N/A')
                
                # 添加到抢单列表（不自动开始抢单）
                self._add_grabbing_item_from_saved(game_data)
            
            if save_data:
                self.log(f"已加载 {len(save_data)} 个抢单任务", "INFO")
        except Exception as e:
            self.log(f"加载抢单列表失败: {e}", "ERROR")
    
    def _add_grabbing_item_from_saved(self, game_data: Dict):
        """从保存的数据添加抢单项（不自动开始）"""
        game_id = game_data.get('id')
        if any(g.get('id') == game_id for g in self.grabbing_games):
            return
        
        grab_price = game_data.get('grab_price', game_data.get('price', 'N/A'))
        game_data['grab_price'] = grab_price
        game_data['grab_time'] = game_data.get('grab_time', datetime.now().isoformat())
        game_data['target_price'] = game_data.get('target_price', '')
        
        self.grabbing_games.append(game_data)
        
        # 创建Widget
        grabbing_widget = GrabbingItemWidget(game_data, grab_price)
        # 如果状态是"抢单成功"，直接设置为成功状态，否则默认暂停
        if game_data.get('status') == '抢单成功':
            grabbing_widget.update_status("抢单成功")
        else:
            grabbing_widget.update_status("暂停")  # 加载时默认暂停
        grabbing_widget.stop_clicked.connect(self.remove_from_grabbing_list)
        grabbing_widget.pause_clicked.connect(self.pause_grabbing)
        grabbing_widget.resume_clicked.connect(self.resume_grabbing)
        grabbing_widget.finish_clicked.connect(self.remove_from_grabbing_list)
        grabbing_widget.target_price_changed.connect(self._on_target_price_changed)
        
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("border: 1px solid #ff9800; border-radius: 3px; margin: 2px; background-color: #fff3e0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(grabbing_widget)
        
        self.grabbing_layout.addWidget(frame)
        self.grabbing_widgets.append((frame, grabbing_widget, game_data))
        
        # 加载图片
        self.load_game_image(grabbing_widget, game_data)
    
    def start_grabbing(self):
        """开始抢单"""
        # 获取选中的游戏
        self.selected_games = self.get_selected_games()
        
        if not self.selected_games:
            QMessageBox.warning(self, "警告", "请先选择要抢单的游戏")
            return
        
        if not self.access_token:
            QMessageBox.warning(self, "警告", "请先设置登录信息")
            return
        
        # 更新UI状态
        self.is_grabbing = True
        if self.start_btn:
            self.start_btn.setEnabled(False)
        if self.stop_btn:
            self.stop_btn.setEnabled(True)
        self.status_label.setText("抢单中...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        
        self.log(f"开始抢单，监控 {len(self.selected_games)} 个游戏")
        for game in self.selected_games:
            self.log(f"  - {game.get('name', '未知')}")
        
        # 确保请求头已更新
        self._update_session_headers()
        
        # 创建抢单线程
        if not self.order_grabber:
            self.order_grabber = OrderGrabber(self.session)
        
        # 注意：旧的批量抢单功能已废弃，使用单个抢单
        QMessageBox.information(self, "提示", "请使用每个游戏项上的'抢单'按钮进行抢单")
        self.grab_thread.log_message.connect(self.log)
        self.grab_thread.finished.connect(self.on_grab_finished)
        self.grab_thread.start()
    
    def on_grab_finished(self):
        """抢单线程完成"""
        self.stop_grabbing()
    
    def stop_grabbing(self):
        """停止抢单"""
        self.is_grabbing = False
        if self.order_grabber:
            self.order_grabber.stop()
        
        if self.grab_thread and self.grab_thread.isRunning():
            self.grab_thread.terminate()
            self.grab_thread.wait()
        
        if self.start_btn:
            self.start_btn.setEnabled(True)
        if self.stop_btn:
            self.stop_btn.setEnabled(False)
        self.status_label.setText("已停止")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        self.log("已停止抢单")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止所有抢单线程
        if self.grab_threads:
            for game_id, thread in list(self.grab_threads.items()):
                if thread and thread.isRunning():
                    thread.requestInterruption()
                    thread.quit()
                    thread.wait(1000)  # 等待最多1秒
                    if thread.isRunning():
                        thread.terminate()
                        thread.wait(500)
            self.grab_threads.clear()
        
        # 停止所有图片加载线程
        for frame, widget, game in self.game_widgets:
            if hasattr(widget, 'image_thread') and widget.image_thread and widget.image_thread.isRunning():
                widget.image_thread.requestInterruption()
                widget.image_thread.quit()
                widget.image_thread.wait(500)  # 等待最多500ms
                if widget.image_thread.isRunning():
                    widget.image_thread.terminate()
                    widget.image_thread.wait(300)
        
        for frame, widget, game in self.grabbing_widgets:
            if hasattr(widget, 'image_thread') and widget.image_thread and widget.image_thread.isRunning():
                widget.image_thread.requestInterruption()
                widget.image_thread.quit()
                widget.image_thread.wait(500)
                if widget.image_thread.isRunning():
                    widget.image_thread.terminate()
                    widget.image_thread.wait(300)
        
        # 停止搜索线程
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.requestInterruption()
            self.search_thread.quit()
            self.search_thread.wait(500)
            if self.search_thread.isRunning():
                self.search_thread.terminate()
                self.search_thread.wait(300)
        
        # 保存抢单列表
        self.save_grabbing_list()
        
        # 保存配置
        self.save_config()
        
        event.accept()


def main():
    """GUI主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = GameOrderGrabberGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
