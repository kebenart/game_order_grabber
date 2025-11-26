# 游戏抢单系统

一个基于Python和PySide6开发的自动化游戏抢单工具，支持SteamPy平台的游戏价格监控和自动抢单功能。

<img width="1805" height="885" alt="image" src="https://github.com/user-attachments/assets/eb8fc04c-2b02-4a1e-aec3-912ab387281f" />


## 🎯 主要功能

- **游戏搜索**：支持按游戏名称搜索，显示价格和可购买状态
- **价格监控**：实时监控游戏价格变化，支持多游戏并发监控
- **自动抢单**：当价格满足条件时自动执行抢单操作
- **灵活定价**：支持自定义目标价格或使用百分比规则
- **邮件通知**：抢单成功后自动发送邮件通知
- **图形界面**：现代化的GUI界面，操作简单直观
- **数据持久化**：自动保存抢单列表和配置信息

## 📸 界面预览

程序提供直观的图形界面，包含：
- 登录信息配置区域
- 游戏搜索和结果展示
- 抢单列表管理
- 实时日志输出
- 配置参数调整

## 🚀 快速开始

### 环境要求

- Python 3.7 或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
# 启动GUI版本（推荐）
python main.py

# 或者直接运行GUI模块
python gui.py
```

## 📦 打包版本

### Windows用户

1. 下载 `游戏抢单系统正式版.exe`
2. 双击运行即可（首次运行可能被杀毒软件拦截，请添加到信任列表）

### 自行打包

#### Windows打包
```batch
# 运行打包脚本
build_windows.bat

# 或手动打包
pyinstaller build_windows.spec
```

#### macOS打包
```bash
# 添加执行权限
chmod +x build_mac.sh

# 运行打包脚本
./build_mac.sh

# 或手动打包
pyinstaller build_mac.spec
```

## ⚙️ 配置说明

### 1. 登录配置

程序需要有效的AccessToken才能正常工作：

1. 在"登录信息"区域输入AccessToken
2. 点击"保存"按钮保存配置
3. 系统会自动验证并显示登录状态

### 2. 抢单配置

#### 请求间隔
- **建议值**：3-10秒
- **说明**：过短可能被限制，过长可能错过机会

#### 目标价格百分比
- **取值范围**：10%-100%
- **默认值**：70%
- **说明**：当前价格低于或等于加入价格的该百分比时触发抢单

#### 邮件通知（可选）
- 填写接收通知的邮箱地址
- 抢单成功后会自动发送详细的通知邮件

### 3. 配置文件

程序会在用户数据目录自动创建配置文件：

```json
{
  "request_interval": 3,
  "notification_email": "your-email@example.com",
  "target_price_percentage": 70
}
```

## 🎮 使用流程

### 1. 搜索游戏
1. 在搜索框输入游戏名称
2. 点击"搜索"按钮
3. 浏览搜索结果，查看价格和状态

### 2. 添加到抢单列表
1. 点击游戏卡片上的"抢单"按钮
2. 游戏会被添加到右侧的"正在抢单"列表
3. 可以设置自定义目标价格（可选）

### 3. 监控和抢单
1. 系统自动开始监控价格
2. 当价格满足条件时自动抢单
3. 可以随时暂停、继续或停止抢单
4. 抢单成功后显示"完成"状态

### 4. 抢单条件

系统支持两种抢单触发条件（满足任一即可）：

**自定义目标价格**
- 在抢单列表中设置具体的目标价格
- 当前价 ≤ 目标价时触发抢单

**百分比规则**
- 当未设置自定义目标价格时使用
- 当前价 ≤ 加入价 × 百分比时触发抢单
- 例如：加入价¥100，设置70%，则当前价≤¥70时触发

## 📧 邮件通知配置

### 常见邮箱配置

#### QQ邮箱
```json
{
  "notification_email": "your-qq@qq.com",
  "smtp_host": "smtp.qq.com",
  "smtp_port": 465,
  "smtp_username": "your-qq@qq.com",
  "smtp_password": "你的授权码",
  "smtp_use_ssl": true
}
```

#### 163邮箱
```json
{
  "notification_email": "your-email@163.com",
  "smtp_host": "smtp.163.com",
  "smtp_port": 465,
  "smtp_username": "your-email@163.com",
  "smtp_password": "你的授权码",
  "smtp_use_ssl": true
}
```

#### Gmail
```json
{
  "notification_email": "your-email@gmail.com",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 465,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "你的应用专用密码",
  "smtp_use_ssl": true
}
```

**注意**：大多数邮箱服务需要使用授权码或应用专用密码，而不是登录密码。

## 🔧 故障排除

### 常见问题

#### 程序无法启动
- 检查是否被杀毒软件拦截
- 确保Python环境正确安装
- 查看是否缺少依赖包

#### 搜索无结果
- 检查AccessToken是否有效
- 确认网络连接正常
- 验证API地址是否可访问

#### 抢单不触发
- 检查目标价格百分比设置
- 查看日志中的价格比较信息
- 确认当前价格是否真的满足条件

#### 邮件发送失败
- 检查SMTP配置是否正确
- 确认邮箱授权码是否有效
- 查看网络防火墙设置

### 调试方法

1. **查看日志**：程序运行时会显示详细的日志信息
2. **检查配置**：确认配置文件格式正确
3. **网络测试**：确保能正常访问相关API
4. **权限检查**：确保程序有读写配置文件的权限

## 📁 项目结构

```
game_order_grabber/
├── main.py                 # 主程序入口
├── gui.py                  # GUI界面实现
├── game_searcher.py        # 游戏搜索模块
├── order_grabber.py        # 抢单逻辑模块
├── config.example.json     # 配置文件示例
├── requirements.txt        # 依赖包列表
├── build_windows.bat       # Windows打包脚本
├── build_mac.sh           # macOS打包脚本
├── build_windows.spec     # Windows打包配置
├── build_mac.spec         # macOS打包配置
├── donate_qr.png          # 捐赠二维码
├── BUILD_README.md        # 打包说明文档
├── CONFIG_README.md       # 配置说明文档
├── GUI_README.md          # GUI使用说明
├── TROUBLESHOOTING.md     # 故障排除指南
├── RELEASE_NOTES.md       # 版本发布说明
└── README.md              # 项目说明文档
```

## 📚 详细文档

- [打包说明](BUILD_README.md) - 如何将项目打包成可执行文件
- [配置说明](CONFIG_README.md) - 详细的配置参数说明
- [GUI使用说明](GUI_README.md) - 图形界面使用指南
- [故障排除](TROUBLESHOOTING.md) - 常见问题解决方案
- [版本发布说明](RELEASE_NOTES.md) - 版本更新记录

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 💝 支持项目

如果这个项目对您有帮助，欢迎通过以下方式支持：

- ⭐ 给项目点个Star
- 🐛 报告Bug或提出改进建议
- 💰 通过程序内的"捐赠支持"功能进行捐赠

## 📞 联系方式

- 项目地址：[GitHub Repository]
- 问题反馈：通过GitHub Issues提交

## ⚠️ 免责声明

本工具仅供学习和研究使用，请遵守相关平台的使用条款和法律法规。使用本工具所产生的任何后果由使用者自行承担。

## 📝 更新日志

### v1.1.0 (2025-11-25)
- ✨ 新增可配置的目标价格百分比功能
- 🔧 修复价格判断逻辑
- 📝 更新配置文档
- 🎨 优化UI提示信息

### v1.0.0
- 🎉 初始版本发布
- 基础抢单功能
- 邮件通知功能
- GUI界面

---

**感谢使用游戏抢单系统！** 🎮
