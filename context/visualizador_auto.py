from netprotocol.rbkNetProtoEnums import *
import netprotocol.rbkNetProtoEnums
import json
import socket
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import re
import os

# ============ CONFIGURAÇÕES ============
ROBOT_IP = '10.101.251.137'  # Ajuste para o IP do seu robô
MODO_OFFLINE = False  # True = funciona sem robô, apenas com arquivo .smap

# Configurações visuais
TAMANHO_ROBO = 0.5  # metros
COMPRIMENTO_TRAJETORIA = 500  # número de pontos da trajetória
INTERVALO_ATUALIZACAO = 100  # ms

# ============ CLASSE VISUALIZADOR ============

class VisualizadorRoboAuto:
    def __init__(self, modo_offline=MODO_OFFLINE):
        self.modo_offline = modo_offline
        
        if self.modo_offline:
            print("📴 Modo OFFLINE ativado - funcionando apenas com arquivo .smap")
        else:
            print("🔍 Buscando configurações do robô...")
        
        # Busca mapa e landmarks automaticamente
        self.landmarks = {}
        self.mapa_paredes = []
        self.mapa_limites = None
        self.pontos_navegaveis = []
        self.buscar_mapa_landmarks()
        
        # Inicializa figura
        titulo = '🤖 MAPA DO ROBOSHOP PRO - VISUALIZAÇÃO EM TEMPO REAL'
        if self.modo_offline:
            titulo = '📴 MAPA DO ROBOSHOP PRO - MODO OFFLINE (APENAS .SMAP)'
        
        self.fig, self.ax = plt.subplots(figsize=(14, 11))
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('X (metros)', fontsize=12)
        self.ax.set_ylabel('Y (metros)', fontsize=12)
        self.ax.set_title(titulo, fontsize=14, fontweight='bold')
        
        # Conexões com o robô
        self.so_state = None
        self.so_area = None
        self.conectado = False
        
        if not self.modo_offline:
            self.conectar()
        else:
            print("\n  ℹ️  Modo offline - Robô não será conectado")
            print("  ℹ️  Visualizando apenas o mapa do arquivo .smap\n")
        
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
        self.landmark_plots = []
        self.mapa_lines = []
        self.target_marker = None
        self.info_text = None
        
        self.inicializar_graficos()
    
    def carregar_arquivo_smap_local(self, caminho_arquivo):
        """Carrega arquivo .smap local"""
        try:
            print(f"  📂 Carregando arquivo local: {caminho_arquivo}")
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
                # Se o arquivo tem múltiplas linhas, pega apenas a primeira
                if '\n' in conteudo:
                    conteudo = conteudo.split('\n')[0]
                dados = json.loads(conteudo)
            
            # Extrai header
            if 'header' in dados:
                header = dados['header']
                map_name = header.get('mapName', 'Desconhecido')
                
                # Obtem minPos e maxPos com verificação segura
                min_pos = header.get('minPos', {})
                max_pos = header.get('maxPos', {})
                
                # Valores padrão
                min_x = min_pos.get('x') if isinstance(min_pos, dict) and 'x' in min_pos else -2
                max_x = max_pos.get('x') if isinstance(max_pos, dict) and 'x' in max_pos else 3
                min_y = min_pos.get('y') if isinstance(min_pos, dict) and 'y' in min_pos else -1
                max_y = max_pos.get('y') if isinstance(max_pos, dict) and 'y' in max_pos else 7
                
                print(f"  📍 Mapa: {map_name}")
                print(f"  📏 Limites: X({min_x:.2f} a {max_x:.2f}), Y({min_y:.2f} a {max_y:.2f})")
                
                # Guarda limites do mapa
                self.mapa_limites = {
                    'min_x': min_x,
                    'max_x': max_x,
                    'min_y': min_y,
                    'max_y': max_y
                }
            
            # Extrai landmarks (de advancedPointList)
            if 'advancedPointList' in dados:
                for lm in dados['advancedPointList']:
                    if 'instanceName' in lm and 'pos' in lm:
                        pos = lm['pos']
                        if isinstance(pos, dict) and 'x' in pos and 'y' in pos:
                            self.landmarks[lm['instanceName']] = (float(pos['x']), float(pos['y']))
                print(f"  ✅ Carregados {len(self.landmarks)} landmarks")
            
            # Extrai linhas do mapa (de normalLineList)
            if 'normalLineList' in dados:
                for linha in dados['normalLineList']:
                    if 'startPos' in linha and 'endPos' in linha:
                        start = linha['startPos']
                        end = linha['endPos']
                        if isinstance(start, dict) and isinstance(end, dict):
                            if 'x' in start and 'y' in start and 'x' in end and 'y' in end:
                                self.mapa_paredes.append([
                                    (float(start['x']), float(start['y'])),
                                    (float(end['x']), float(end['y']))
                                ])
                print(f"  ✅ Carregadas {len(self.mapa_paredes)} linhas do mapa")
            
            # Extrai pontos navegáveis (normalPosList) - opcional para visualização
            if 'normalPosList' in dados and len(dados['normalPosList']) > 0:
                for p in dados['normalPosList']:
                    if isinstance(p, dict) and 'x' in p and 'y' in p:
                        self.pontos_navegaveis.append((float(p['x']), float(p['y'])))
                print(f"  ✅ Carregados {len(self.pontos_navegaveis)} pontos navegáveis")
            
            # Extrai posição do robô (se disponível)
            if 'robotPos' in dados:
                robot_pos = dados['robotPos']
                if 'x' in robot_pos and 'y' in robot_pos:
                    self.pos_x = float(robot_pos['x'])
                    self.pos_y = float(robot_pos['y'])
                    if 'theta' in robot_pos:
                        self.angulo = float(robot_pos['theta'])
                    print(f"  🤖 Posição inicial do robô: X={self.pos_x:.2f}, Y={self.pos_y:.2f}, θ={self.angulo:.2f}")
            
            return True
            
        except FileNotFoundError:
            print(f"  ⚠️ Arquivo não encontrado: {caminho_arquivo}")
            return False
        except Exception as e:
            print(f"  ⚠️ Erro ao carregar arquivo .smap: {e}")
            return False
    
    def buscar_mapa_landmarks(self):
        """Busca automaticamente o mapa e landmarks do RoboShop Pro"""
        # Primeiro tenta carregar arquivo .smap local
        arquivos_locais = ['InnovationBox.smap', 'map.smap', 'mapa.smap']
        for arquivo in arquivos_locais:
            if os.path.exists(arquivo):
                if self.carregar_arquivo_smap_local(arquivo):
                    print(f"\n  ✅ Mapa carregado com sucesso do arquivo local!\n")
                    return
        
        # Se está em modo offline e não encontrou arquivo, avisa
        if self.modo_offline:
            print(f"\n  ⚠️ Nenhum arquivo .smap encontrado em modo offline!")
            print(f"  ℹ️  Arquivos procurados: {', '.join(arquivos_locais)}")
            print(f"  ℹ️  Usando configuração vazia\n")
            return
        
        # Se não encontrou arquivo local, tenta buscar do robô
        try:
            print("  🔌 Conectando ao robô para buscar mapa...")
            
            # Conecta ao daemon para listar arquivos
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.settimeout(5)
            so.connect((ROBOT_IP, API_PORT_ROBOD))
            
            # Busca arquivos na pasta /userdata (onde ficam os mapas)
            for pasta in ['/userdata', '/userdata/map', '/map', '/config']:
                try:
                    print(f"    📂 Buscando em {pasta}...")
                    so.send(packMsg(1, robot_daemon_ls_req, {"path": pasta}))
                    data = so.recv(16)
                    
                    if len(data) >= 16:
                        jsonDataLen = unpackHead(data)[0]
                        if jsonDataLen > 0:
                            data = so.recv(8192)
                            ret = json.loads(data)
                            
                            if 'files' in ret:
                                print(f"      ✅ Encontrados {len(ret['files'])} arquivos")
                                
                                # Busca arquivos de mapa (.map, .dat, .json)
                                for arquivo in ret['files']:
                                    nome = arquivo.get('name', '')
                                    if any(ext in nome.lower() for ext in ['.map', '.dat', '.json', 'landmark']):
                                        print(f"        📄 {nome}")
                                        self.tentar_carregar_arquivo(so, pasta, nome)
                    
                    time.sleep(0.2)
                except Exception as e:
                    pass
            
            so.close()
            
            # Se não encontrou landmarks, tenta buscar pela API de status
            if len(self.landmarks) == 0:
                print("  🔍 Tentando buscar landmarks pela API de localização...")
                self.buscar_landmarks_pela_api()
            
            print(f"\n  ✅ Carregados {len(self.landmarks)} landmarks")
            print(f"  ✅ Carregadas {len(self.mapa_paredes)} linhas do mapa\n")
            
        except Exception as e:
            print(f"  ⚠️ Não foi possível buscar mapa automaticamente: {e}")
            print("  ℹ️  Usando configuração manual básica\n")
            # Configuração padrão baseada na imagem
            self.landmarks = {
                'LM1': (0, 3),
                'y_LM': (0, 0),
            }
    
    def tentar_carregar_arquivo(self, so, pasta, nome):
        """Tenta baixar e carregar um arquivo de mapa/landmarks"""
        try:
            # Solicita download do arquivo
            so.send(packMsg(2, robot_daemon_scp_req, {
                "path": pasta, 
                "filename": nome
            }))
            data = so.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    # Recebe conteúdo do arquivo
                    conteudo = b''
                    while len(conteudo) < jsonDataLen:
                        chunk = so.recv(min(8192, jsonDataLen - len(conteudo)))
                        if not chunk:
                            break
                        conteudo += chunk
                    
                    # Tenta parsear como JSON
                    try:
                        dados = json.loads(conteudo)
                        self.extrair_landmarks_do_json(dados, nome)
                        self.extrair_mapa_do_json(dados, nome)
                    except:
                        # Tenta parsear como texto
                        try:
                            texto = conteudo.decode('utf-8')
                            self.extrair_landmarks_do_texto(texto, nome)
                        except:
                            pass
        except Exception as e:
            pass
    
    def extrair_landmarks_do_json(self, dados, nome_arquivo):
        """Extrai landmarks de um arquivo JSON"""
        # Procura por landmarks no JSON
        if isinstance(dados, dict):
            # Formato: {"landmarks": [{"id": "LM1", "x": 0, "y": 0}, ...]}
            if 'landmarks' in dados:
                for lm in dados['landmarks']:
                    if 'id' in lm and 'x' in lm and 'y' in lm:
                        self.landmarks[lm['id']] = (float(lm['x']), float(lm['y']))
            
            # Formato: {"LM1": {"x": 0, "y": 0}, ...}
            for key, value in dados.items():
                if isinstance(value, dict) and 'x' in value and 'y' in value:
                    if key.startswith('LM') or 'landmark' in key.lower():
                        self.landmarks[key] = (float(value['x']), float(value['y']))
    
    def extrair_mapa_do_json(self, dados, nome_arquivo):
        """Extrai paredes/obstáculos de um arquivo JSON"""
        if isinstance(dados, dict):
            # Procura por linhas/paredes
            if 'walls' in dados or 'lines' in dados or 'obstacles' in dados:
                chave = 'walls' if 'walls' in dados else ('lines' if 'lines' in dados else 'obstacles')
                for linha in dados[chave]:
                    if isinstance(linha, dict):
                        # Formato: {"x1": 0, "y1": 0, "x2": 1, "y2": 1}
                        if all(k in linha for k in ['x1', 'y1', 'x2', 'y2']):
                            self.mapa_paredes.append([
                                (float(linha['x1']), float(linha['y1'])),
                                (float(linha['x2']), float(linha['y2']))
                            ])
                    elif isinstance(linha, (list, tuple)) and len(linha) >= 4:
                        # Formato: [x1, y1, x2, y2]
                        self.mapa_paredes.append([
                            (float(linha[0]), float(linha[1])),
                            (float(linha[2]), float(linha[3]))
                        ])
    
    def extrair_landmarks_do_texto(self, texto, nome_arquivo):
        """Extrai landmarks de um arquivo de texto"""
        # Procura por padrões como: LM1 0.0 3.0 ou LM1: (0.0, 3.0)
        padroes = [
            r'(LM\d+|[a-zA-Z_]+LM)\s+([-\d.]+)\s+([-\d.]+)',
            r'(LM\d+|[a-zA-Z_]+LM)[:\s]+\(?([-\d.]+)[,\s]+([-\d.]+)\)?',
        ]
        
        for padrao in padroes:
            matches = re.findall(padrao, texto)
            for match in matches:
                nome, x, y = match
                self.landmarks[nome.strip()] = (float(x), float(y))
    
    def buscar_landmarks_pela_api(self):
        """Tenta descobrir landmarks observando navegações anteriores"""
        try:
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.settimeout(2)
            so.connect((ROBOT_IP, API_PORT_STATE))
            
            # Busca informações de task atual
            so.send(packMsg(1, robot_status_task_req, {}))
            data = so.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = so.recv(1024)
                    ret = json.loads(data)
                    
                    # Se tem um target_id, adiciona como landmark temporário
                    if 'target_id' in ret and ret['target_id']:
                        target = ret['target_id']
                        if target not in self.landmarks:
                            # Posição será descoberta quando o robô chegar lá
                            print(f"      📍 Landmark detectado: {target}")
            
            so.close()
        except:
            pass
    
    def conectar(self):
        """Conecta ao robô"""
        try:
            print("🔌 Conectando ao robô...")
            
            # Conexão para localização e estado
            self.so_state = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.so_state.connect((ROBOT_IP, API_PORT_STATE))
            self.so_state.settimeout(1.0)
            print(f"  ✅ Conectado à porta STATE ({API_PORT_STATE})")
            
            # Conexão para áreas/sensores (reutiliza STATE)
            self.so_area = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.so_area.connect((ROBOT_IP, API_PORT_STATE))
            self.so_area.settimeout(1.0)
            
            print("✅ Conexões estabelecidas!\n")
            self.conectado = True
            
        except Exception as e:
            print(f"⚠️ Não foi possível conectar ao robô: {e}")
            print(f"  ℹ️  Continuando em modo offline (apenas visualização do mapa)\n")
            self.conectado = False
            self.modo_offline = True
    
    def inicializar_graficos(self):
        """Inicializa os elementos gráficos"""
        # Desenha pontos navegáveis (fundo - opcional)
        if len(self.pontos_navegaveis) > 0:
            # Desenha como pontos muito pequenos para dar contexto do espaço navegável
            xs = [p[0] for p in self.pontos_navegaveis]
            ys = [p[1] for p in self.pontos_navegaveis]
            self.ax.scatter(xs, ys, c='lightgray', s=0.5, alpha=0.3, zorder=1)
            print(f"  ℹ️  Desenhados {len(self.pontos_navegaveis)} pontos navegáveis (fundo)")
        
        # Desenha mapa (paredes)
        for parede in self.mapa_paredes:
            x_coords = [parede[0][0], parede[1][0]]
            y_coords = [parede[0][1], parede[1][1]]
            line, = self.ax.plot(x_coords, y_coords, 'purple', 
                                linestyle='--', linewidth=2, alpha=0.7)
            self.mapa_lines.append(line)
        
        # Robô (triângulo apontando para frente)
        self.robo_patch = patches.FancyArrow(0, 0, TAMANHO_ROBO, 0, 
                                             width=TAMANHO_ROBO*0.8, 
                                             head_width=TAMANHO_ROBO*1.2,
                                             head_length=TAMANHO_ROBO*0.3,
                                             fc='blue', ec='darkblue', 
                                             linewidth=2, zorder=10)
        self.ax.add_patch(self.robo_patch)
        
        # Trajetória
        self.trajetoria_line, = self.ax.plot([], [], 'g-', alpha=0.5, 
                                             linewidth=2, label='Trajetória')
        
        # Landmarks
        if len(self.landmarks) > 0:
            for nome, (x, y) in self.landmarks.items():
                plot = self.ax.plot(x, y, 'ro', markersize=12, zorder=8)[0]
                # Caixa ao redor do landmark (estilo RoboShop Pro)
                rect = patches.Rectangle((x-0.3, y-0.2), 0.6, 0.4,
                                         fc='orange', ec='darkorange',
                                         alpha=0.6, zorder=7)
                self.ax.add_patch(rect)
                self.ax.text(x, y+0.4, nome, ha='center', fontsize=10, 
                           fontweight='bold', zorder=9)
                self.landmark_plots.append(plot)
        
        # Marcador de destino (quando está navegando)
        self.target_marker, = self.ax.plot([], [], 'r*', markersize=20, 
                                          label='Destino', zorder=9)
        
        # Origem (0, 0)
        self.ax.plot(0, 0, 'ro', markersize=8, zorder=9)
        self.ax.text(0.1, -0.3, '0,0', fontsize=9, fontweight='bold')
        
        # Eixos de referência
        self.ax.arrow(0, 0, 1, 0, head_width=0.15, head_length=0.2, 
                     fc='red', ec='red', alpha=0.5, zorder=5)
        self.ax.text(1.2, 0, 'x', fontsize=12, fontweight='bold', color='red')
        self.ax.arrow(0, 0, 0, 1, head_width=0.15, head_length=0.2, 
                     fc='green', ec='green', alpha=0.5, zorder=5)
        self.ax.text(0, 1.2, 'y', fontsize=12, fontweight='bold', color='green')
        
        # Texto de informações
        self.info_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Legenda
        self.ax.legend(loc='upper right')
        
        # Ajusta limites iniciais
        if self.mapa_limites:
            # Usa limites do arquivo .smap
            margin = 0.5
            self.ax.set_xlim(self.mapa_limites['min_x'] - margin, self.mapa_limites['max_x'] + margin)
            self.ax.set_ylim(self.mapa_limites['min_y'] - margin, self.mapa_limites['max_y'] + margin)
        elif len(self.landmarks) > 0:
            xs = [x for x, y in self.landmarks.values()]
            ys = [y for x, y in self.landmarks.values()]
            margin = 3
            self.ax.set_xlim(min(xs) - margin, max(xs) + margin)
            self.ax.set_ylim(min(ys) - margin, max(ys) + margin)
        else:
            self.ax.set_xlim(-5, 15)
            self.ax.set_ylim(-5, 15)
    
    def ler_posicao(self):
        """Lê a posição atual do robô"""
        try:
            self.so_state.send(packMsg(1, robot_status_loc_req, {}))
            data = self.so_state.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    
                    # Atualiza posição
                    self.pos_x = ret.get('x', self.pos_x)
                    self.pos_y = ret.get('y', self.pos_y)
                    self.angulo = ret.get('angle', self.angulo)
                    
                    return True
        except socket.timeout:
            pass
        except Exception as e:
            pass
        
        return False
    
    def ler_task_status(self):
        """Lê o status da task atual"""
        try:
            self.so_state.send(packMsg(2, robot_status_task_req, {}))
            data = self.so_state.recv(16)
            
            if len(data) >= 16:
                jsonDataLen = unpackHead(data)[0]
                if jsonDataLen > 0:
                    data = self.so_state.recv(2048)
                    ret = json.loads(data)
                    
                    self.target_id = ret.get('target_id', None)
                    self.task_status = ret.get('task_status', None)
                    
                    # Se chegou em um landmark desconhecido, registra posição
                    if self.target_id and self.target_id not in self.landmarks:
                        if self.task_status == 4:  # COMPLETED
                            self.landmarks[self.target_id] = (self.pos_x, self.pos_y)
                            print(f"  📍 Novo landmark descoberto: {self.target_id} em ({self.pos_x:.2f}, {self.pos_y:.2f})")
                    
                    return True
        except socket.timeout:
            pass
        except Exception as e:
            pass
        
        return False
    
    def ler_velocidade(self):
        """Lê a velocidade atual do robô"""
        try:
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
                    
                    return True
        except socket.timeout:
            pass
        except Exception as e:
            pass
        
        return False
    
    def ler_areas(self):
        """Lê as áreas detectadas pelos sensores"""
        try:
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
            pass
        except Exception as e:
            pass
        
        return False
    
    def atualizar_frame(self, frame):
        """Atualiza o frame da animação"""
        # Lê dados do robô (apenas se conectado)
        if self.conectado and self.so_state:
            self.ler_posicao()
            self.ler_task_status()
            self.ler_velocidade()
            self.ler_areas()
            
            # Adiciona posição à trajetória
            self.trajetoria_x.append(self.pos_x)
            self.trajetoria_y.append(self.pos_y)
            
            # Atualiza trajetória
            if len(self.trajetoria_x) > 0:
                self.trajetoria_line.set_data(list(self.trajetoria_x), list(self.trajetoria_y))
            
            # Atualiza posição do robô
            if self.robo_patch in self.ax.patches:
                self.robo_patch.remove()
            
            dx = TAMANHO_ROBO * np.cos(self.angulo)
            dy = TAMANHO_ROBO * np.sin(self.angulo)
            
            self.robo_patch = patches.FancyArrow(
                self.pos_x, self.pos_y, dx, dy,
                width=TAMANHO_ROBO*0.8, 
                head_width=TAMANHO_ROBO*1.2,
                head_length=TAMANHO_ROBO*0.3,
                fc='blue', ec='darkblue', 
                linewidth=2, zorder=10
            )
            self.ax.add_patch(self.robo_patch)
            
            # Remove patches de sensores anteriores
            for patch in self.sensor_patches:
                if patch in self.ax.patches:
                    patch.remove()
            self.sensor_patches.clear()
            
            # Desenha áreas detectadas
            if len(self.areas_detectadas) > 0:
                for i, area_id in enumerate(self.areas_detectadas):
                    angulo_area = self.angulo + (i - len(self.areas_detectadas)/2) * 0.3
                    dist = 1.5
                    sensor_x = self.pos_x + dist * np.cos(angulo_area)
                    sensor_y = self.pos_y + dist * np.sin(angulo_area)
                    
                    sensor_circle = patches.Circle(
                        (sensor_x, sensor_y), 0.3, 
                        fc='red', ec='darkred', alpha=0.5, zorder=5
                    )
                    self.ax.add_patch(sensor_circle)
                    self.sensor_patches.append(sensor_circle)
            
            # Atualiza marcador de destino
            if self.target_id and self.target_id in self.landmarks:
                target_x, target_y = self.landmarks[self.target_id]
                self.target_marker.set_data([target_x], [target_y])
            else:
                self.target_marker.set_data([], [])
            
            # Atualiza texto de informações
            status_names = {1: 'Suspenso', 2: 'Executando', 3: 'Pausado', 4: 'Completo', 5: 'Falhou'}
            status_text = status_names.get(self.task_status, 'Desconhecido') if self.task_status else 'N/A'
            
            info = f'📍 Posição: ({self.pos_x:.2f}, {self.pos_y:.2f})\n'
            info += f'🧭 Ângulo: {np.degrees(self.angulo):.1f}°\n'
            info += f'⚡ Vel. Linear: {self.velocidade_linear:.2f} m/s\n'
            info += f'🔄 Vel. Angular: {self.velocidade_angular:.2f} rad/s\n'
            
            if self.target_id:
                info += f'🎯 Destino: {self.target_id}\n'
                info += f'📊 Status: {status_text}\n'
            
            info += f'📡 Áreas: {len(self.areas_detectadas)}'
            if len(self.areas_detectadas) > 0:
                info += f' {self.areas_detectadas}'
        else:
            # Modo offline - apenas mostra o mapa estático
            info = f'📴 MODO OFFLINE - APENAS VISUALIZAÇÃO DO MAPA\n\n'
            info += f'📊 Estatísticas do mapa:\n'
            info += f'  • Pontos navegáveis: {len(self.pontos_navegaveis)}\n'
            info += f'  • Paredes/linhas: {len(self.mapa_paredes)}\n'
            info += f'  • Landmarks: {len(self.landmarks)}\n'
            
            if self.mapa_limites:
                info += f'\n📏 Limites do mapa:\n'
                info += f'  X: [{self.mapa_limites["min_x"]:.2f}, {self.mapa_limites["max_x"]:.2f}]\n'
                info += f'  Y: [{self.mapa_limites["min_y"]:.2f}, {self.mapa_limites["max_y"]:.2f}]'
        
        self.info_text.set_text(info)
        
        return [self.robo_patch, self.trajetoria_line, self.info_text, 
                self.target_marker] + self.sensor_patches
    
    def iniciar(self):
        """Inicia a visualização"""
        if self.modo_offline:
            print("\n🎬 Iniciando visualização em MODO OFFLINE...")
            print("📌 Visualizando apenas o mapa do arquivo .smap")
            print("📌 Feche a janela para sair\n")
        else:
            print("\n🎬 Iniciando visualização...")
            print("📌 Feche a janela para sair\n")
        
        if self.conectado or self.modo_offline:
            ani = FuncAnimation(self.fig, self.atualizar_frame, 
                              interval=INTERVALO_ATUALIZACAO, 
                              blit=True, cache_frame_data=False)
            
            plt.tight_layout()
            plt.show()
        else:
            print("\n⚠️ Não foi possível conectar ao robô e nenhum arquivo .smap foi encontrado")
            print("  Para modo offline, certifique-se de ter um arquivo .smap no diretório")
            return
        
        # Fecha conexões ao sair
        if self.so_state:
            self.so_state.close()
        if self.so_area:
            self.so_area.close()
        
        print("\n👋 Visualização encerrada")

