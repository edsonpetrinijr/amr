from netprotocol.rbkNetProtoEnums import *
import netprotocol.rbkNetProtoEnums
import json
import socket
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, TextBox
import numpy as np
from collections import deque
import threading
import queue

# ============ CONFIGURAÇÕES ============
TAMANHO_ROBO = 0.5  # metros
COMPRIMENTO_TRAJETORIA = 500  # número de pontos da trajetória
INTERVALO_ATUALIZACAO = 100  # ms
INTERVALO_RECONEXAO = 5  # segundos para tentar reconectar

# Cores para múltiplos robôs
CORES_ROBOS = [
    ('blue', 'darkblue'),
    ('green', 'darkgreen'),
    ('orange', 'darkorange'),
    ('purple', 'darkviolet'),
    ('cyan', 'darkcyan'),
    ('magenta', 'darkmagenta'),
]

# ============ CLASSE ROBÔ ============

class RoboMonitorado:
    def __init__(self, ip, nome, cor_index=0):
        self.ip = ip
        self.nome = nome
        self.cor_principal, self.cor_borda = CORES_ROBOS[cor_index % len(CORES_ROBOS)]
        
        # Conexões
        self.so_state = None
        self.so_area = None
        self.conectado = False
        self.tentando_reconectar = False
        self.ultima_tentativa_conexao = 0
        
        # Dados do robô
        self.pos_x = 0
        self.pos_y = 0
        self.angulo = 0
        self.velocidade_linear = 0
        self.velocidade_angular = 0
        self.target_id = None
        self.task_status = None
        
        # Trajetória
        self.trajetoria_x = deque(maxlen=COMPRIMENTO_TRAJETORIA)
        self.trajetoria_y = deque(maxlen=COMPRIMENTO_TRAJETORIA)
        
        # Áreas detectadas
        self.areas_detectadas = []
        
        # Elementos gráficos
        self.robo_patch = None
        self.trajetoria_line = None
        self.sensor_patches = []
        self.target_marker = None
        self.label_text = None
    
    def tentar_conectar(self):
        """Tenta conectar ao robô"""
        try:
            # Conexão para localização e estado
            self.so_state = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.so_state.settimeout(2.0)
            self.so_state.connect((self.ip, API_PORT_STATE))
            
            # Conexão para áreas/sensores
            self.so_area = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.so_area.settimeout(2.0)
            self.so_area.connect((self.ip, API_PORT_STATE))
            
            self.conectado = True
            print(f"  ✅ {self.nome} ({self.ip}) conectado!")
            return True
            
        except Exception as e:
            self.conectado = False
            if self.so_state:
                try:
                    self.so_state.close()
                except:
                    pass
            if self.so_area:
                try:
                    self.so_area.close()
                except:
                    pass
            self.so_state = None
            self.so_area = None
            return False
    
    def desconectar(self):
        """Desconecta do robô"""
        self.conectado = False
        if self.so_state:
            try:
                self.so_state.close()
            except:
                pass
        if self.so_area:
            try:
                self.so_area.close()
            except:
                pass
        self.so_state = None
        self.so_area = None
    
    def ler_dados(self):
        """Lê todos os dados do robô"""
        if not self.conectado:
            return False
        
        try:
            # Lê posição
            self.so_state.send(packMsg(1, robot_status_loc_req, {}))
            data = self.so_state.recv(16)
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    self.pos_x = ret.get('x', self.pos_x)
                    self.pos_y = ret.get('y', self.pos_y)
                    self.angulo = ret.get('angle', self.angulo)
            
            time.sleep(0.05)
            
            # Lê task
            self.so_state.send(packMsg(2, robot_status_task_req, {}))
            data = self.so_state.recv(16)
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    self.target_id = ret.get('target_id', None)
                    self.task_status = ret.get('task_status', None)
            
            time.sleep(0.05)
            
            # Lê velocidade
            self.so_state.send(packMsg(3, robot_status_speed_req, {}))
            data = self.so_state.recv(16)
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    vx = ret.get('vx', 0)
                    vy = ret.get('vy', 0)
                    self.velocidade_linear = np.sqrt(vx**2 + vy**2)
                    self.velocidade_angular = ret.get('w', 0)
            
            time.sleep(0.05)
            
            # Lê áreas
            self.so_area.send(packMsg(4, robot_status_area_req, {}))
            data = self.so_area.recv(16)
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_area.recv(2048)
                    ret = json.loads(data)
                    self.areas_detectadas = ret.get('area_ids', [])
            
            return True
            
        except socket.timeout:
            return True  # Timeout não é erro crítico
        except Exception as e:
            print(f"  ⚠️ {self.nome} perdeu conexão: {e}")
            self.desconectar()
            return False

