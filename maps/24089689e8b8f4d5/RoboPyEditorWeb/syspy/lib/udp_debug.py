import socket,sys
import logging,logging.handlers
class udpDebug:
    def __init__(self):
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as e:
            pass
        
    def write(self, str1):
        try:
            str1 = str1.strip("\n")
            self.udp_socket.sendto(str1.encode("utf-8"), ("192.168.192.255", 20000))
        except Exception as e:
            pass
    
    def flush(self):
        pass

    def close(self):
        self.udp_socket.close()


class syslogDebug:
    def __init__(self, identifier="my_script"):
        """
        初始化SyslogLogger类，设置将print输出重定向到syslog。

        参数:
        - identifier: 标识符，用于标识日志来源（默认为'my_script'）
        """
        self.identifier = identifier
        self.logger = self._setup_logger()

        # 重定向stdout到syslog
        sys.stdout = self.SyslogRedirector(self.logger)

    def _setup_logger(self):
        # 设置syslog处理器
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')

        # 设置日志格式，添加标识符
        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
        syslog_handler.setFormatter(formatter)

        # 获取logger
        logger = logging.getLogger(self.identifier)
        logger.setLevel(logging.INFO)
        logger.addHandler(syslog_handler)
        return logger

    class SyslogRedirector:
        def __init__(self, logger):
            self.logger = logger

        def write(self, message):
            if message.strip():
                self.logger.info(message.strip())

        def flush(self):
            pass

import sys, socket, pdb, errno

class _UnbufferedIO:
    def __init__(self, stream):
        self._stream = stream
    def write(self, data):
        self._stream.write(data)
        self._stream.flush()
    def flush(self):
        self._stream.flush()
    def readline(self, *args):
        return self._stream.readline(*args)
    def read(self, *args):
        return self._stream.read(*args)

class RemotePdb(pdb.Pdb):
    def __init__(self, host='127.0.0.1', port=4444):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._sock.listen(1)
        print(f"[remote_pdb] waiting for debugger attach at {host}:{port} …")
        conn, _ = self._sock.accept()
        conn.send(b"*** remote pdb connected ***\n")
        rfile = conn.makefile('r')
        wfile = _UnbufferedIO(conn.makefile('w'))
        super().__init__(stdin=rfile, stdout=wfile)
        self._orig_stdout, self._orig_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = wfile

    def do_quit(self, arg):
        sys.stdout, sys.stderr = self._orig_stdout, self._orig_stderr
        super().do_quit(arg)
        try: self._sock.close()
        except: pass


_RPDB_INSTANCE = None

def set_trace(host='127.0.0.1', port=4444, max_tries=5):
    """
    用法：
        from 该模块 import set_trace
        在需要停下的地方set_trace() 
    """
    global _RPDB_INSTANCE
    if _RPDB_INSTANCE is None:
        # 尝试绑定端口
        for offset in range(max_tries):
            try:
                srv = RemotePdb(host, port + offset)
                bound = port + offset
                break
            except OSError as e:
                if getattr(e, 'errno', None) == errno.EADDRINUSE:
                    continue
                raise
        else:
            raise OSError(f"无法绑定远程调试端口 {port}~{port+max_tries-1}，均已被占用")

        print(f"[remote_pdb] bound to {host}:{bound}，请通过 telnet/nc 连接")
        _RPDB_INSTANCE = srv
    else:
        pass

    _RPDB_INSTANCE.set_trace(sys._getframe().f_back)


if __name__ == "__main__":
    pass