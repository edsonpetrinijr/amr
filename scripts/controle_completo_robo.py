from netprotocol.rbkNetProtoEnums import *
import netprotocol.rbkNetProtoEnums
import json
import socket
import struct
import time
import os
import threading

# ============ CONFIGURAÇÕES ============
ROBOT_IP = '10.101.251.137'  # Ajuste para o IP do seu robô

# Velocidades (ajuste conforme necessário)
VELOCIDADE_PADRAO = 0.3  # m/s - velocidade linear
VELOCIDADE_CURVA = 0.3   # rad/s - velocidade angular

# Jack/Base - IDs de Digital Output
JACK_UP_DO_ID = 1      # ID do DO para subir (ajuste conforme seu robô)
JACK_DOWN_DO_ID = 2    # ID do DO para descer (ajuste conforme seu robô)

# ============ FUNÇÕES ============

def conectar_robo_ctrl():
    """Conecta ao robô na porta de controle"""
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.connect((ROBOT_IP, API_PORT_CTRL))
    so.settimeout(10)
    print(f"✅ Conectado ao robô CTRL em {ROBOT_IP}:{API_PORT_CTRL}")
    return so

def conectar_robo_task():
    """Conecta ao robô na porta de tasks/navegação"""
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.connect((ROBOT_IP, API_PORT_TASK))
    so.settimeout(10)
    print(f"✅ Conectado ao robô TASK em {ROBOT_IP}:{API_PORT_TASK}")
    return so

def conectar_robo_other():
    """Conecta ao robô na porta OTHER (para DO/DI)"""
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.connect((ROBOT_IP, API_PORT_OTHER))
    so.settimeout(5)
    print(f"✅ Conectado ao robô OTHER em {ROBOT_IP}:{API_PORT_OTHER}")
    return so

def conectar_robo_state():
    """Conecta ao robô na porta de estado"""
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.connect((ROBOT_IP, API_PORT_STATE))
    so.settimeout(5)
    print(f"✅ Conectado ao robô STATE em {ROBOT_IP}:{API_PORT_STATE}")
    return so

def mover_robo_continuo(so, vx, vy, w, duracao=2):
    """
    Move o robô continuamente enviando comandos repetidamente
    vx: velocidade frente/trás (+ = frente, - = trás) em m/s
    vy: velocidade esquerda/direita (+ = esquerda, - = direita) em m/s
    w: velocidade angular (+ = anti-horário, - = horário) em rad/s
    duracao: tempo em segundos
    """
    print(f"🤖 Movendo CONTÍNUO: vx={vx}, vy={vy}, w={w} por {duracao}s")
    
    tempo_inicio = time.time()
    req_num = 1
    
    # Envia comandos continuamente durante a duração especificada
    while (time.time() - tempo_inicio) < duracao:
        so.send(packMsg(req_num, robot_control_motion_req, {"vx": vx, "vy": vy, "w": w}))
        req_num += 1
        
        # Aguarda um pouco antes de enviar o próximo comando
        time.sleep(0.1)  # Envia comandos a cada 100ms
    
    # Para o robô
    print("   🛑 Parando movimento...")
    so.send(packMsg(req_num, robot_control_motion_req, {"vx": 0, "vy": 0, "w": 0}))
    time.sleep(0.3)

def parar_robo(so):
    """Para completamente o robô"""
    print("🛑 Parando robô...")
    so.send(packMsg(5, robot_control_motion_req, {"vx": 0, "vy": 0, "w": 0}))
    time.sleep(0.5)

def controlar_jack(acao):
    """
    Controla o jack/base do robô via Digital Output
    acao: 'up' para subir ou 'down' para descer
    """
    try:
        so = conectar_robo_other()
        
        if acao == 'up':
            print("⬆️  Jack subindo...")
            # Ativa DO para subir
            so.send(packMsg(1, robot_other_setdo_req, {"id": JACK_UP_DO_ID, "status": True}))
            data = so.recv(16)
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = so.recv(1024)
                    ret = json.loads(data)
                    print(f"   Resposta: {ret}")
            
            time.sleep(3)  # Aguarda o movimento
            
            # Desativa DO
            so.send(packMsg(2, robot_other_setdo_req, {"id": JACK_UP_DO_ID, "status": False}))
            so.recv(16)
            
        elif acao == 'down':
            print("⬇️  Jack descendo...")
            # Ativa DO para descer
            so.send(packMsg(1, robot_other_setdo_req, {"id": JACK_DOWN_DO_ID, "status": True}))
            data = so.recv(16)
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = so.recv(1024)
                    ret = json.loads(data)
                    print(f"   Resposta: {ret}")
            
            time.sleep(3)  # Aguarda o movimento
            
            # Desativa DO
            so.send(packMsg(2, robot_other_setdo_req, {"id": JACK_DOWN_DO_ID, "status": False}))
            so.recv(16)
        
        so.close()
        print("   ✅ Ação do jack concluída")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao controlar jack: {e}")