# ============ CLASSE VISUALIZADOR MULTI-ROBÔ ============

class VisualizadorMultiRobo:
    def __init__(self):
        # Lista de robôs
        self.robos = []
        self.landmarks = {}
        
        # Thread de reconexão
        self.thread_reconexao = None
        self.rodando = True
        
        # Inicializa figura
        self.fig = plt.figure(figsize=(16, 11))
        
        # Área principal do mapa
        self.ax = plt.subplot2grid((10, 3), (0, 0), rowspan=9, colspan=3)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('X (metros)', fontsize=12)
        self.ax.set_ylabel('Y (metros)', fontsize=12)
        self.ax.set_title('🤖 VISUALIZAÇÃO MULTI-ROBÔ - RoboShop Pro', 
                         fontsize=14, fontweight='bold')
        
        # Painel de informações
        self.ax_info = plt.subplot2grid((10, 3), (9, 0), colspan=3)
        self.ax_info.axis('off')
        self.info_text = self.ax_info.text(0.02, 0.5, '', 
                                          verticalalignment='center',
                                          fontsize=9,
                                          family='monospace')
        
        # Origem (0, 0)
        self.ax.plot(0, 0, 'ko', markersize=10, zorder=9)
        self.ax.text(0.15, -0.25, '(0,0)', fontsize=10, fontweight='bold')
        
        # Eixos de referência
        self.ax.arrow(0, 0, 1.5, 0, head_width=0.2, head_length=0.3, 
                     fc='red', ec='red', alpha=0.7, zorder=5, linewidth=2)
        self.ax.text(1.8, 0.1, 'X', fontsize=14, fontweight='bold', color='red')
        
        self.ax.arrow(0, 0, 0, 1.5, head_width=0.2, head_length=0.3, 
                     fc='green', ec='green', alpha=0.7, zorder=5, linewidth=2)
        self.ax.text(0.1, 1.8, 'Y', fontsize=14, fontweight='bold', color='green')
        
        # Limites iniciais
        self.ax.set_xlim(-3, 12)
        self.ax.set_ylim(-3, 12)
        
        print("\n✅ Visualizador iniciado (modo offline)")
        print("📌 Adicione robôs para começar a monitorar\n")
    
    def adicionar_robo(self, ip, nome=None):
        """Adiciona um robô para monitoramento"""
        if nome is None:
            nome = f"Robô_{len(self.robos)+1}"
        
        # Verifica se já existe
        for robo in self.robos:
            if robo.ip == ip:
                print(f"  ⚠️ Robô {ip} já está sendo monitorado")
                return None
        
        print(f"🔄 Adicionando {nome} ({ip})...")
        
        robo = RoboMonitorado(ip, nome, len(self.robos))
        
        # Cria elementos gráficos
        robo.trajetoria_line, = self.ax.plot([], [], '-', alpha=0.5, 
                                             linewidth=2, 
                                             color=robo.cor_principal,
                                             label=f'{nome}')
        
        robo.target_marker, = self.ax.plot([], [], '*', markersize=20, 
                                          color=robo.cor_principal,
                                          zorder=9)
        
        self.robos.append(robo)
        self.ax.legend(loc='upper right')
        
        # Tenta conectar
        if robo.tentar_conectar():
            # Busca landmarks na primeira conexão
            if len(self.landmarks) == 0:
                self.buscar_landmarks_do_robo(robo)
        else:
            print(f"  ⚠️ Não conectado (tentará reconectar automaticamente)")
        
        return robo
    
    def buscar_landmarks_do_robo(self, robo):
        """Busca landmarks do robô conectado"""
        try:
            print(f"  🔍 Buscando landmarks de {robo.nome}...")
            
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.settimeout(5)
            so.connect((robo.ip, API_PORT_ROBOD))
            
            # Lista arquivos
            so.send(packMsg(1, robot_daemon_ls_req, {"path": '/userdata'}))
            data = so.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = so.recv(8192)
                    ret = json.loads(data)
                    
                    if 'files' in ret:
                        for arquivo in ret['files']:
                            nome = arquivo.get('name', '')
                            # Procura por arquivos que podem ter landmarks
                            if 'landmark' in nome.lower() or 'map' in nome.lower():
                                print(f"    📄 Encontrado: {nome}")
                                # Aqui poderíamos baixar o arquivo se necessário
            
            so.close()
            
            # Se não encontrou, adiciona landmarks básicos baseados na imagem
            if len(self.landmarks) == 0:
                print("  ℹ️  Usando landmarks padrão")
                self.landmarks = {
                    'LM1': (3.5, 5.5),    # Posição aproximada da imagem
                    'y_LM': (3.5, 1.5),   # Posição aproximada da imagem
                }
                self.desenhar_landmarks()
            
        except Exception as e:
            print(f"    ⚠️ Erro ao buscar landmarks: {e}")
            # Landmarks padrão
            if len(self.landmarks) == 0:
                self.landmarks = {
                    'LM1': (3.5, 5.5),
                    'y_LM': (3.5, 1.5),
                }
                self.desenhar_landmarks()
    
    def desenhar_landmarks(self):
        """Desenha landmarks no mapa"""
        for nome, (x, y) in self.landmarks.items():
            # Caixa laranja (estilo RoboShop Pro)
            largura = 0.8
            altura = 0.5
            rect = patches.Rectangle((x-largura/2, y-altura/2), largura, altura,
                                     fc='orange', ec='darkorange',
                                     alpha=0.7, zorder=7, linewidth=2)
            self.ax.add_patch(rect)
            
            # Ponto central
            self.ax.plot(x, y, 'ro', markersize=8, zorder=8)
            
            # Nome do landmark
            self.ax.text(x, y+0.5, nome, ha='center', fontsize=11, 
                       fontweight='bold', zorder=9,
                       bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='white', alpha=0.8))
        
        print(f"  ✅ {len(self.landmarks)} landmarks desenhados")
    
    def thread_reconexao_func(self):
        """Thread que tenta reconectar robôs desconectados"""
        while self.rodando:
            try:
                for robo in self.robos:
                    if not robo.conectado:
                        tempo_atual = time.time()
                        if tempo_atual - robo.ultima_tentativa_conexao >= INTERVALO_RECONEXAO:
                            robo.ultima_tentativa_conexao = tempo_atual
                            if robo.tentar_conectar():
                                # Se conseguiu conectar e não tem landmarks, busca
                                if len(self.landmarks) == 0:
                                    self.buscar_landmarks_do_robo(robo)
                
                time.sleep(1)
            except Exception as e:
                pass
    
    def atualizar_frame(self, frame):
        """Atualiza o frame da animação"""
        elementos_atualizados = []
        
        # Atualiza cada robô
        for robo in self.robos:
            if robo.conectado:
                robo.ler_dados()
                
                # Adiciona à trajetória
                robo.trajetoria_x.append(robo.pos_x)
                robo.trajetoria_y.append(robo.pos_y)
                
                # Atualiza trajetória
                if len(robo.trajetoria_x) > 0:
                    robo.trajetoria_line.set_data(list(robo.trajetoria_x), 
                                                 list(robo.trajetoria_y))
                
                # Remove patch antigo do robô
                if robo.robo_patch and robo.robo_patch in self.ax.patches:
                    robo.robo_patch.remove()
                
                # Cria novo patch do robô
                dx = TAMANHO_ROBO * np.cos(robo.angulo)
                dy = TAMANHO_ROBO * np.sin(robo.angulo)
                
                robo.robo_patch = patches.FancyArrow(
                    robo.pos_x, robo.pos_y, dx, dy,
                    width=TAMANHO_ROBO*0.8, 
                    head_width=TAMANHO_ROBO*1.2,
                    head_length=TAMANHO_ROBO*0.3,
                    fc=robo.cor_principal, 
                    ec=robo.cor_borda, 
                    linewidth=2, zorder=10
                )
                self.ax.add_patch(robo.robo_patch)
                
                # Remove patches de sensores anteriores
                for patch in robo.sensor_patches:
                    if patch in self.ax.patches:
                        patch.remove()
                robo.sensor_patches.clear()
                
                # Desenha áreas detectadas
                if len(robo.areas_detectadas) > 0:
                    for i, area_id in enumerate(robo.areas_detectadas):
                        angulo_area = robo.angulo + (i - len(robo.areas_detectadas)/2) * 0.3
                        dist = 1.5
                        sensor_x = robo.pos_x + dist * np.cos(angulo_area)
                        sensor_y = robo.pos_y + dist * np.sin(angulo_area)
                        
                        sensor_circle = patches.Circle(
                            (sensor_x, sensor_y), 0.3, 
                            fc='red', ec='darkred', alpha=0.5, zorder=5
                        )
                        self.ax.add_patch(sensor_circle)
                        robo.sensor_patches.append(sensor_circle)
                
                # Atualiza marcador de destino
                if robo.target_id and robo.target_id in self.landmarks:
                    target_x, target_y = self.landmarks[robo.target_id]
                    robo.target_marker.set_data([target_x], [target_y])
                else:
                    robo.target_marker.set_data([], [])
                
                # Label com nome do robô
                if robo.label_text:
                    robo.label_text.remove()
                robo.label_text = self.ax.text(
                    robo.pos_x, robo.pos_y - 0.8, robo.nome,
                    ha='center', fontsize=9, fontweight='bold',
                    color=robo.cor_borda,
                    bbox=dict(boxstyle='round,pad=0.3', 
                             facecolor='white', alpha=0.8),
                    zorder=11
                )
                
                elementos_atualizados.extend([
                    robo.robo_patch, robo.trajetoria_line, 
                    robo.target_marker, robo.label_text
                ] + robo.sensor_patches)
        
        # Atualiza painel de informações
        info_lines = []
        status_names = {1: 'Suspenso', 2: 'Executando', 3: 'Pausado', 
                       4: 'Completo', 5: 'Falhou'}
        
        for robo in self.robos:
            status = '🔴 OFFLINE' if not robo.conectado else '🟢 ONLINE'
            
            if robo.conectado:
                status_task = status_names.get(robo.task_status, 'N/A') if robo.task_status else 'N/A'
                linha = f"{robo.nome}: {status} | Pos:({robo.pos_x:.2f},{robo.pos_y:.2f}) "
                linha += f"Ang:{np.degrees(robo.angulo):.0f}° "
                linha += f"Vel:{robo.velocidade_linear:.2f}m/s "
                if robo.target_id:
                    linha += f"Dest:{robo.target_id} "
                linha += f"Status:{status_task}"
            else:
                linha = f"{robo.nome}: {status} | Tentando reconectar..."
            
            info_lines.append(linha)
        
        info_text = '\n'.join(info_lines) if info_lines else 'Nenhum robô adicionado'
        self.info_text.set_text(info_text)
        elementos_atualizados.append(self.info_text)
        
        return elementos_atualizados
    
    def iniciar(self):
        """Inicia a visualização"""
        print("\n🎬 Iniciando visualização...")
        
        # Inicia thread de reconexão
        self.thread_reconexao = threading.Thread(target=self.thread_reconexao_func, daemon=True)
        self.thread_reconexao.start()
        
        # Animação
        ani = FuncAnimation(self.fig, self.atualizar_frame, 
                          interval=INTERVALO_ATUALIZACAO, 
                          blit=True, cache_frame_data=False)
        
        plt.tight_layout()
        plt.show()
        
        # Cleanup
        self.rodando = False
        for robo in self.robos:
            robo.desconectar()
        
        print("\n👋 Visualização encerrada")

