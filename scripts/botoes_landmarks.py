"""
Integração de botões OPC UA (Kepware) com navegação por landmarks do robô.

- BTN011 (borda de subida): envia o robô de LM1 -> LM2
- BTN012 (borda de subida): envia o robô de LM2 -> LM1

Reaproveita a função `ir_para_landmark` de controle_completo_robo.py
"""

import asyncio
import threading
from asyncua import Client

from controle_completo_robo import ir_para_landmark

# ============ CONFIGURAÇÕES ============
OPC_URL = "opc.tcp://192.168.1.1:4840"

# NodeIDs dos botões no Kepware
BTN_LM1_TO_LM2 = "ns=1;s=boolBTN011"  # Botão que envia LM1 -> LM2
BTN_LM2_TO_LM1 = "ns=1;s=boolBTN012"  # Botão que envia LM2 -> LM1

# Landmarks de destino
LANDMARK_A = "LM1"
LANDMARK_B = "LM2"

# Intervalo de polling dos botões (segundos)
POLL_INTERVAL = 0.2

# ============ ESTADO ============
# Trava para garantir que apenas uma navegação ocorra por vez
_navegando_lock = threading.Lock()
_navegando = False


def _executar_navegacao(destino: str):
    """Executa a navegação em uma thread separada para não bloquear o polling OPC."""
    global _navegando

    with _navegando_lock:
        if _navegando:
            print(f"⚠️  Já existe uma navegação em andamento. Ignorando pedido para {destino}.")
            return
        _navegando = True

    def _worker():
        global _navegando
        try:
            print(f"\n🚀 Iniciando navegação para {destino}...")
            ir_para_landmark(destino)
        except Exception as e:
            print(f"❌ Erro durante navegação para {destino}: {e}")
        finally:
            with _navegando_lock:
                _navegando = False
            print(f"🏁 Navegação para {destino} finalizada.\n")

    threading.Thread(target=_worker, daemon=True).start()


async def monitorar_botoes():
    """Conecta ao Kepware e monitora os dois botões com detecção de borda de subida."""
    client = Client(url=OPC_URL)

    try:
        await client.connect()
        print(f"✅ Conectado ao Kepware em {OPC_URL}")

        node_btn1 = client.get_node(BTN_LM1_TO_LM2)
        node_btn2 = client.get_node(BTN_LM2_TO_LM1)

        # Estado anterior - inicializa com o valor atual para evitar disparo na inicialização
        try:
            estado_btn1 = await node_btn1.read_value()
            estado_btn2 = await node_btn2.read_value()
        except Exception:
            estado_btn1 = False
            estado_btn2 = False

        print(f"📡 Monitorando botões:")
        print(f"   • {BTN_LM1_TO_LM2}  →  {LANDMARK_A} para {LANDMARK_B}")
        print(f"   • {BTN_LM2_TO_LM1}  →  {LANDMARK_B} para {LANDMARK_A}")
        print("   (Pressione Ctrl+C para sair)\n")

        while True:
            try:
                valor_btn1 = await node_btn1.read_value()
                valor_btn2 = await node_btn2.read_value()

                # Detecção de borda de subida (False -> True)
                if valor_btn1 and not estado_btn1:
                    print(f"🔘 Botão 1 pressionado ({BTN_LM1_TO_LM2})")
                    _executar_navegacao(LANDMARK_B)

                if valor_btn2 and not estado_btn2:
                    print(f"🔘 Botão 2 pressionado ({BTN_LM2_TO_LM1})")
                    _executar_navegacao(LANDMARK_A)

                estado_btn1 = valor_btn1
                estado_btn2 = valor_btn2

            except Exception as e:
                print(f"⚠️  Erro ao ler botões: {e}")

            await asyncio.sleep(POLL_INTERVAL)

    except Exception as e:
        print(f"❌ Erro de conexão OPC UA: {e}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        print("🔌 Desconectado do Kepware.")


def main():
    print("\n" + "=" * 60)
    print("🤖 INTEGRAÇÃO BOTÕES OPC UA ↔ NAVEGAÇÃO POR LANDMARKS")
    print("=" * 60 + "\n")

    try:
        asyncio.run(monitorar_botoes())
    except KeyboardInterrupt:
        print("\n\n👋 Encerrado pelo usuário.")


if __name__ == "__main__":
    main()
