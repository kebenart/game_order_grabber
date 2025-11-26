#!/bin/bash

echo "========================================"
echo "游戏抢单系统 - Mac 打包脚本"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.7 或更高版本"
    exit 1
fi

echo "[1/4] 检查依赖..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo ""
echo "[2/4] 清理旧的构建文件..."
rm -rf build dist "游戏抢单系统.spec"

echo ""
echo "[3/4] 开始打包..."
pyinstaller build_mac.spec
if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

echo ""
echo "[4/4] 打包完成！"
echo ""
echo "应用程序位置: dist/游戏抢单系统.app"
echo ""
echo "提示："
echo "- 首次运行可能需要右键点击并选择'打开'来绕过安全限制"
echo "- 程序需要网络连接才能正常工作"
echo "- 配置文件会自动生成在程序目录"
echo ""
echo "创建 DMG 安装包（可选）..."
read -p "是否创建 DMG 安装包？(y/n): " create_dmg

if [ "$create_dmg" = "y" ] || [ "$create_dmg" = "Y" ]; then
    if command -v create-dmg &> /dev/null; then
        create-dmg dist/游戏抢单系统.dmg dist/游戏抢单系统.app
        echo "DMG 安装包已创建: dist/游戏抢单系统.dmg"
    else
        echo "未安装 create-dmg，跳过 DMG 创建"
        echo "安装方法: brew install create-dmg"
    fi
fi

echo ""
echo "完成！"