# ============ MAIN ============

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 VISUALIZADOR MULTI-ROBÔ - RoboShop Pro Edition")
    print("="*70)
    print("\n✨ RECURSOS:")
    print("  • Visualização de MÚLTIPLOS robôs simultaneamente")
    print("  • Funciona OFFLINE (mostra interface antes de conectar)")
    print("  • Reconexão automática a cada 5 segundos")
    print("  • Cada robô tem cor diferente")
    print("  • Landmarks e mapa compartilhados")
    print("\n📋 CONFIGURAÇÃO:")
    
    # Solicita IPs dos robôs
    robos_config = []
    
    print("\n  Digite os IPs dos robôs a monitorar (Enter vazio para finalizar):")
    
    contador = 1
    while True:
        try:
            ip = input(f"    Robô {contador} IP: ").strip()
            if not ip:
                break
            
            nome = input(f"    Robô {contador} Nome (Enter para padrão): ").strip()
            if not nome:
                nome = f"Robô_{contador}"
            
            robos_config.append((ip, nome))
            contador += 1
            
        except KeyboardInterrupt:
            break
    
    if len(robos_config) == 0:
        print("\n  ℹ️  Nenhum robô configurado. Usando IP padrão...")
        robos_config = [('10.101.251.137', 'Robô_1')]
    
    print(f"\n✅ {len(robos_config)} robô(s) configurado(s)")
    print("\n")
    
    try:
        visualizador = VisualizadorMultiRobo()
        
        # Adiciona robôs
        for ip, nome in robos_config:
            visualizador.adicionar_robo(ip, nome)
        
        print("\n📊 Iniciando monitoramento...")
        print("💡 A tela aparecerá imediatamente")
        print("🔄 Robôs offline serão conectados automaticamente")
        print("📌 Feche a janela para sair\n")
        
        visualizador.iniciar()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
