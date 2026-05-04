"""
BiasharaFlow TZ
A Tanzania-focused business flow and market-intelligence prototype app.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Dict, List


EINSTEIN_QUOTE = "Logic will get you from A to B. Imagination will take you everywhere."
ROOTED_FLOWING_MOTTO = "I am rooted, but I flow."


@dataclass
class Supplier:
    name: str
    location: str
    unit_cost_tzs: float


@dataclass
class TransportOption:
    mode: str
    cost_tzs: float


@dataclass
class StockSignal:
    symbol: str
    trend_score: float  # -1 to +1
    valuation_score: float  # -1 to +1


@dataclass
class ItemMarketData:
    item: str
    local_price_tzs: float
    world_price_tzs: float
    expected_change_pct: float


class BiasharaFlowTZ:
    """Prototype engine that combines operations, behavior, and lightweight data science."""

    def __init__(self) -> None:
        self.behavior_state: Dict[str, float] = {
            "motivation": 0.55,
            "fatigue": 0.35,
            "focus": 0.50,
        }

    @staticmethod
    def lewin_behavior(person_factor: float, environment_factor: float) -> float:
        """
        Lewin's field theory (B = f(P, E)) translated to a simple score.
        Returns a behavior-readiness score between 0 and 1.
        """
        raw = 0.6 * person_factor + 0.4 * environment_factor
        return max(0.0, min(1.0, raw))

    def dopamine_nudge(self, progress_ratio: float) -> float:
        """Simple dopamine effect proxy to increase motivation after progress milestones."""
        bump = 0.10 if progress_ratio >= 0.8 else 0.05 if progress_ratio >= 0.5 else 0.0
        self.behavior_state["motivation"] = min(1.0, self.behavior_state["motivation"] + bump)
        return self.behavior_state["motivation"]

    @staticmethod
    def compute_total_cost(
        supplier: Supplier,
        transport: TransportOption,
        quantity: int,
        other_charges_tzs: float,
    ) -> float:
        return supplier.unit_cost_tzs * quantity + transport.cost_tzs + other_charges_tzs

    @staticmethod
    def gross_profit(revenue_tzs: float, total_cost_tzs: float) -> float:
        return revenue_tzs - total_cost_tzs

    @staticmethod
    def profit_probability(history_profits: List[float]) -> float:
        """Probability of profit based on historical outcomes."""
        if not history_profits:
            return 0.0
        positives = sum(1 for p in history_profits if p > 0)
        return positives / len(history_profits)

    @staticmethod
    def stock_buy_advice(signal: StockSignal) -> str:
        combined = 0.7 * signal.trend_score + 0.3 * signal.valuation_score
        if combined > 0.35:
            return f"BUY candidate: {signal.symbol}"
        if combined > 0.10:
            return f"WATCH closely: {signal.symbol}"
        return f"HOLD/AVOID for now: {signal.symbol}"

    @staticmethod
    def predict_price_rise(item: ItemMarketData, oil_shock: float, war_risk: float) -> float:
        """Small explanatory model for future price increase pressure."""
        shock_factor = 0.5 * oil_shock + 0.5 * war_risk
        return item.expected_change_pct + shock_factor * 12

    @staticmethod
    def compare_world_local(item: ItemMarketData) -> str:
        diff = item.world_price_tzs - item.local_price_tzs
        sign = "higher" if diff > 0 else "lower"
        return f"{item.item}: World market price is {abs(diff):,.0f} TZS {sign} than Tanzania local price."


def demo() -> None:
    app = BiasharaFlowTZ()

    print("=== BiasharaFlow TZ ===")
    print(EINSTEIN_QUOTE)
    print(ROOTED_FLOWING_MOTTO)

    supplier = Supplier("Kariakoo Wholesale Hub", "Dar es Salaam", unit_cost_tzs=28_000)
    transport = TransportOption("Truck", cost_tzs=180_000)
    total_cost = app.compute_total_cost(supplier, transport, quantity=100, other_charges_tzs=90_000)
    revenue = 3_600_000
    profit = app.gross_profit(revenue, total_cost)

    history = [120_000, -30_000, 88_000, 54_000, -12_000, 93_000]
    p_profit = app.profit_probability(history)

    readiness = app.lewin_behavior(person_factor=0.72, environment_factor=0.65)
    motivation = app.dopamine_nudge(progress_ratio=0.83)

    # NOTE: signal values are mock values for demonstration only.
    stock_signals = [
        StockSignal("CRDB", trend_score=0.52, valuation_score=0.20),
        StockSignal("NMB", trend_score=0.26, valuation_score=0.12),
        StockSignal("SWISS", trend_score=-0.05, valuation_score=0.08),
    ]

    price_data = [
        ItemMarketData("Cooking Oil (20L)", local_price_tzs=120_000, world_price_tzs=132_000, expected_change_pct=5.5),
        ItemMarketData("Wheat Flour (50kg)", local_price_tzs=58_000, world_price_tzs=62_000, expected_change_pct=4.0),
    ]

    print(f"Supplier: {supplier.name} ({supplier.location})")
    print(f"Total cost: {total_cost:,.0f} TZS")
    print(f"Revenue: {revenue:,.0f} TZS")
    print(f"Gross profit: {profit:,.0f} TZS")
    print(f"Profit probability: {p_profit:.1%}")
    print(f"Behavior readiness (Lewin B=f(P,E)): {readiness:.2f}")
    print(f"Motivation after dopamine nudge: {motivation:.2f}")

    print("\nStock advice (prototype):")
    for s in stock_signals:
        print("-", app.stock_buy_advice(s))

    print("\nMarket price comparison (world vs Tanzania):")
    for item in price_data:
        print("-", app.compare_world_local(item))
        forecast = app.predict_price_rise(item, oil_shock=0.6, war_risk=0.7)
        print(f"  Predicted near-term rise pressure: {forecast:.1f}%")

    expected_margin = profit / revenue if revenue else 0
    summary_score = mean([readiness, motivation, p_profit, max(0.0, expected_margin)])
    print(f"\nBusiness health score: {summary_score:.2f}/1.00")


if __name__ == "__main__":
    demo()
