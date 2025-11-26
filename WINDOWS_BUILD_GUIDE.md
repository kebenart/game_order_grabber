# Windows 打包指南

## ⚠️ 重要说明

**PyInstaller 无法在 Mac 上直接打包 Windows 的 exe 文件**。PyInstaller 只能为当前运行的操作系统打包。

## 🎯 解决方案

### 方案 1：在 Windows 系统上打包（推荐）

1. **准备 Windows 环境**
   - 安装 Python 3.7 或更高版本
   - 安装 Git（可选）

2. **在 Windows 上执行打包**
   ```batch
   # 克隆或复制项目到 Windows 系统
   cd game_order_grabber
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 执行打包
   build_windows.bat
   # 或
   pyinstaller build_windows.spec
   ```

3. **打包结果**
   - 可执行文件：`dist\游戏抢单系统.exe`

### 方案 2：使用 GitHub Actions（自动化）

创建一个 `.github/workflows/build.yml` 文件：

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Build executable
        run: |
          pyinstaller build_windows.spec
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-exe
          path: dist/游戏抢单系统.exe
```

### 方案 3：使用 Docker（跨平台）

1. **创建 Dockerfile.windows**
   ```dockerfile
   FROM python:3.9-windowsservercore
   
   WORKDIR /app
   COPY . .
   
   RUN pip install -r requirements.txt
   RUN pyinstaller build_windows.spec
   
   CMD ["cmd"]
   ```

2. **构建和运行**
   ```bash
   docker build -f Dockerfile.windows -t game-grabber-win .
   docker run -v %cd%\dist:/app/dist game-grabber-win
   ```

### 方案 4：使用虚拟机

1. 在 Mac 上安装 Windows 虚拟机（VMware、Parallels、VirtualBox）
2. 在虚拟机中安装 Python 和依赖
3. 在虚拟机中执行打包

## 📋 Windows 打包步骤（详细）

### 1. 环境准备

```batch
# 检查 Python 版本
python --version

# 应该显示 Python 3.7 或更高版本
```

### 2. 安装依赖

```batch
# 安装 PyInstaller 和项目依赖
pip install -r requirements.txt
```

### 3. 执行打包

**方法 A：使用批处理脚本（推荐）**
```batch
build_windows.bat
```

**方法 B：手动执行**
```batch
# 清理旧文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

# 执行打包
pyinstaller build_windows.spec
```

### 4. 验证结果

```batch
# 检查生成的文件
dir dist\游戏抢单系统.exe

# 测试运行
dist\游戏抢单系统.exe --gui
```

## 🔧 常见问题

### Q: 为什么在 Mac 上无法打包 Windows exe？
A: PyInstaller 使用当前系统的工具链和库，无法跨平台打包。必须在目标平台上打包。

### Q: 可以使用交叉编译吗？
A: PyInstaller 不支持交叉编译。必须使用目标平台。

### Q: 打包后的文件在哪里？
A: 在 `dist` 文件夹中，文件名为 `游戏抢单系统.exe`

### Q: 如何减小文件大小？
A: 
- 使用 UPX 压缩（已在配置中启用）
- 排除不需要的模块
- 使用 `--onefile` 模式（已在配置中）

### Q: 被杀毒软件拦截怎么办？
A: 
- 添加杀毒软件信任
- 使用代码签名证书（需要购买）
- 在打包时使用 `--clean` 选项

## 📦 打包后的文件结构

```
dist/
  └── 游戏抢单系统.exe  (单文件可执行程序，约 50-100 MB)
```

## 🚀 快速开始（Windows）

如果您有 Windows 系统，最简单的方法是：

1. 将项目文件复制到 Windows 系统
2. 双击运行 `build_windows.bat`
3. 等待打包完成
4. 在 `dist` 文件夹中找到 `游戏抢单系统.exe`

## 💡 提示

- 首次打包可能需要 5-10 分钟
- 打包后的 exe 文件可以在任何 Windows 系统上运行（无需安装 Python）
- 建议在 Windows 10/11 上打包以确保兼容性

