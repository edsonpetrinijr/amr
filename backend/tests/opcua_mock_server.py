"""
Local mock OPC UA server for testing the callbutton driver end-to-end.

Exposes the same node namespace/structure the driver subscribes to: a set of
boolean call-button nodes addressed by their exact OPC UA node-id strings (e.g.
``ns=2;s=CallButton.CB1``). A test can flip any node True/False to simulate a
physical button press.

Built on asyncua's Server API (same library pinned in requirements.txt), so the
client driver talks real OPC UA over TCP to a real (in-process) server.

Usage (async):
    srv = MockOpcUaServer("opc.tcp://127.0.0.1:48400/fleet",
                          {"ns=2;s=CallButton.CB1": False})
    await srv.start()
    await srv.set("ns=2;s=CallButton.CB1", True)   # rising edge → press
    await srv.stop()
"""
from __future__ import annotations

from asyncua import Server, ua


class MockOpcUaServer:
    def __init__(self, endpoint: str, nodes: dict[str, bool]) -> None:
        """
        endpoint : opc.tcp URL to bind, e.g. "opc.tcp://127.0.0.1:48400/fleet".
        nodes    : {node_id_str: initial_bool}. node_id_str is a full OPC UA
                   node id like "ns=2;s=CallButton.CB1".
        """
        self.endpoint = endpoint
        self._spec = dict(nodes)
        self._server: Server | None = None
        self._vars: dict[str, object] = {}

    async def start(self) -> None:
        server = Server()
        await server.init()
        server.set_endpoint(self.endpoint)
        server.set_server_name("Fleet Mock OPC UA")

        parsed = {nid: ua.NodeId.from_string(nid) for nid in self._spec}

        # Make sure every namespace index referenced by a node id actually exists
        # in the server's namespace array (index 0 and 1 are pre-populated).
        max_idx = max((p.NamespaceIndex for p in parsed.values()), default=1)
        ns_array = await server.get_namespace_array()
        while len(ns_array) <= max_idx:
            await server.register_namespace(f"urn:fleet:mock:{len(ns_array)}")
            ns_array = await server.get_namespace_array()

        objects = server.nodes.objects
        for nid, init in self._spec.items():
            node_id = parsed[nid]
            bname = f"{node_id.NamespaceIndex}:{node_id.Identifier}"
            var = await objects.add_variable(node_id, bname, bool(init),
                                             varianttype=ua.VariantType.Boolean)
            await var.set_writable()
            self._vars[nid] = var

        await server.start()
        self._server = server

    async def set(self, node_id: str, value: bool) -> None:
        """Flip a button node — drives a datachange notification to subscribers."""
        await self._vars[node_id].write_value(
            ua.DataValue(ua.Variant(bool(value), ua.VariantType.Boolean))
        )

    async def stop(self) -> None:
        if self._server is not None:
            try:
                await self._server.stop()
            finally:
                self._server = None
                self._vars.clear()
