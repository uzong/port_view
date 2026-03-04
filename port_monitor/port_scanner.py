import subprocess
import re


def parse_lsof_output(output):
    """解析 lsof 命令的输出"""
    ports_info = {}
    lines = output.strip().split('\n')
    
    for line in lines[1:]:  # 跳过标题行
        parts = line.split()
        if len(parts) < 9:
            continue
        
        command = parts[0]
        pid = parts[1]
        user = parts[2]
        fd = parts[3]
        conn_type = parts[4]
        device = parts[5]
        size = parts[6]
        node = parts[7]
        name = parts[8]
        
        # 解析端口号
        port_match = re.search(r':(\d+)', name)
        if port_match:
            port = int(port_match.group(1))
        else:
            continue
        
        # 解析协议
        protocol = 'TCP' if 'TCP' in line else 'UDP'
        
        # 解析状态
        if '(LISTEN)' in line:
            status = 'LISTEN'
        elif '(ESTABLISHED)' in line:
            status = 'ESTABLISHED'
        else:
            status = 'UNKNOWN'
        
        # 只保留 LISTEN 状态的端口
        if status != 'LISTEN':
            continue
        
        process_info = {
            'pid': pid,
            'user': user,
            'command': command,
            'fd': fd,
            'type': conn_type,
            'device': device,
            'size': size,
            'node': node,
            'name': name
        }
        
        if port not in ports_info:
            ports_info[port] = {
                'port': port,
                'protocol': protocol,
                'status': status,
                'processes': []
            }
        
        ports_info[port]['processes'].append(process_info)
    
    return list(ports_info.values())


def scan_all_ports():
    """扫描所有监听的端口"""
    try:
        result = subprocess.run(
            ['lsof', '-i', '-P', '-n'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            ports_info = parse_lsof_output(result.stdout)
            ports_info.sort(key=lambda x: x['port'])
            return ports_info
        else:
            print(f"lsof error: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"Error scanning ports: {e}")
        return []


def get_port_info(port_number):
    """获取指定端口的详细信息"""
    try:
        result = subprocess.run(
            ['lsof', '-i', f':{port_number}', '-P', '-n'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            ports_info = parse_lsof_output(result.stdout)
            for info in ports_info:
                if info['port'] == port_number:
                    return info
        
        return None
        
    except Exception as e:
        print(f"Error getting port info: {e}")
        return None


def kill_process(pid):
    """终止指定 PID 的进程"""
    try:
        result = subprocess.run(
            ['kill', str(pid)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {'success': True, 'message': f'Process {pid} terminated successfully'}
        else:
            return {'success': False, 'message': f'Failed to kill process {pid}: {result.stderr}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error killing process {pid}: {str(e)}'}


def get_port_statistics(ports_info):
    """获取端口统计信息"""
    total_ports = len(ports_info)
    tcp_ports = sum(1 for p in ports_info if p.get('protocol') == 'TCP')
    udp_ports = sum(1 for p in ports_info if p.get('protocol') == 'UDP')
    privileged_ports = sum(1 for p in ports_info if p.get('port', 0) < 1024)
    
    return {
        'total_ports': total_ports,
        'tcp_ports': tcp_ports,
        'udp_ports': udp_ports,
        'privileged_ports': privileged_ports
    }
