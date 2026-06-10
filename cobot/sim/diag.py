"""Diagnostico de conexao com o robo real: mostra exatamente o que acontece
com as portas 20003/20005/20007 e tenta ler as juntas."""
import sys, os, socket, time, contextlib, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.58.2"

def port_state(ip, port, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port)); s.close(); return "aberta"
    except ConnectionRefusedError:
        return "recusada"
    except socket.timeout:
        return "timeout/filtrada"
    except Exception as e:
        return f"erro {e}"

print(f"== Portas em {IP} ==")
for p in (20003, 20004, 20005, 20007):
    print(f"  {p}: {port_state(IP, p)}")

print("\n== Construindo Robot.RPC (capturando prints do SDK) ==")
from fairino import Robot
buf = io.StringIO()
t0 = time.time()
with contextlib.redirect_stdout(buf):
    robot = Robot.RPC(IP)
dt = time.time() - t0
out = buf.getvalue()
for line in out.splitlines():
    if any(k in line for k in ("20005", "20007", "CNDE", "UDP", "XML")):
        print("  SDK>", line)
print(f"  (construcao levou {dt:.1f}s)")
print("  is_connect (antes do bypass):", Robot.RPC.is_connect)

print("\n== Bypass ==")
Robot.RPC.is_connect = True
print("  is_connect (depois):", Robot.RPC.is_connect)

print("\n== Leitura de juntas ==")
t0 = time.time()
res = robot.GetActualJointPosDegree(1)
print(f"  GetActualJointPosDegree -> {res}   ({time.time()-t0:.2f}s)")

print("\n== Leitura TCP ==")
res2 = robot.GetActualTCPPose(1)
print(f"  GetActualTCPPose -> {res2}")
print("\nOK")