def ir_para_landmark(landmark_id):
    """
    Envia o robô para um landmark específico (LM1, LM2, etc.)
    """
    try:
        print(f"🎯 Navegando para {landmark_id}...")
        
        so_task = conectar_robo_task()
        so_state = conectar_robo_state()
        
        # Envia comando para ir ao landmark
        so_task.send(packMsg(1, robot_task_gotarget_req, {"id": landmark_id}))
        
        try:
            data = so_task.recv(16)
            if len(data) >= 16:
                jsonDataLen, backReqNum = unpackHead(data)
                if jsonDataLen > 0:
                    data = so_task.recv(1024)
                    ret = json.loads(data)
                    print(f"   Comando enviado: {ret}")
        except socket.timeout:
            print("   ⚠️ Timeout ao enviar comando")
        
        # Monitora o status até chegar
        COMPLETED = 4
        chegou = False
        tentativas = 0
        max_tentativas = 100
        
        while not chegou and tentativas < max_tentativas:
            try:
                so_state.send(packMsg(1, robot_status_task_req, {}))
                data = so_state.recv(16)
                
                if len(data) >= 16:
                    jsonDataLen = unpackHead(data)[0]
                    if jsonDataLen > 0:
                        data = so_state.recv(1024)
                        ret = json.loads(data)
                        
                        if ret.get('task_status') == COMPLETED and ret.get('target_id') == landmark_id:
                            chegou = True
                            print(f"   ✅ Chegou em {landmark_id}!")
                        else:
                            print(f"   🔄 Status: {ret.get('task_status')} | Alvo: {ret.get('target_id')}")
                            time.sleep(0.5)
            except Exception as e:
                print(f"   ⚠️ Erro ao verificar status: {e}")
            
            tentativas += 1
        
        so_task.close()
        so_state.close()
        
        if not chegou:
            print(f"   ⚠️ Timeout: não chegou em {landmark_id}")
        
        return chegou
        
    except Exception as e:
        print(f"   ❌ Erro ao navegar: {e}")
        return False

# ============ DEMONSTRAÇÃO ============

