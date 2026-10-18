"""Modelos de activo y metricas de riesgo/retorno.

Estos esquemas mapean 1:1 con lo que devuelve ``financial-mcp-server``:

- ``get_fundamentals`` -> campos de :class:`Fundamentals`
- ``get_momentum``     -> campos de :class:`MomentumMetrics`
- ``get_price_history``-> lista de :class:`PriceBar`

Se implementan en la Fase 3, al promover el codigo desde ``labs/``. Aqui solo
se fija el contrato de datos, verificado contra el catalogo real de 42 tools.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["bajo", "medio", "alto", "extremo"]


class PriceBar(BaseModel):
    """Una barra OHLCV.

    Fuente: ``get_price_history``. Nota: el servidor trunca siempre a los
    ultimos 250 bars (``_MAX_BARS``) e incluye un flag ``truncated``.
    """

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(ge=0)

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }


class Fundamentals(BaseModel):
    """Valoracion basica.

    Fuente: ``get_fundamentals``. Solo 7 campos, verificado:
    NO hay ROE, beta, deuda, FCF, P/E forward ni growth.
    Si el agente necesita mas, hay que calcularlo desde
    ``get_price_history`` o anadir otra fuente.
    """

    symbol: str
    pe_ratio: float | None = None
    ev_to_ebitda: float | None = None
    price_to_book: float | None = None
    dividend_yield: float | None = None
    market_cap: float | None = None
    sector: str | None = None
    industry: str | None = None

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }


class MomentumMetrics(BaseModel):
    """Momentum y riesgo de un activo.

    Fuente: ``get_momentum`` — trae TODO esto en una sola llamada, que es la
    opcion optima para el Agente Analista.

    Campos:
        price_momentum_30d: momento del precio a 30 dias.
        price_momentum_90d: momento del precio a 90 dias.
        volatility: desviacion tipica rolling 30d ANUALIZADA (x sqrt(252)).
            Es la unica metrica de volatilidad directa del servidor.
        relative_strength: momentum_90d / retorno_90d de SPY. Ojo: es un
            "beta de momentum", NO el beta de mercado.
        max_drawdown: peor caida desde maximo.
    """

    symbol: str
    price_momentum_30d: float
    price_momentum_90d: float
    volatility: float = Field(ge=0.0)
    relative_strength: float
    max_drawdown: float

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }


class Asset(BaseModel):
    """Un activo candidato con sus metricas.

    Es la unidad que el Agente Analista Financiero produce y que el Agente
    Investigador Cuantico consume para construir el QUBO.
    """

    symbol: str
    name: str | None = None
    price: float = Field(gt=0.0)
    fundamentals: Fundamentals | None = None
    momentum: MomentumMetrics | None = None
    sector: str | None = None

    @property
    def risk_level(self) -> RiskLevel:
        """Clasificacion de riesgo por volatilidad anualizada.

        Umbrales calibrados para el rango habitual de ``get_momentum``:
        <15% bajo, <25% medio, <40% alto, resto extremo.

        Mover estos umbrales al proyecto implica actualizarlos tambien en
        ``config/`` (ver ``AGENTS.md`` 3.3). Si se parametrizan, este metodo
        pasa a leer de la config.
        """
        if self.momentum is None:
            return "medio"
        vol = self.momentum.volatility
        if vol < 0.15:
            return "bajo"
        if vol < 0.25:
            return "medio"
        if vol < 0.40:
            return "alto"
        return "extremo"


__all__ = [
    "Asset",
    "Fundamentals",
    "MomentumMetrics",
    "PriceBar",
    "RiskLevel",
]