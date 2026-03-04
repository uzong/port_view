#!/bin/bash

# Port Monitor 打包脚本
# 用于将 Python 项目打包成 macOS 应用程序

set -e

echo "=========================================="
echo "  Port Monitor 打包工具"
echo "=========================================="
echo ""

# 检查 Python 环境
echo "[1/5] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi
echo "✓ Python3 已安装"

# 安装依赖
echo ""
echo "[2/5] 安装依赖..."
python3 -m pip install -r requirements.txt --break-system-packages --quiet
echo "✓ 依赖安装完成"

# 清理旧的构建文件
echo ""
echo "[3/5] 清理旧的构建文件..."
rm -rf build dist *.spec
echo "✓ 清理完成"

# 打包应用程序
echo ""
echo "[4/5] 打包应用程序..."
python3 -m PyInstaller \
    --name="PortMonitor" \
    --windowed \
    --onefile \
    --clean \
    --noconfirm \
    --hidden-import=port_monitor.port_scanner \
    --hidden-import=port_monitor.gui \
    run.py

echo "✓ 打包完成"

# 创建应用程序包
echo ""
echo "[5/5] 创建应用程序包..."

# 创建输出目录
mkdir -p "PortMonitor-Tool"

# 复制可执行文件
cp "dist/PortMonitor" "PortMonitor-Tool/"

# 创建启动脚本
cat > "PortMonitor-Tool/启动端口监控工具.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./PortMonitor
EOF
chmod +x "PortMonitor-Tool/启动端口监控工具.command"

# 创建说明文件
cat > "PortMonitor-Tool/使用说明.txt" << 'EOF'
========================================
    Port Monitor - 端口监控工具
========================================

功能特点:
- 实时监控 macOS 系统端口占用情况
- 扁平化设计的可视化界面
- 支持自动刷新和手动刷新
- 快速搜索端口和进程
- 双击端口可直接终止进程

使用方法:
1. 双击 "启动端口监控工具.command" 运行程序
2. 或者在终端中运行: ./PortMonitor

系统要求:
- macOS 10.14 或更高版本
- 需要管理员权限才能终止某些系统进程

注意事项:
- 终止系统进程可能导致系统不稳定
- 请谨慎操作

========================================
EOF

echo "✓ 应用程序包创建完成"

echo ""
echo "=========================================="
echo "  打包成功!"
echo "=========================================="
echo ""
echo "输出目录: ./PortMonitor-Tool/"
echo ""
echo "文件列表:"
ls -la "PortMonitor-Tool/"
echo ""
echo "使用方法:"
echo "  1. 将整个 PortMonitor-Tool 文件夹复制到任意位置"
echo "  2. 双击 '启动端口监控工具.command' 即可运行"
echo ""
