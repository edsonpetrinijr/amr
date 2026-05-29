from asyncua import Client

async with Client(url='opc.tcp://10.101.252.107:4840') as client:
    while True:
        # Do something with client
        node = client.get_node('i=85')
        value = await node.read_value()