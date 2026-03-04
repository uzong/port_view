# 端口监控工具 (Port Monitor)
<img width="2282" height="1508" alt="image" src="https://github.com/user-attachments/assets/8d1f6301-8d1c-490d-bbf2-10e001c24581" />

一个用于监控和管理 macOS 上端口占用情况的可视化工具。

## 功能特点

- 📊 **实时监控**: 实时显示系统中所有监听的端口
- 🎨 **扁平化设计**: 现代化的扁平化界面设计
- 🔄 **自动刷新**: 支持自动和手动刷新端口信息
- 🔍 **快速搜索**: 可以按端口号、进程名、用户等快速搜索
- 📈 **统计信息**: 显示端口统计信息（TCP/UDP/特权端口）
- ⚡ **快速管理**: 双击端口行可以直接终止对应进程

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python run.py
```

## 系统要求

- macOS
- Python 3.6+

## 使用说明

1. **查看端口**: 程序启动后会自动扫描并显示所有监听的端口
2. **搜索**: 在搜索框中输入端口号、进程名或用户进行过滤
3. **刷新**: 点击"刷新"按钮或启用"自动刷新"来更新端口信息
4. **终止进程**: 双击端口行，输入密码后可以终止对应进程

## 技术栈

- Python 3
- Tkinter (GUI)
- psutil (系统进程信息)
- subprocess (调用 lsof 命令)

## 许可证

MIT License
