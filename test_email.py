#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试邮件发送功能
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timedelta

def test_send_email():
    """测试发送邮件"""
    # 读取配置
    config_file = "config.json"
    if not os.path.exists(config_file):
        print("✗ config.json 文件不存在")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    notification_email = config.get('notification_email', '')
    smtp_host = config.get('smtp_host', '')
    smtp_port = config.get('smtp_port', 465)
    smtp_username = config.get('smtp_username', '')
    smtp_password = config.get('smtp_password', '')
    smtp_use_ssl = config.get('smtp_use_ssl', True)
    
    # 如果没有配置，使用测试邮箱
    if not notification_email:
        notification_email = "xxxxxxx@qq.com"
    
    # 如果SMTP主机无效，自动配置
    invalid_hosts = ['', 'smtp.example.com', 'example.com']
    if not smtp_host or smtp_host in invalid_hosts:
        email = notification_email.lower()
        if '@qq.com' in email:
            smtp_host = 'smtp.qq.com'
            smtp_port = 465
            smtp_use_ssl = True
            if not smtp_username:
                smtp_username = notification_email
        elif '@163.com' in email:
            smtp_host = 'smtp.163.com'
            smtp_port = 465
            smtp_use_ssl = True
            if not smtp_username:
                smtp_username = notification_email
        elif '@gmail.com' in email:
            smtp_host = 'smtp.gmail.com'
            smtp_port = 465
            smtp_use_ssl = True
            if not smtp_username:
                smtp_username = notification_email
        else:
            print(f"✗ 无法自动配置SMTP服务器（邮箱: {notification_email}）")
            return
    
    print(f"邮件配置:")
    print(f"  收件人: {notification_email}")
    print(f"  SMTP服务器: {smtp_host}:{smtp_port}")
    print(f"  SSL: {smtp_use_ssl}")
    print(f"  用户名: {smtp_username}")
    print(f"  密码: {'已配置' if smtp_password else '未配置'}")
    print()
    
    if not smtp_password:
        print("✗ SMTP密码未配置，无法发送邮件")
        print("  请在config.json中配置smtp_password字段")
        return
    
    # 准备邮件内容
    now = datetime.now()
    release_time = now + timedelta(minutes=5)
    
    body = (
        f"游戏名: 测试游戏\n"
        f"当前价格: ¥23.50\n"
        f"加入抢单时最低价: ¥80.00\n"
        f"价格差: ¥56.50\n"
        f"折扣率: 29.38%\n"
        f"状态: 抢单成功\n"
        f"抢单时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"预计放出时间: {release_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    subject = "抢单成功通知 - 测试游戏"
    sender = smtp_username or notification_email
    
    try:
        print("正在创建邮件...")
        msg = MIMEText(body, "plain", "utf-8")
        msg['Subject'] = Header(subject, "utf-8")
        msg['From'] = sender
        msg['To'] = notification_email
        
        print(f"正在连接SMTP服务器 {smtp_host}:{smtp_port}...")
        if smtp_use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        
        print("SMTP连接成功")
        
        if smtp_username:
            if not smtp_use_ssl:
                try:
                    print("启动STARTTLS...")
                    server.starttls()
                    print("STARTTLS成功")
                except Exception as e:
                    print(f"STARTTLS失败: {e}")
            
            print("正在登录SMTP服务器...")
            server.login(smtp_username, smtp_password)
            print("SMTP登录成功")
        
        print("正在发送邮件...")
        server.sendmail(sender, [notification_email], msg.as_string())
        server.quit()
        print(f"✓ 邮件已成功发送到 {notification_email}")
        
    except smtplib.SMTPException as e:
        print(f"✗ SMTP错误: {e}")
        import traceback
        print(traceback.format_exc())
    except Exception as e:
        print(f"✗ 发送邮件失败: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_send_email()

