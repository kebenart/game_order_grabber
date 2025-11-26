# 快速打包指南

## 🚀 快速开始

### Windows 用户

1. **双击运行** `build_windows.bat`
2. 等待打包完成
3. 在 `dist` 文件夹中找到 `游戏抢单系统.exe`

### Mac 用户

1. **打开终端**，进入项目目录
2. **运行命令**：
   ```bash
   ./build_mac.sh
   ```
3. 在 `dist` 文件夹中找到 `游戏抢单系统.app`

## 📋 打包前准备

### 1. 安装依赖

**Windows:**
```batch
pip install -r requirements.txt
```

**Mac:**
```bash
pip3 install -r requirements.txt
```

### 2. 确保文件完整

打包前请确保以下文件存在：
- ✅ `main.py` - 主程序入口
- ✅ `gui.py` - GUI 界面
- ✅ `game_searcher.py` - 游戏搜索模块
- ✅ `order_grabber.py` - 抢单模块
- ✅ `donate_qr.png` - 捐赠二维码（可选）
- ✅ `config.example.json` - 示例配置（可选）

## ⚙️ 打包选项

### 自定义图标

1. **Windows**: 准备 `icon.ico` 文件
2. **Mac**: 准备 `icon.icns` 文件
3. 在对应的 `.spec` 文件中修改 `icon` 参数

### 修改应用名称

在 `.spec` 文件中修改 `name` 参数：
- Windows: `name='你的应用名称'`
- Mac: `name='你的应用名称.app'`

## 📦 打包结果

### Windows
- 输出文件：`dist/游戏抢单系统.exe`
- 文件大小：约 50-100 MB
- 运行方式：双击运行

### Mac
- 输出文件：`dist/游戏抢单系统.app`
- 文件大小：约 50-100 MB
- 运行方式：双击运行（首次可能需要右键"打开"）

## 🔧 常见问题

### Q: 打包失败怎么办？
A: 
1. 检查是否安装了所有依赖：`pip install -r requirements.txt`
2. 确保 Python 版本 >= 3.7
3. 查看错误信息，根据提示解决问题

### Q: 打包后的程序很大？
A: 这是正常的，因为包含了 Python 解释器和所有依赖库。可以使用 UPX 压缩（已在配置中启用）。

### Q: Windows 被杀毒软件拦截？
A: 这是正常现象，添加信任即可。如需避免，可以使用代码签名证书。

### Q: Mac 无法打开应用？
A: 
1. 右键点击应用，选择"打开"
2. 或在终端运行：`xattr -cr "游戏抢单系统.app"`

## 📚 更多信息

详细说明请查看 `BUILD_README.md`

