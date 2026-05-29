import asyncio
from asyncua import Client, ua
 
# Configure o endereço do seu servidor Kepware e o NodeID da tag
URL = "opc.tcp://192.168.1.1:4840" # Porta padrão do OPC UA no Kepware
# TAG_NODE_ID = "ns=1,s=OPC_LoraWan.GW_Innovation.boolBTN011"
 
async def main():
    client = Client(url=URL)
   
    # await client.connect()
 
    # ns_array = await client.get_namespace_array()
    # for i, uri in enumerate(ns_array):
    #     print(i, uri)
 
    # async def browse(node, depth=0):
    #     for child in await node.get_children():
    #         bn = await child.read_browse_name()
    #         print(" " * depth, child.nodeid, bn)
    #         if depth < 3:
    #             await browse(child, depth + 1)
    # await browse(client.nodes.objects)
    try:
        # Conecta ao servidor Kepware
 
        await client.connect()
        print("Conectado ao Kepware com sucesso!")
       
        while True:
        # 1. LENDO O VALOR DA TAG
            node = client.get_node("ns=1;s=boolBTN011")
            # node = client.get_node("1,OPC_LoraWan.GW_Innovation.BTN011")
            valor_atual = await node.read_value()
            print(f"Valor atual da tag: {valor_atual}")
       
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Desconecta do servidor
        await client.disconnect()
        print("Desconectado do servidor.")
 
if __name__ == "__main__":
    asyncio.run(main())