def demo_completa():
    """Executa uma demonstração completa de todos os movimentos"""
    print("\n" + "="*50)
    print("🤖 DEMONSTRAÇÃO COMPLETA DE CONTROLE DO ROBÔ")
    print("="*50 + "\n")
    
    so = conectar_robo_ctrl()
    
    try:
        print("\n--- 1️⃣ MOVIMENTO PARA FRENTE ---")
        mover_robo_continuo(so, VELOCIDADE_PADRAO, 0, 0, duracao=3)
        time.sleep(1)
        
        print("\n--- 2️⃣ MOVIMENTO PARA TRÁS ---")
        mover_robo_continuo(so, -VELOCIDADE_PADRAO, 0, 0, duracao=3)
        time.sleep(1)
        
        print("\n--- 3️⃣ CURVA PARA ESQUERDA (ANTI-HORÁRIO) ---")
        mover_robo_continuo(so, 0, 0, VELOCIDADE_CURVA, duracao=3)
        time.sleep(1)
        
        print("\n--- 4️⃣ CURVA PARA DIREITA (HORÁRIO) ---")
        mover_robo_continuo(so, 0, 0, -VELOCIDADE_CURVA, duracao=3)
        time.sleep(1)
        
        print("\n--- 5️⃣ SUBIR JACK ---")
        controlar_jack('up')
        time.sleep(1)
        
        print("\n--- 6️⃣ DESCER JACK ---")
        controlar_jack('down')
        time.sleep(1)
        
        print("\n--- 7️⃣ MOVIMENTO DIAGONAL (FRENTE + ESQUERDA) ---")
        mover_robo_continuo(so, VELOCIDADE_PADRAO, VELOCIDADE_PADRAO, 0, duracao=2)
        time.sleep(1)
        
        print("\n✅ Demonstração completa finalizada!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    finally:
        parar_robo(so)
        so.close()
        print("\n🔌 Conexão fechada")

def demo_navegacao_landmarks():
    """Demonstração de navegação entre landmarks"""
    print("\n" + "="*50)
    print("🎯 DEMONSTRAÇÃO DE NAVEGAÇÃO POR LANDMARKS")
    print("="*50 + "\n")
    
    try:
        print("\n--- Navegando de LM1 para LM2 ---")
        
        # Vai para LM1
        print("\n🔹 Indo para LM1...")
        if ir_para_landmark("LM1"):
            print("✅ Em LM1")
            time.sleep(2)
            
            # Vai para LM2
            print("\n🔹 Indo para LM2...")
            if ir_para_landmark("LM2"):
                print("✅ Em LM2")
                time.sleep(2)
                
                # Retorna para LM1
                print("\n🔹 Retornando para LM1...")
                if ir_para_landmark("LM1"):
                    print("✅ Voltou para LM1")
        
        print("\n✅ Demonstração de navegação finalizada!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

# ============ MENU INTERATIVO ============

def menu_interativo():
    """Menu para controlar o robô manualmente"""
    print("\n" + "="*50)
    print("🎮 CONTROLE MANUAL DO ROBÔ")
    print("="*50)
    
    so = conectar_robo_ctrl()
    
    while True:
        print("\n📋 MENU DE OPÇÕES:")
        print("  1 - Mover para FRENTE")
        print("  2 - Mover para TRÁS")
        print("  3 - Curva ESQUERDA (anti-horário)")
        print("  4 - Curva DIREITA (horário)")
        print("  5 - SUBIR jack")
        print("  6 - DESCER jack")
        print("  7 - Mover ESQUERDA lateral")
        print("  8 - Mover DIREITA lateral")
        print("  9 - PARAR robô")
        print("  L - Ir para LANDMARK (LM1, LM2, etc.)")
        print("  0 - SAIR")
        
        try:
            opcao = input("\n👉 Escolha uma opção: ").strip()
            
            if opcao == '1':
                duracao = float(input("   Duração (segundos): "))
                mover_robo_continuo(so, VELOCIDADE_PADRAO, 0, 0, duracao=duracao)
            elif opcao == '2':
                duracao = float(input("   Duração (segundos): "))
                mover_robo_continuo(so, -VELOCIDADE_PADRAO, 0, 0, duracao=duracao)
            elif opcao == '3':
                duracao = float(input("   Duração (segundos): "))
                mover_robo_continuo(so, 0, 0, VELOCIDADE_CURVA, duracao=duracao)
            elif opcao == '4':
                duracao = float(input("   Duração (segundos): "))
                mover_robo_continuo(so, 0, 0, -VELOCIDADE_CURVA, duracao=duracao)
            elif opcao == '5':
                controlar_jack('up')
            elif opcao == '6':
                controlar_jack('down')
            elif opcao == '7':
                duracao = float(input("   Duração (segundos): "))
                mover_robo_continuo(so, 0, VELOCIDADE_PADRAO, 0, duracao=duracao)
            elif opcao == '8':
                duracao = float(input("   Duração (segundos): "))
                mover_robo_continuo(so, 0, -VELOCIDADE_PADRAO, 0, duracao=duracao)
            elif opcao == '9':
                parar_robo(so)
            elif opcao.upper() == 'L':
                landmark = input("   Digite o landmark (ex: LM1, LM2): ").strip()
                so.close()  # Fecha conexão CTRL antes de navegar
                ir_para_landmark(landmark)
                so = conectar_robo_ctrl()  # Reconecta para continuar
            elif opcao == '0':
                print("\n👋 Saindo...")
                break
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrompido!")
            break
        except ValueError:
            print("❌ Valor inválido!")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    parar_robo(so)
    so.close()
    print("🔌 Conexão fechada\n")

# ============ MAIN ============

if __name__ == "__main__":
    print("\n🤖 SISTEMA DE CONTROLE DO ROBÔ")
    print("\nEscolha o modo de operação:")
    print("  1 - Demonstração automática (movimentos básicos)")
    print("  2 - Demonstração navegação (LM1 <-> LM2)")
    print("  3 - Controle manual interativo")
    
    try:
        modo = input("\n👉 Modo: ").strip()
        
        if modo == '1':
            demo_completa()
        elif modo == '2':
            demo_navegacao_landmarks()
        elif modo == '3':
            menu_interativo()
        else:
            print("❌ Opção inválida!")
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    print("\n")
