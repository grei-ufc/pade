"""Simplified three-phase backward/forward sweep for radial distribution grids."""

from __future__ import annotations

import numpy as np

from mygrid.grid import DistributionGrid


def _phase_currents(power: np.ndarray, voltage: np.ndarray) -> np.ndarray:
    safe_voltage = np.where(np.abs(voltage) < 1e-6, 1.0 + 0.0j, voltage)
    return np.conj(power / safe_voltage)


def calc_power_flow(
    grid: DistributionGrid,
    max_iterations: int = 15,
    tolerance: float = 1e-3,
) -> DistributionGrid:
    """Run a radial backward/forward sweep and update each node voltage."""

    nodes = grid.nodes
    root = grid.root

    voltages = {
        name: node.vp.reshape(3,) if node.vp.size else node.nominal_voltage_vector()
        for name, node in nodes.items()
    }
    voltages[root.name] = root.nominal_voltage_vector()

    for _ in range(max_iterations):
        branch_currents = {}
        node_currents = {}

        for node_name in reversed(grid.bfs_order):
            node = nodes[node_name]
            own_current = _phase_currents(node.net_power, voltages[node_name])
            child_current = np.zeros(3, dtype=complex)
            for section in grid.children.get(node_name, []):
                child_current += branch_currents[section.n2.name]
            total_current = own_current + child_current
            node_currents[node_name] = total_current
            branch_currents[node_name] = total_current

        max_delta = 0.0
        next_voltages = dict(voltages)
        next_voltages[root.name] = root.nominal_voltage_vector()

        for node_name in grid.bfs_order:
            parent_voltage = next_voltages[node_name]
            for section in grid.children.get(node_name, []):
                child_name = section.n2.name
                current = branch_currents[child_name]
                child_voltage = section.transfer_voltage(parent_voltage, current)
                next_voltages[child_name] = child_voltage
                delta = np.max(np.abs(child_voltage - voltages[child_name]))
                max_delta = max(max_delta, float(delta))

        voltages = next_voltages
        if max_delta < tolerance:
            break

    for node_name, node in nodes.items():
        node.vp = voltages[node_name].reshape(3, 1)

    return grid
