"""Smoke test: el paquete importa y los contratos de datos existen.

No necesita red, ni servidores MCP, ni Qiskit. Debe pasar siempre.
"""

from quantum_portfolio import __version__
from quantum_portfolio.graph.state import PortfolioState
from quantum_portfolio.mcp_clients.session_group import (
    DEFAULT_SERVERS_CONFIG,
    MCPServerSpec,
)
from quantum_portfolio.models.asset import Asset, Fundamentals, MomentumMetrics


def test_version_exists() -> None:
    assert __version__ == "0.1.0"


def test_state_is_typed_dict() -> None:
    assert PortfolioState.__annotations__["alta_volatilidad"] is bool


def test_mcp_server_spec_defaults() -> None:
    spec = MCPServerSpec(name="financial", command="uvx")
    assert spec.timeout_seconds == 60.0
    assert spec.args == ()


def test_asset_risk_without_momentum_defaults_to_medio() -> None:
    asset = Asset(symbol="AAPL", price=100.0)
    assert asset.risk_level == "medio"


def test_momentum_volatility_is_non_negative() -> None:
    m = MomentumMetrics(
        symbol="AAPL",
        price_momentum_30d=0.01,
        price_momentum_90d=0.02,
        volatility=0.2,
        relative_strength=1.0,
        max_drawdown=-0.05,
    )
    assert m.volatility >= 0.0


def test_servers_config_path_points_at_config() -> None:
    assert DEFAULT_SERVERS_CONFIG.name == "mcp_servers.json"


def test_fundamentals_allows_seven_known_fields() -> None:
    f = Fundamentals(symbol="AAPL", pe_ratio=39.39, sector="Technology")
    assert f.symbol == "AAPL"
