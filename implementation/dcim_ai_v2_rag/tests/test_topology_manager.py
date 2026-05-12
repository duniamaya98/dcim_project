from dcim_ai.root_cause.topology_manager import CausalTopologyManager


def test_topology_load():

    topo = CausalTopologyManager()
    graph = topo.get_full_graph()

    assert isinstance(graph, dict)
    assert "compute" in graph