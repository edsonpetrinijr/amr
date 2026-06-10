# Aprendizados — Fairino SDK (essencial)

Fatos técnicos descobertos e validados neste robô (`192.168.58.2`, Python 3.13).

## SDK: usar a versão pure-Python
- Download `fairino-python-sdk-main` tem duas opções no Windows:
  - `windows\libfairino` → só `.pyd` compilado (cp310/311/312). **Não roda no 3.13.**
  - `windows\fairino\Robot.py` → **pure-Python, roda em qualquer versão.** ← usar esta.
- Copiar `Robot.py` para uma pasta `fairino/` com `__init__.py` vazio → `from fairino import Robot`. Não precisa instalar nada.

## Bypass de conexão obrigatório neste firmware
- SDK novo exige porta **CNDE 20005** (dados de estado). Este firmware **não abre** a 20005.
- Sem ela, o SDK seta `is_connect=False` e o decorator `@xmlrpc_timeout` faz **todo** comando retornar `-4` sem enviar nada (robô não se mexe, mas não dá erro).
- Solução: após conectar, forçar `Robot.RPC.is_connect = True`.
- Comandos de movimento usam **XML-RPC na 20003** (funciona). A 20004 também está aberta.

## Porta UDP 20007 (SDK novo) — ruído inofensivo
- O SDK novo abre, no construtor, um `FrUdpClient` na **20007** (controle servoJ/MIT) e
  um *auto-reconnect* que tenta a 20005 em loop. Neste firmware a 20007 está **filtrada**.
- Os prints em chinês (`CNDE连接失败`, `FrUdpClient ... 20007`, `is_connect = False`) são
  **esperados e inofensivos** — a leitura de juntas/TCP e o `MoveJ` continuam pela 20003.
- Para evitar travas e silenciar o ruído, em `FairinoRobot.connect()` também fazemos:
  `RPC._reconnect_enable = False`, `robot.reconnect_flag = False` e
  `robot._udp_client.stop_recv_thread()`. Confirmado: depois disso, `GetActualJointPosDegree`
  responde em ~0,08 s.
- Diagnóstico rápido das portas + leitura: `python sim\diag.py 192.168.58.2`.

## Portas do robô (verificado)
| Porta | Função | Status |
|-------|--------|--------|
| 20003 | XML-RPC (comandos) | aberta ✅ |
| 20004 | status clássico | aberta ✅ |
| 20005 | CNDE (status novo) | filtrada/recusada ❌ |
| 20007 | UDP (servoJ/MIT, SDK novo) | filtrada ❌ (inofensiva) |

## API — formatos de retorno
- `Robot.RPC(ip)` — construtor (default `192.168.58.2`).
- `RobotEnable(state)` → `0`/`None` em sucesso.
- `MoveJ(joint_pos, tool, user, vel=...)` → joint_pos em **graus**, `vel` em % (0–100). Retorna código (`0`=ok, negativo=erro).
- `MoveL(desc_pos, tool, user, ...)` → pose cartesiana.
- `GetActualJointPosDegree(flag=1)` → **sucesso: `(0, [j1..j6])`** ; falha: int de erro. (Padrão `(codigo, dados)` na maioria dos getters.)

## Ambiente
- Python 3.13.9. `opencv-python` 4.13 (tem `cv2.aruco`), `numpy` 2.x.
- Câmera: webcam USB via `cv2.VideoCapture(index, cv2.CAP_DSHOW)` (mais estável no Windows).
