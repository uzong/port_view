import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from .port_scanner import scan_all_ports, get_port_statistics, kill_process


class PortMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Port Monitor - 端口监控工具")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f7fa')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_styles()
        self.create_widgets()
        
        self.refresh_interval = 3000
        self.auto_refresh = True
        self.refresh_thread = None
        
        self.start_auto_refresh()
    
    def setup_styles(self):
        self.style.configure('TFrame', background='#f5f7fa')
        self.style.configure('TLabel', background='#f5f7fa', foreground='#2c3e50', font=('Helvetica', 10))
        self.style.configure('Header.TLabel', background='#3498db', foreground='white', font=('Helvetica', 16, 'bold'))
        self.style.configure('Card.TFrame', background='white', relief='flat', borderwidth=0)
        self.style.configure('Card.TLabel', background='white', foreground='#2c3e50', font=('Helvetica', 11))
        self.style.configure('Status.TLabel', background='#e8f4f8', foreground='#3498db', font=('Helvetica', 10, 'bold'))
        self.style.configure('TCP.TLabel', background='#e8f4f8', foreground='#3498db', font=('Helvetica', 9))
        self.style.configure('UDP.TLabel', background='#fef5e6', foreground='#f39c12', font=('Helvetica', 9))
        self.style.configure('Treeview', rowheight=25, font=('Helvetica', 10))
        self.style.configure('Treeview.Heading', font=('Helvetica', 11, 'bold'), background='#3498db', foreground='white')
        self.style.map('Treeview', background=[('selected', '#3498db')], foreground=[('selected', 'white')])
        
        self.style.configure('TButton', font=('Helvetica', 11), padding=6)
        self.style.map('TButton', background=[('active', '#2980b9')])
        self.style.configure('Kill.TButton', font=('Helvetica', 10), padding=4, background='#e74c3c', foreground='white')
        self.style.map('Kill.TButton', background=[('active', '#c0392b')])
        self.style.configure('Refresh.TButton', font=('Helvetica', 10), padding=4, background='#3498db', foreground='white')
        self.style.map('Refresh.TButton', background=[('active', '#2980b9')])
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="端口监控工具", style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        stats_frame = ttk.Frame(main_frame, style='TFrame')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.total_label = self.create_stat_card(stats_frame, "总端口数", "0")
        self.tcp_label = self.create_stat_card(stats_frame, "TCP端口", "0")
        self.udp_label = self.create_stat_card(stats_frame, "UDP端口", "0")
        self.privileged_label = self.create_stat_card(stats_frame, "特权端口", "0")
        
        controls_frame = ttk.Frame(main_frame, style='TFrame')
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.refresh_button = ttk.Button(controls_frame, text="刷新", style='Refresh.TButton', command=self.manual_refresh)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        self.auto_refresh_check = ttk.Checkbutton(controls_frame, text="自动刷新", variable=self.auto_refresh_var, command=self.toggle_auto_refresh)
        self.auto_refresh_check.pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=30, font=('Helvetica', 10))
        self.search_entry.pack(side=tk.LEFT, padx=(20, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_ports)
        
        self.search_entry.insert(0, "🔍 搜索端口或进程...")
        self.search_entry.config(foreground='grey')
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        
        tree_frame = ttk.Frame(main_frame, style='TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('port', 'protocol', 'status', 'pid', 'user', 'command')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')
        
        self.tree.heading('port', text='端口')
        self.tree.heading('protocol', text='协议')
        self.tree.heading('status', text='状态')
        self.tree.heading('pid', text='PID')
        self.tree.heading('user', text='用户')
        self.tree.heading('command', text='进程命令')
        
        self.tree.column('port', width=80, anchor='center')
        self.tree.column('protocol', width=80, anchor='center')
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('pid', width=80, anchor='center')
        self.tree.column('user', width=120, anchor='center')
        self.tree.column('command', width=300, anchor='center')
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        self.status_label = ttk.Label(main_frame, text="就绪", style='TLabel')
        self.status_label.pack(fill=tk.X, pady=(10, 0))
    
    def create_stat_card(self, parent, label, value):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side=tk.LEFT, padx=10)
        
        value_label = ttk.Label(card, text=value, style='Card.TLabel', font=('Helvetica', 18, 'bold'))
        value_label.pack()
        
        label_label = ttk.Label(card, text=label, style='Card.TLabel', foreground='#7f8c8d')
        label_label.pack()
        
        return value_label
    
    def on_search_focus_in(self, event):
        if self.search_var.get() == "🔍 搜索端口或进程...":
            self.search_var.set("")
            self.search_entry.config(foreground='black')
    
    def on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("🔍 搜索端口或进程...")
            self.search_entry.config(foreground='grey')
    
    def filter_ports(self, event):
        self.refresh_ports()
    
    def toggle_auto_refresh(self):
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        if self.refresh_thread:
            self.stop_auto_refresh()
        self.refresh_ports()
        self.auto_refresh_loop()
    
    def stop_auto_refresh(self):
        if hasattr(self, '_refresh_after_id'):
            self.root.after_cancel(self._refresh_after_id)
    
    def auto_refresh_loop(self):
        if self.auto_refresh:
            self.refresh_ports()
            self._refresh_after_id = self.root.after(self.refresh_interval, self.auto_refresh_loop)
    
    def manual_refresh(self):
        self.stop_auto_refresh()
        self.refresh_ports()
        self.auto_refresh_loop()
    
    def refresh_ports(self):
        def update_ui():
            self.status_label.config(text="正在扫描端口...")
            self.root.update()
            
            search_text = self.search_var.get().lower()
            if search_text == "🔍 搜索端口或进程...":
                search_text = ""
            
            try:
                ports_info = scan_all_ports()
                stats = get_port_statistics(ports_info)
                
                self.total_label.config(text=str(stats['total_ports']))
                self.tcp_label.config(text=str(stats['tcp_ports']))
                self.udp_label.config(text=str(stats['udp_ports']))
                self.privileged_label.config(text=str(stats['privileged_ports']))
                
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                for port_info in ports_info:
                    port_num = port_info.get('port', 0)
                    protocol = port_info.get('protocol', 'Unknown')
                    status = port_info.get('status', 'Unknown')
                    
                    processes = port_info.get('processes', [])
                    
                    if processes:
                        for proc in processes:
                            pid = proc.get('pid', 'N/A')
                            user = proc.get('user', 'N/A')
                            command = proc.get('command', 'N/A')
                            
                            if search_text and search_text not in str(port_num).lower() and \
                               search_text not in command.lower() and \
                               search_text not in pid.lower() and \
                               search_text not in user.lower():
                                continue
                            
                            tag = 'tcp' if protocol == 'TCP' else 'udp'
                            self.tree.insert('', tk.END, values=(port_num, protocol, status, pid, user, command), tags=(tag,))
                    else:
                        if search_text:
                            continue
                        tag = 'tcp' if protocol == 'TCP' else 'udp'
                        self.tree.insert('', tk.END, values=(port_num, protocol, status, 'N/A', 'N/A', 'N/A'), tags=(tag,))
                
                self.tree.tag_configure('tcp', background='#e8f4f8')
                self.tree.tag_configure('udp', background='#fef5e6')
                
                self.status_label.config(text=f"最后更新: {time.strftime('%H:%M:%S')} | 共扫描到 {stats['total_ports']} 个端口")
                
            except Exception as e:
                self.status_label.config(text=f"错误: {str(e)}")
        
        self.root.after(0, update_ui)
    
    def on_item_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            port = values[0]
            pid = values[3]
            
            if pid != 'N/A':
                result = kill_process(pid)
                if result['success']:
                    messagebox.showinfo("成功", result['message'])
                    self.refresh_ports()
                else:
                    messagebox.showerror("错误", result['message'])
            else:
                messagebox.showwarning("警告", "无法确定要终止的进程")
    
    def on_closing(self):
        self.stop_auto_refresh()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = PortMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