# ============ MAIN ============

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🤖 VISUALIZADOR AUTOMÁTICO DO ROBOSHOP PRO")
    print("="*60)
    
    # Verifica argumentos de linha de comando
    modo_offline = '--offline' in sys.argv or '-o' in sys.argv
    
    if modo_offline:
        print("\n📴 MODO OFFLINE ATIVADO")
        print("\n✨ Mostrando apenas o mapa do arquivo .smap")
        print("  • Não conecta ao robô")
        print("  • Carrega mapa de: InnovationBox.smap, map.smap ou mapa.smap")
    else:
        print("\n✨ Este programa busca AUTOMATICAMENTE:")
        print("  • Mapa do ambiente (paredes e obstáculos)")
        print("  • Landmarks configurados no RoboShop Pro")
        print("  • Descobre novos landmarks durante navegação")
        print("\n📊 E mostra em tempo real:")
        print("  • Posição e orientação do robô")
        print("  • Trajetória percorrida")
        print("  • Destino atual e status da navegação")
        print("  • Áreas detectadas pelos sensores")
        print("\n💡 Dica: Use 'python visualizador_auto.py --offline' para modo offline")
    
    print("\n")
    
    try:
        visualizador = VisualizadorRoboAuto(modo_offline=modo_offline)
        visualizador.iniciar()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
