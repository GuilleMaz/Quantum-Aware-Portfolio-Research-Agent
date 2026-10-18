"""Modelos de cartera.

Esquemas para representar carteras y posiciones. Se implementan en la Fase 3.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PortfolioPosition(BaseModel):
    """Una posicion dentro de una cartera."""

    symbol: str
    shares: Decimal = Field(gt=0)
    average_cost: Decimal = Field(gt=0)
    opened_at: date | None = None

    @property
    def cost_basis(self) -> Decimal:
        """Coste total de la posicion."""
        return self.shares * self.average_cost

    @property
    def current_value(self) -> Decimal:
        """Valor de mercado actual (requiere el precio actual)."""
        raise NotImplementedError(
            "Se implementa en la Fase 3 con el precio del Analista Financiero."
        )

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }


class Portfolio(BaseModel):
    """Una cartera de inversion.

    Mapea con lo que devuelve ``create_portfolio`` de
    ``financial-mcp-server`` (paper trading). Nota: ese servidor persiste en
    SQLite local (``~/.financial-mcp/financial_mcp.db``), asi que la fuente de
    verdad de una cartera persistida es el servidor, no este modelo.
    """

    portfolio_id: str
    name: str = "Default"
    starting_capital: Decimal = Field(gt=0)
    risk_profile: str = "moderate"
    investment_horizon: str = "medium"
    positions: list[PortfolioPosition] = Field(default_factory=list)

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }


__all__ = ["Portfolio", "PortfolioPosition"]