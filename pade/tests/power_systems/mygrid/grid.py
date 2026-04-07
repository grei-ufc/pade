"""Minimal grid models used by the local IEEE-13 power-flow example."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import numpy as np


PHASE_ANGLES = np.deg2rad([0.0, -120.0, 120.0])
PHASE_ROTATION = np.exp(1j * PHASE_ANGLES)


def _safe_complex_vector(values: Iterable[complex]) -> np.ndarray:
    return np.asarray(list(values), dtype=complex).reshape(3,)


@dataclass
class Switch:
    name: str
    state: int = 1

    @property
    def is_closed(self) -> bool:
        return bool(self.state)


@dataclass
class Conductor:
    id: Optional[int] = None
    resistance_ohm_per_mile: Optional[float] = None
    reactance_ohm_per_mile: Optional[float] = None

    _IMPEDANCE_BY_ID = {
        75: 0.22 + 0.39j,
        44: 0.31 + 0.45j,
        31: 0.46 + 0.63j,
        32: 0.51 + 0.71j,
    }

    @property
    def impedance_per_mile(self) -> complex:
        if self.resistance_ohm_per_mile is not None and self.reactance_ohm_per_mile is not None:
            return complex(self.resistance_ohm_per_mile, self.reactance_ohm_per_mile)
        return self._IMPEDANCE_BY_ID.get(self.id, 0.35 + 0.55j)


@dataclass
class Under_Ground_Conductor(Conductor):
    outsider_diameter: Optional[float] = None
    rp: Optional[float] = None
    GMRp: Optional[float] = None
    dp: Optional[float] = None
    k: Optional[float] = None
    rs: Optional[float] = None
    GMRs: Optional[float] = None
    ds: Optional[float] = None
    ampacity: Optional[float] = None
    type: Optional[str] = None
    T: Optional[float] = None

    @property
    def impedance_per_mile(self) -> complex:
        if self.rp is None:
            return 0.28 + 0.30j
        reactance = 0.30 + 0.015 * (self.k or 0.0)
        return complex(float(self.rp), reactance)


@dataclass
class LineModel:
    loc: List[complex]
    phasing: List[str]
    conductor: Conductor
    neutral_conductor: Optional[Conductor] = None

    def impedance_vector(self, length_miles: float) -> np.ndarray:
        base = self.conductor.impedance_per_mile * max(length_miles, 0.0)
        present_phases = {phase for phase in self.phasing if phase in {"a", "b", "c"}}
        scale = 1.0 + max(0, 3 - len(present_phases)) * 0.08
        return np.array(
            [
                base * (scale if "a" in present_phases or not present_phases else 0.95),
                base * (scale if "b" in present_phases or not present_phases else 1.00),
                base * (scale if "c" in present_phases or not present_phases else 1.05),
            ],
            dtype=complex,
        )


@dataclass
class UnderGroundLine(LineModel):
    def impedance_vector(self, length_miles: float) -> np.ndarray:
        base = self.conductor.impedance_per_mile * max(length_miles, 0.0)
        return np.array([base * 0.92, base * 0.97, base * 1.02], dtype=complex)


@dataclass
class Shunt_Capacitor:
    vll: complex
    Qa: float = 0.0
    Qb: float = 0.0
    Qc: float = 0.0
    type_connection: str = "wye"

    @property
    def reactive_compensation(self) -> np.ndarray:
        return np.array([1j * self.Qa, 1j * self.Qb, 1j * self.Qc], dtype=complex)


@dataclass
class ExternalGrid:
    name: str
    vll: complex
    Z: np.ndarray = field(default_factory=lambda: np.zeros((3, 3), dtype=complex))


@dataclass
class Generation:
    name: str = "generation"


@dataclass
class Substation:
    name: str = "substation"


@dataclass
class Sector:
    name: str = "sector"


@dataclass
class TransformerModel:
    name: str
    primary_voltage: complex
    secondary_voltage: complex
    power: float = 0.0
    connection: str = "Dyn"
    R: float = 0.0
    X: float = 0.0

    def __post_init__(self) -> None:
        ratio = self.effective_ratio
        self.A = np.eye(3, dtype=complex) * ratio
        self.d = np.eye(3, dtype=complex) * ratio
        self.z = np.eye(3, dtype=complex) * self.series_impedance

    @property
    def effective_ratio(self) -> float:
        primary = abs(self.primary_voltage) or 1.0
        secondary = abs(self.secondary_voltage) or primary
        return secondary / primary

    @property
    def series_impedance(self) -> complex:
        base_voltage = abs(self.secondary_voltage) or 1.0
        base_power = self.power or 1.0
        z_base = (base_voltage ** 2) / base_power
        return z_base * complex(self.R, self.X) / 100.0

    def impedance_vector(self) -> np.ndarray:
        z = self.series_impedance
        return np.array([z, z, z], dtype=complex)


@dataclass
class Auto_TransformerModel(TransformerModel):
    step: float = 0.0
    tap_max: int = 32
    vhold: float = 122.0
    voltage: float = 4160.0
    CTP: float = 700.0
    Npt: float = 20.0
    Z: complex = 0.0 + 0.0j

    def __init__(
        self,
        name: str,
        step: float,
        tap_max: int,
        vhold: float,
        voltage: float,
        R: float,
        X: float,
        CTP: float,
        Npt: float,
        Z: complex,
    ) -> None:
        self.step = step
        self.tap_max = tap_max
        self.vhold = vhold
        self.voltage = voltage
        self.CTP = CTP
        self.Npt = Npt
        self.Z = Z
        super().__init__(
            name=name,
            primary_voltage=voltage,
            secondary_voltage=voltage,
            power=max(voltage * 1e3, 1.0),
            connection="auto",
            R=R,
            X=X,
        )

    @property
    def effective_ratio(self) -> float:
        return 1.0 + (self.step / 100.0)


@dataclass
class LoadNode:
    name: str
    ppa: complex = 0.0 + 0.0j
    ppb: complex = 0.0 + 0.0j
    ppc: complex = 0.0 + 0.0j
    type_connection: str = "wye"
    zipmodel: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0])
    external_grid: Optional[ExternalGrid] = None
    voltage: complex = 4160.0 + 0.0j
    shunt_capacitor: Optional[Shunt_Capacitor] = None
    vp: np.ndarray = field(default_factory=lambda: np.zeros((3, 1), dtype=complex))

    def __post_init__(self) -> None:
        self.vp = self.nominal_voltage_vector().reshape(3, 1)

    def nominal_voltage_vector(self) -> np.ndarray:
        line_to_line = abs(self.voltage) or 1.0
        line_to_neutral = line_to_line / np.sqrt(3.0)
        phase_shift = np.exp(1j * np.angle(self.voltage))
        return line_to_neutral * PHASE_ROTATION * phase_shift

    @property
    def pp(self) -> np.ndarray:
        return np.array([[self.ppa], [self.ppb], [self.ppc]], dtype=complex)

    @pp.setter
    def pp(self, value: np.ndarray) -> None:
        vector = np.asarray(value, dtype=complex).reshape(3,)
        self.ppa, self.ppb, self.ppc = vector.tolist()

    @property
    def net_power(self) -> np.ndarray:
        power = np.array([self.ppa, self.ppb, self.ppc], dtype=complex)
        if self.shunt_capacitor is not None:
            power = power - self.shunt_capacitor.reactive_compensation
        return power


@dataclass
class Section:
    name: str
    n1: LoadNode
    n2: LoadNode
    line_model: Optional[LineModel] = None
    transformer: Optional[TransformerModel] = None
    switch: Optional[Switch] = None
    length: float = 0.0

    @property
    def is_closed(self) -> bool:
        return self.switch is None or self.switch.is_closed

    def voltage_drop(self, current: np.ndarray) -> np.ndarray:
        if self.transformer is not None:
            return self.transformer.impedance_vector() * current
        if self.line_model is not None:
            return self.line_model.impedance_vector(self.length) * current
        return np.zeros(3, dtype=complex)

    def transfer_voltage(self, parent_voltage: np.ndarray, current: np.ndarray) -> np.ndarray:
        voltage = parent_voltage.copy()
        if self.transformer is not None:
            voltage = voltage * self.transformer.effective_ratio
        return voltage - self.voltage_drop(current)


@dataclass
class DistributionGrid:
    name: str
    nodes: Dict[str, LoadNode]
    sections: List[Section]
    root: LoadNode
    children: Dict[str, List[Section]]
    parent_section: Dict[str, Section]
    bfs_order: List[str]


class GridElements:
    """Container that mirrors the subset of the legacy mygrid API used here."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.switches: List[Switch] = []
        self.load_nodes: List[LoadNode] = []
        self.sections: List[Section] = []
        self.dist_grids: Dict[str, DistributionGrid] = {}

    def add_switch(self, switches: Iterable[Switch]) -> None:
        self.switches.extend(list(switches))

    def add_load_node(self, load_nodes: Iterable[LoadNode]) -> None:
        self.load_nodes.extend(list(load_nodes))

    def add_section(self, sections: Iterable[Section]) -> None:
        self.sections.extend(list(sections))

    def create_grid(self) -> None:
        if not self.load_nodes:
            raise ValueError("No load nodes were registered in GridElements.")

        nodes = {node.name: node for node in self.load_nodes}
        root = next((node for node in self.load_nodes if node.external_grid is not None), self.load_nodes[0])

        adjacency: Dict[str, List[Section]] = {node.name: [] for node in self.load_nodes}
        for section in self.sections:
            if section.is_closed:
                adjacency[section.n1.name].append(section)
                adjacency[section.n2.name].append(section)

        children: Dict[str, List[Section]] = {node.name: [] for node in self.load_nodes}
        parent_section: Dict[str, Section] = {}
        bfs_order: List[str] = []

        queue = deque([root.name])
        visited = {root.name}
        while queue:
            node_name = queue.popleft()
            bfs_order.append(node_name)
            for section in adjacency[node_name]:
                other = section.n2 if section.n1.name == node_name else section.n1
                if other.name in visited:
                    continue
                visited.add(other.name)
                if section.n1.name != node_name:
                    section = Section(
                        name=section.name,
                        n1=nodes[node_name],
                        n2=other,
                        line_model=section.line_model,
                        transformer=section.transformer,
                        switch=section.switch,
                        length=section.length,
                    )
                children[node_name].append(section)
                parent_section[other.name] = section
                queue.append(other.name)

        self.dist_grids["F0"] = DistributionGrid(
            name="F0",
            nodes=nodes,
            sections=self.sections,
            root=root,
            children=children,
            parent_section=parent_section,
            bfs_order=bfs_order,
        )
