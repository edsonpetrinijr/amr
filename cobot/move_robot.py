"""Movimento simples do cobot Fairino.

Obs: o SDK baixado e' a versao nova que exige a porta CNDE 20005, mas o firmware
deste robo so abre as portas classicas (20003 XML-RPC + 20004 status). Como os
comandos de movimento usam o XML-RPC (20003), que funciona, forcamos is_connect
= True para liberar o envio dos comandos.
"""
from fairino import Robot

# Conecta ao robo (ja conectado em 192.168.58.2)
robot = Robot.RPC('192.168.58.2')

# Bypass do gate de conexao CNDE (20005), que este firmware nao expoe.
# O XML-RPC (20003), usado pelos comandos de movimento, esta funcionando.
Robot.RPC.is_connect = True

# Habilita o robo
ret = robot.RobotEnable(1)
print("RobotEnable ->", ret)

# Posicao em juntas (graus): [j1, j2, j3, j4, j5, j6]
pose_a = [0.0, -20.0, -90.0, -70.0, 90.0, 0.0]
pose_b = [20.0, -20.0, -90.0, -70.0, 90.0, 0.0]

# Move para a posicao A e depois para a B
# vel = velocidade em % (0-100)
ret = robot.MoveJ(pose_a, tool=0, user=0, vel=20)
print("MoveJ A ->", ret)
ret = robot.MoveJ(pose_b, tool=0, user=0, vel=20)
print("MoveJ B ->", ret)

print("Movimento concluido. (0 = sucesso; negativo = erro)")
