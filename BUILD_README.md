# 打包说明文档

本指南将帮助您将游戏抢单系统打包成 Windows 和 Mac 的安装包。

## 前置要求

### Windows
- Python 3.7 或更高版本
- pip（Python 包管理器）

### Mac
- Python 3.7 或更高版本
- pip3（Python 包管理器）
- Xcode Command Line Tools（可选，用于创建 DMG）

## 快速开始

### Windows 打包

1. **打开命令提示符（CMD）或 PowerShell**
   - 导航到项目目录：`cd /path/to/game_order_grabber`

2. **运行打包脚本**
   ```batch
   build_windows.bat
   ```

3. **等待打包完成**
   - 打包完成后，可执行文件位于 `dist\游戏抢单系统.exe`

### Mac 打包

1. **打开终端（Terminal）**
   - 导航到项目目录：`cd /path/to/game_order_grabber`

2. **给脚本添加执行权限**
   ```bash
   chmod +x build_mac.sh
   ```

3. **运行打包脚本**
   ```bash
   ./build_mac.sh
   ```

4. **等待打包完成**
   - 打包完成后，应用程序位于 `dist/游戏抢单系统.app`

## 手动打包（高级用户）

### Windows 手动打包

```batch
# 1. 安装依赖
pip install -r requirements.txt

# 2. 使用 spec 文件打包
pyinstaller build_windows.spec
```

### Mac 手动打包

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 使用 spec 文件打包
pyinstaller build_mac.spec
```

## 打包选项说明

### build_windows.spec
- **console=False**: 不显示控制台窗口（GUI 模式）
- **name**: 可执行文件名称
- **datas**: 包含的数据文件（二维码、示例配置等）

### build_mac.spec
- **console=False**: 不显示控制台窗口（GUI 模式）
- **name**: 应用程序名称
- **bundle_identifier**: 应用程序标识符
- **info_plist**: Mac 应用程序信息配置

## 创建安装包

### Windows - 创建安装程序

可以使用以下工具创建安装程序：
- **Inno Setup**（推荐）：免费，功能强大
- **NSIS**：开源安装程序制作工具
- **WiX Toolset**：微软官方工具

#### 使用 Inno Setup 示例

1. 下载并安装 [Inno Setup](https://jrsoftware.org/isdl.php)
2. 创建 `.iss` 脚本文件
3. 编译生成 `.exe` 安装程序

### Mac - 创建 DMG 安装包

1. **安装 create-dmg**
   ```bash
   brew install create-dmg
   ```

2. **创建 DMG**
   ```bash
   create-dmg dist/游戏抢单系统.dmg dist/游戏抢单系统.app
   ```

或者使用打包脚本中的自动创建选项。

## 文件说明

打包后的文件结构：

### Windows
```
dist/
  └── 游戏抢单系统.exe  (可执行文件)
```

### Mac
```
dist/
  └── 游戏抢单系统.app/  (应用程序包)
      ├── Contents/
      │   ├── MacOS/
      │   │   └── 游戏抢单系统  (可执行文件)
      │   ├── Resources/
      │   └── Info.plist
      └── ...
```

## 包含的文件

打包时会自动包含以下文件：
- `donate_qr.png` - 捐赠二维码
- `config.example.json` - 示例配置文件

其他文件（如 `config.json`、`accesstoken.txt` 等）会在首次运行时自动生成。

## 常见问题

### 1. 打包失败：找不到模块

**解决方案**：
- 确保所有依赖都已安装：`pip install -r requirements.txt`
- 检查 `hiddenimports` 列表是否包含所有需要的模块

### 2. Windows：被杀毒软件拦截

**解决方案**：
- 这是正常现象，因为 PyInstaller 打包的程序可能被误报
- 添加杀毒软件信任或使用代码签名证书

### 3. Mac：无法打开应用程序

**解决方案**：
- 右键点击应用程序，选择"打开"
- 或者在终端运行：`xattr -cr "游戏抢单系统.app"`

### 4. 文件大小过大

**解决方案**：
- 使用 `--onefile` 模式（已在 spec 文件中配置）
- 考虑使用 UPX 压缩（需要安装 UPX）

### 5. 缺少图标

**解决方案**：
- Windows：准备 `.ico` 文件，在 spec 文件中设置 `icon='icon.ico'`
- Mac：准备 `.icns` 文件，在 spec 文件中设置 `icon='icon.icns'`

## 测试打包结果

### Windows
1. 双击 `dist\游戏抢单系统.exe` 运行
2. 测试所有功能是否正常

### Mac
1. 双击 `dist/游戏抢单系统.app` 运行
2. 测试所有功能是否正常

## 分发建议

1. **Windows**
   - 创建安装程序（.exe 或 .msi）
   - 提供使用说明文档
   - 考虑代码签名（可选）

2. **Mac**
   - 创建 DMG 安装包
   - 提供使用说明文档
   - 考虑代码签名和公证（可选，需要 Apple Developer 账号）

## 更新日志

- v1.0.0: 初始打包配置

## 技术支持

如有问题，请查看：
- PyInstaller 文档：https://pyinstaller.org/
- 项目 README 文件

