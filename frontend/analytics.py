from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pandas as pd
import streamlit as st


def _build_irrigation_df(
    irrigation_history: Iterable[dict],
    selected_zone: str | None = None,
) -> pd.DataFrame:
    df = pd.DataFrame(list(irrigation_history)) if irrigation_history else pd.DataFrame()
    if df.empty:
        return df

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    if selected_zone and selected_zone != "All":
        if "zone" in df.columns:
            df = df[df["zone"] == selected_zone]

    return df


def _aggregate_irrigation_trends(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Agrège les événements d'irrigation (pompe) par période."""
    if df.empty or "timestamp" not in df.columns or "volume" not in df.columns:
        return pd.DataFrame()

    if period == "Daily":
        df = df.copy()
        df["bucket"] = df["timestamp"].dt.date
    elif period == "Weekly":
        df = df.copy()
        df["bucket"] = df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time.date())
    else:  # Monthly
        df = df.copy()
        df["bucket"] = df["timestamp"].dt.to_period("M").apply(lambda r: r.start_time.date())

    grouped = (
        df.groupby("bucket")["volume"]
        .sum()
        .reset_index()
        .rename(columns={"bucket": "Period", "volume": "Irrigation Volume (L)"})
    )
    return grouped


def _aggregate_sensor_trends(
    df: pd.DataFrame, period: str, selected_zone: str | None = None
) -> pd.DataFrame:
    """Agrège flow_rate des capteurs par période pour enrichir les tendances."""
    if df.empty or "timestamp" not in df.columns or "flow_rate" not in df.columns:
        return pd.DataFrame()

    work = df.copy()
    if selected_zone and selected_zone != "All" and "device_id" in work.columns:
        work = work[work["device_id"] == selected_zone]
    work["flow_rate"] = pd.to_numeric(work["flow_rate"], errors="coerce").fillna(0)

    if period == "Daily":
        work["bucket"] = work["timestamp"].dt.date
    elif period == "Weekly":
        work["bucket"] = work["timestamp"].dt.to_period("W").apply(lambda r: r.start_time.date())
    else:
        work["bucket"] = work["timestamp"].dt.to_period("M").apply(lambda r: r.start_time.date())

    grouped = work.groupby("bucket")["flow_rate"].agg(sum="sum", mean="mean").reset_index()
    grouped = grouped.rename(columns={"bucket": "Period", "sum": "Flow Total (L/min)", "mean": "Avg Flow (L/min)"})
    return grouped


def render_analytics(
    df: pd.DataFrame,
    irrigation_history: Iterable[dict],
    total_water_saved: float,
    water_cost_per_m3: float,
    selected_zone: str | None = None,
) -> None:
    """
    Affiche la section Analytics (eau économisée, coûts, tendances).
    """
    st.markdown("### 📊 Water Savings & Analytics")

    # Calcul des métriques de base
    baseline_usage = 100.0
    ai_usage = max(0.0, baseline_usage - (total_water_saved or 0.0))
    savings_percentage = (total_water_saved / baseline_usage * 100) if baseline_usage > 0 else 0

    cost_per_liter = water_cost_per_m3 / 1000.0 if water_cost_per_m3 > 0 else 0.0
    total_cost_saved = total_water_saved * cost_per_liter

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Water Saved vs Manual",
            f"{total_water_saved:.1f} L",
            delta=f"{savings_percentage:.1f}% estimated",
        )
    with col2:
        st.metric("AI Usage (Index)", f"{ai_usage:.1f}", delta="- water vs baseline")
    with col3:
        st.metric(
            "Cost Saved",
            f"{total_cost_saved:,.2f}",
            delta=f"Cost/l: {cost_per_liter:.4f}",
        )
    with col4:
        st.metric(
            "Selected Zone",
            selected_zone or "All",
        )

    st.markdown("#### 📈 Historical Irrigation Trends")
    trends_period = st.radio(
        "Aggregation period",
        options=["By event", "Daily", "Weekly", "Monthly"],
        horizontal=True,
        key="trends_period_radio",
    )

    irrigation_df = _build_irrigation_df(irrigation_history, selected_zone)

    if trends_period == "By event":
        # Each irrigation event = one point (no aggregation)
        if irrigation_df.empty:
            st.info("No irrigation events yet. Start the pump to see trends.")
        else:
            chart_df = (
                irrigation_df[["timestamp", "volume"]]
                .rename(columns={"timestamp": "Time", "volume": "Irrigation Volume (L)"})
                .set_index("Time")
                .sort_index()
            )
            st.line_chart(chart_df, use_container_width=True)
    else:
        irrigation_trends = _aggregate_irrigation_trends(irrigation_df, trends_period)
        sensor_trends = _aggregate_sensor_trends(df, trends_period, selected_zone)

        chart_df = None
        if not irrigation_trends.empty and not sensor_trends.empty:
            chart_df = irrigation_trends.merge(
                sensor_trends, on="Period", how="outer"
            ).sort_values("Period")
        elif not irrigation_trends.empty:
            chart_df = irrigation_trends.sort_values("Period")
        elif not sensor_trends.empty:
            chart_df = sensor_trends.sort_values("Period")

        if chart_df is None or chart_df.empty:
            st.info("No data yet. Run the simulator or start the pump.")
        else:
            display_cols = [c for c in chart_df.columns if c != "Period"]
            plot_data = chart_df.set_index("Period")[display_cols].fillna(0)
            st.line_chart(plot_data, use_container_width=True)

