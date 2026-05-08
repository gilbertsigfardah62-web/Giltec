"""BiasharaFlow TZ - full Python prototype.

A Tanzania-focused business management and analytics app that combines:
- Operations flow (suppliers, transport, charges)
- Probability and data-science style forecasting
- Lewin's behavior model B = f(P, E)
- Dopamine-inspired motivation nudges
- World market vs Tanzania local price comparison
- Stock-screening prototype (educational, not investment advice)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import mean
from typing import Dict, List, Tuple


EINSTEIN_QUOTE = "Logic will get you from A to B. Imagination will take you everywhere."
ROOTED_FLOWING_MOTTO = "I am rooted, but I flow."


@dataclass
class Supplier:
    name: str
    location: str
    unit_cost_tzs: float
    reliability_score: float  # 0..1


@dataclass
class TransportOption:
    mode: str
    route: str
    cost_tzs: float
    delay_risk: float  # 0..1


@dataclass
class ItemMarketData:
    item: str
    local_price_tzs: float
    world_price_tzs: float
    expected_change_pct: float


@dataclass
class StockSignal:
    symbol: str
    recent_return_pct: float
    volatility_pct: float
    value_score: float  # 0..1


class BiasharaFlowTZ:
    def __init__(self, owner_name: str, business_name: str) -> None:
        self.owner_name = owner_name
        self.business_name = business_name
        self.behavior_state: Dict[str, float] = {
            "motivation": 0.55,
            "focus": 0.50,
            "fatigue": 0.35,
        }

    # --------------------------- Behavior Layer ---------------------------
    @staticmethod
    def lewin_behavior(person_factor: float, environment_factor: float) -> float:
        """Lewin: B = f(P, E), normalized to 0..1."""
        p = max(0.0, min(1.0, person_factor))
        e = max(0.0, min(1.0, environment_factor))
        return round(0.6 * p + 0.4 * e, 3)

    def dopamine_nudge(self, progress_ratio: float) -> float:
        """Increase motivation when progress milestones are reached."""
        ratio = max(0.0, min(1.0, progress_ratio))
        if ratio >= 0.8:
            bump = 0.10
        elif ratio >= 0.5:
            bump = 0.05
        else:
            bump = 0.0
        self.behavior_state["motivation"] = min(1.0, self.behavior_state["motivation"] + bump)
        return round(self.behavior_state["motivation"], 3)

    # ------------------------- Operations Layer --------------------------
    @staticmethod
    def landed_cost_per_unit(
        supplier: Supplier,
        transport: TransportOption,
        quantity: int,
        other_charges_tzs: float,
    ) -> float:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        total = supplier.unit_cost_tzs * quantity + transport.cost_tzs + other_charges_tzs
        return total / quantity

    @staticmethod
    def gross_profit(revenue_tzs: float, total_cost_tzs: float) -> float:
        return revenue_tzs - total_cost_tzs

    @staticmethod
    def margin_pct(revenue_tzs: float, profit_tzs: float) -> float:
        if revenue_tzs <= 0:
            return 0.0
        return round((profit_tzs / revenue_tzs) * 100, 2)

    @staticmethod
    def choose_best_supplier(
        suppliers: List[Supplier],
        quantity: int,
        transport_cost_tzs: float,
        other_charges_tzs: float,
    ) -> Supplier:
        """Simple multi-factor score: cost efficiency + reliability."""
        best: Tuple[float, Supplier] | None = None
        for s in suppliers:
            total = s.unit_cost_tzs * quantity + transport_cost_tzs + other_charges_tzs
            score = (0.7 * (1 / total)) + (0.3 * s.reliability_score)
            if best is None or score > best[0]:
                best = (score, s)
        if best is None:
            raise ValueError("No suppliers provided.")
        return best[1]

    # ---------------------- Probability / Forecasting --------------------
    @staticmethod
    def profit_probability(history_profits: List[float]) -> float:
        if not history_profits:
            return 0.0
        wins = sum(1 for p in history_profits if p > 0)
        return round(wins / len(history_profits), 3)

    @staticmethod
    def expected_profit(history_profits: List[float]) -> float:
        return round(mean(history_profits), 2) if history_profits else 0.0

    @staticmethod
    def predict_price_rise_pct(
        market_data: ItemMarketData,
        oil_shock: float,
        war_risk: float,
        transport_stress: float,
    ) -> float:
        """Interpretable pressure model for near-term price movement."""
        base = market_data.expected_change_pct
        risk_factor = (0.45 * oil_shock) + (0.35 * war_risk) + (0.20 * transport_stress)
        # scale risk_factor (0..1) into additional 0..14% pressure
        return round(base + (14 * max(0.0, min(1.0, risk_factor))), 2)

    @staticmethod
    def compare_world_vs_tanzania(market_data: ItemMarketData) -> str:
        diff = market_data.world_price_tzs - market_data.local_price_tzs
        if diff > 0:
            return (
                f"{market_data.item}: World market price is {diff:,.0f} TZS ABOVE Tanzania local price."
            )
        if diff < 0:
            return (
                f"{market_data.item}: World market price is {abs(diff):,.0f} TZS BELOW Tanzania local price."
            )
        return f"{market_data.item}: World and Tanzania prices are equal."

    # ------------------------- Stock Prototype ---------------------------
    @staticmethod
    def stock_buy_advice(signal: StockSignal) -> str:
        """Educational scoring only; not financial advice."""
        momentum_score = signal.recent_return_pct / 20  # normalized rough scale
        risk_penalty = signal.volatility_pct / 30
        combined = (0.5 * signal.value_score) + (0.35 * momentum_score) - (0.15 * risk_penalty)

        if combined >= 0.60:
            verdict = "BUY candidate"
        elif combined >= 0.35:
            verdict = "WATCH"
        else:
            verdict = "HOLD/AVOID"

        return f"{signal.symbol}: {verdict} (score={combined:.2f})"

    # --------------------------- Reporting ------------------------------
    def business_health_score(
        self,
        behavior_score: float,
        profit_probability: float,
        margin_percent: float,
        supplier_reliability: float,
    ) -> float:
        normalized_margin = max(0.0, min(1.0, margin_percent / 30))
        score = (
            0.30 * behavior_score
            + 0.30 * profit_probability
            + 0.25 * normalized_margin
            + 0.15 * supplier_reliability
        )
        return round(score, 3)


def run_demo() -> None:
    app = BiasharaFlowTZ(owner_name="Asha", business_name="Asha Smart Trade")

    print("=" * 72)
    print("BiasharaFlow TZ - Tanzania Business Flow + Data Science Prototype")
    print("=" * 72)
    print(EINSTEIN_QUOTE)
    print(ROOTED_FLOWING_MOTTO)
    print(f"Date: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}")

    suppliers = [
        Supplier("Kariakoo Hub", "Dar es Salaam", 28_000, 0.86),
        Supplier("Mwanza Link", "Mwanza", 27_200, 0.78),
        Supplier("Arusha Trade Center", "Arusha", 29_100, 0.92),
    ]
    transport = TransportOption("Truck", "Dar -> Dodoma", 180_000, 0.22)
    quantity = 100
    other_charges = 95_000

    best_supplier = app.choose_best_supplier(
        suppliers, quantity, transport_cost_tzs=transport.cost_tzs, other_charges_tzs=other_charges
    )
    unit_landed = app.landed_cost_per_unit(best_supplier, transport, quantity, other_charges)
    total_cost = unit_landed * quantity

    sell_price_per_unit = 36_000
    revenue = sell_price_per_unit * quantity
    profit = app.gross_profit(revenue, total_cost)
    margin = app.margin_pct(revenue, profit)

    history = [120_000, -30_000, 88_000, 54_000, -12_000, 93_000, 110_000, 42_000]
    p_profit = app.profit_probability(history)
    exp_profit = app.expected_profit(history)

    behavior = app.lewin_behavior(person_factor=0.74, environment_factor=0.67)
    motivation = app.dopamine_nudge(progress_ratio=0.84)

    market_items = [
        ItemMarketData("Cooking Oil (20L)", 120_000, 132_000, 5.5),
        ItemMarketData("Wheat Flour (50kg)", 58_000, 62_000, 4.0),
    ]

    stocks = [
        StockSignal("CRDB", recent_return_pct=14.2, volatility_pct=9.1, value_score=0.71),
        StockSignal("NMB", recent_return_pct=9.0, volatility_pct=7.4, value_score=0.63),
        StockSignal("TBL", recent_return_pct=4.1, volatility_pct=12.0, value_score=0.55),
    ]

    print("\n--- Operations ---")
    print(f"Selected supplier: {best_supplier.name} ({best_supplier.location})")
    print(f"Landed cost/unit: {unit_landed:,.0f} TZS")
    print(f"Total cost: {total_cost:,.0f} TZS")
    print(f"Revenue: {revenue:,.0f} TZS")
    print(f"Gross profit: {profit:,.0f} TZS")
    print(f"Margin: {margin:.2f}%")

    print("\n--- Probability + Data Science ---")
    print(f"Profit probability: {p_profit:.1%}")
    print(f"Expected profit from history: {exp_profit:,.0f} TZS")

    print("\n--- Behavior (Lewin + Dopamine) ---")
    print(f"Behavior readiness B=f(P,E): {behavior:.2f}")
    print(f"Motivation after progress nudge: {motivation:.2f}")

    print("\n--- Market Price Intelligence ---")
    for item in market_items:
        print("-", app.compare_world_vs_tanzania(item))
        forecast = app.predict_price_rise_pct(item, oil_shock=0.60, war_risk=0.70, transport_stress=0.45)
        print(f"  Predicted near-term rise pressure: {forecast:.2f}%")

    print("\n--- Stock Prototype Signals (Educational) ---")
    for s in stocks:
        print("-", app.stock_buy_advice(s))

    health = app.business_health_score(
        behavior_score=behavior,
        profit_probability=p_profit,
        margin_percent=margin,
        supplier_reliability=best_supplier.reliability_score,
    )
    print("\n--- Strategic Output ---")
    print(f"Business health score: {health:.3f}/1.000")
    print(
        "Real-world value: integrated decisions on supplier choice, costs, prices, risk, and behavior."
    )
    print(
        "If absent: higher chance of fragmented decisions, weaker forecasting, and missed margin opportunities."
    )
    print("\nDisclaimer: Stock signals are educational prototypes, not financial advice.")


if __name__ == "__main__":
    run_demo()
