# 故障排查指南

## 问题：打包后的 exe 启动后是命令行版本，不是 GUI 窗口

### 原因
`main.py` 的默认行为是命令行模式，需要传递 `--gui` 参数才会启动 GUI。

### 解决方案
已修改 `main.py`，现在**默认启动 GUI 模式**。

### 修改内容
- **之前**：默认命令行模式，需要 `--gui` 参数启动 GUI
- **现在**：默认 GUI 模式，需要 `--cli` 参数启动命令行

### 验证
重新打包后，双击 exe 文件应该直接启动 GUI 窗口。

---

## 问题：打包后的 exe 点击后没反应

### 排查步骤

#### 1. 使用调试版本查看错误信息

**创建调试版本：**
```batch
pyinstaller build_windows_debug.spec
```

**运行调试版本：**
- 会显示控制台窗口，可以看到错误信息
- 根据错误信息定位问题

#### 2. 检查常见问题

**问题 A：缺少依赖模块**
- **症状**：控制台显示 `ModuleNotFoundError`
- **解决**：在 `build_windows.spec` 的 `hiddenimports` 中添加缺失的模块

**问题 B：路径问题**
- **症状**：找不到文件或资源
- **解决**：使用 `sys._MEIPASS` 获取临时目录路径
  ```python
  import sys
  if getattr(sys, 'frozen', False):
      # 打包后的路径
      base_path = sys._MEIPASS
  else:
      # 开发环境路径
      base_path = os.path.dirname(__file__)
  ```

**问题 C：PySide6 相关错误**
- **症状**：`ImportError` 或 `DLL load failed`
- **解决**：
  1. 确保 PySide6 已正确安装
  2. 检查 `hiddenimports` 中是否包含所有 PySide6 模块
  3. 尝试禁用 UPX 压缩（在 spec 文件中设置 `upx=False`）

**问题 D：杀毒软件拦截**
- **症状**：程序启动后立即退出
- **解决**：
  1. 添加杀毒软件信任
  2. 检查 Windows 事件查看器中的错误日志

#### 3. 手动测试

**在命令行中运行：**
```batch
cd dist
游戏抢单系统.exe
```

如果命令行中能看到错误信息，根据提示修复。

#### 4. 检查日志文件

程序可能会在以下位置生成日志：
- 程序运行目录
- 用户临时目录
- Windows 事件查看器

---

## 问题：GUI 窗口不显示

### 可能原因

1. **QApplication 未正确初始化**
   - 检查 `gui.py` 中的 `QApplication` 创建
   - 确保 `app.exec()` 被调用

2. **窗口被隐藏**
   - 检查 `window.show()` 是否被调用
   - 检查窗口是否在屏幕外

3. **异常被静默捕获**
   - 使用调试版本查看错误
   - 检查异常处理代码

### 解决方案

1. **添加启动日志**
   ```python
   import sys
   print("程序启动中...", file=sys.stderr)
   app = QApplication(sys.argv)
   print("QApplication 已创建", file=sys.stderr)
   window = GameOrderGrabberGUI()
   print("窗口已创建", file=sys.stderr)
   window.show()
   print("窗口已显示", file=sys.stderr)
   sys.exit(app.exec())
   ```

2. **使用调试版本**
   - 使用 `build_windows_debug.spec` 打包
   - 查看控制台输出的错误信息

---

## 问题：资源文件找不到

### 解决方案

**修改文件路径获取方式：**
```python
import sys
import os

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller 创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 使用示例
qr_image_path = resource_path("donate_qr.png")
```

**在 spec 文件中确保包含资源：**
```python
datas=[
    ('donate_qr.png', '.'),
    ('config.example.json', '.'),
],
```

---

## 调试技巧

### 1. 启用详细日志

在代码开头添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 使用调试版本打包

```batch
pyinstaller build_windows_debug.spec
```

### 3. 检查依赖

```batch
# 查看打包文件包含的模块
pyi-archive_viewer dist/游戏抢单系统.exe
```

### 4. 测试导入

在打包后的环境中测试：
```python
# 在临时目录中测试
import sys
print(sys.path)
import PySide6
print("PySide6 导入成功")
```

---

## 常见错误及解决方案

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `ModuleNotFoundError` | 缺少模块 | 添加到 `hiddenimports` |
| `DLL load failed` | 缺少 DLL | 检查 PySide6 安装 |
| `FileNotFoundError` | 路径错误 | 使用 `sys._MEIPASS` |
| 程序闪退 | 未捕获异常 | 使用调试版本查看错误 |
| 窗口不显示 | QApplication 问题 | 检查 GUI 初始化代码 |

---

## 获取帮助

如果问题仍然存在：

1. **使用调试版本**获取详细错误信息
2. **检查 Windows 事件查看器**中的应用程序日志
3. **在命令行中运行**查看输出
4. **检查杀毒软件日志**是否拦截

---

## 重新打包步骤

修复问题后，重新打包：

```batch
# 清理旧文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

# 重新打包
pyinstaller build_windows.spec
```

