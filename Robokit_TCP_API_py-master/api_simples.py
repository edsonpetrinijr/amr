from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

@app.route('/')
def home():
    """Página inicial com instruções"""
    return """
    <h1>🤖 API Simple - Robô Monitor</h1>
    <p>Use: <code>/api?id=SEU_ID</code></p>
    <p>Exemplo: <code>/api?id=LM1</code></p>
    <hr>
    <p>Seu IP na rede: <strong>{}</strong></p>
    """.format(obter_ip_local())

@app.route('/api')
def receber_id():
    """Endpoint que recebe ID via query string"""
    # Pega o ID da query string
    id_recebido = request.args.get('id', None)
    
    if id_recebido:
        # Printa no console
        print(f"📥 ID RECEBIDO: {id_recebido}")
        
        # Retorna JSON
        return jsonify({
            "status": "sucesso",
            "id_recebido": id_recebido,
            "mensagem": f"ID '{id_recebido}' recebido e printado!"
        }), 200
    else:
        print("⚠️ Requisição sem ID")
        return jsonify({
            "status": "erro",
            "mensagem": "Parâmetro 'id' não fornecido. Use: /api?id=SEU_ID"
        }), 400

def obter_ip_local():
    """Descobre o IP local da máquina"""
    try:
        # Cria socket temporário para descobrir IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Não foi possível determinar"

if __name__ == '__main__':
    ip_local = obter_ip_local()
    porta = 4545
    
    print("\n" + "="*60)
    print("🚀 API SIMPLES INICIADA!")
    print("="*60)
    print(f"\n📡 Seu IP na rede local: {ip_local}")
    print(f"🌐 Porta: {porta}")
    print(f"\n✅ Qualquer pessoa na sua rede pode acessar:")
    print(f"   http://{ip_local}:{porta}/api?id=ALGUM_ID")
    print(f"\n📝 Exemplos:")
    print(f"   http://{ip_local}:{porta}/api?id=LM1")
    print(f"   http://{ip_local}:{porta}/api?id=robo_123")
    print(f"   http://{ip_local}:{porta}/api?id=teste")
    print(f"\n💡 Teste no navegador ou com curl:")
    print(f"   curl http://{ip_local}:{porta}/api?id=teste")
    print(f"\n🛑 Pressione Ctrl+C para parar\n")
    print("="*60 + "\n")
    
    # host='0.0.0.0' permite acesso de qualquer IP na rede
    app.run(host='0.0.0.0', port=porta, debug=True)
