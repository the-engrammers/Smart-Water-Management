from __future__ import annotations

import os
from datetime import datetime

import requests
import streamlit as st


CONTROL_API_URL = os.getenv("CONTROL_API_URL", "http://localhost:8000/control/pump")


def _call_control_api(action: str, zone: str | None = None) -> tuple[bool, str]:
    """
    Appelle l'API de contrôle de la pompe.
    """
    payload = {"action": action}
    if zone:
        payload["zone"] = zone

    try:
        response = requests.post(CONTROL_API_URL, json=payload, timeout=3)
        if response.status_code == 200:
            try:
                data = response.json()
                message = data.get("message", "Commande envoyée au backend.")
            except Exception:
                message = "Commande envoyée au backend."
            return True, message
        return False, f"Backend a renvoyé le statut {response.status_code}"
    except requests.exceptions.RequestException as exc:
        return False, f"Impossible de joindre l'API de contrôle ({exc})."


def render_pump_controls(recommendation: dict, selected_zone: str | None = None) -> None:
    """
    Affiche les boutons START/STOP et gère l'état de la pompe.
    """
    if "pump_status" not in st.session_state:
        st.session_state.pump_status = "STOPPED"
    if "total_water_saved" not in st.session_state:
        st.session_state.total_water_saved = 0.0
    if "irrigation_history" not in st.session_state:
        st.session_state.irrigation_history = []

    st.markdown("### ⚙️ Pump / Valve Controls")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🚀 START PUMP", type="primary", use_container_width=True):
            success, message = _call_control_api("start", selected_zone)
            api_reached = success
            st.session_state.pump_status = "RUNNING"
            if recommendation.get("volume", 0) > 0:
                irrigation_event = {
                    "timestamp": datetime.now(),
                    "volume": recommendation["volume"],
                    "crop": st.session_state.get("selected_crop", "Unknown"),
                    "action": "Started",
                    "zone": selected_zone or "All",
                }
                st.session_state.irrigation_history.append(irrigation_event)
                manual_waste = recommendation["volume"] * 0.25
                st.session_state.total_water_saved += manual_waste
                if api_reached:
                    st.success(
                        f"Pompe démarrée pour {selected_zone or 'All'} "
                        f"({recommendation['volume']:.1f} L). {message}"
                    )
                else:
                    st.warning(
                        f"Mode démo : backend injoignable. Pompe démarrée dans l'interface "
                        f"({recommendation['volume']:.1f} L). Lancez le backend (port 8000) pour contrôler le matériel."
                    )
            else:
                if api_reached:
                    st.warning("Aucune irrigation nécessaire selon l'IA.")
                else:
                    st.warning("Mode démo : état mis à jour localement. Backend non disponible.")

    with col2:
        if st.button("🛑 STOP PUMP", type="secondary", use_container_width=True):
            success, message = _call_control_api("stop", selected_zone)
            st.session_state.pump_status = "STOPPED"
            if success:
                st.info(f"Pompe arrêtée pour {selected_zone or 'All'}. {message}")
            else:
                st.warning(
                    "Mode démo : pompe arrêtée dans l'interface. Backend non disponible (lancez uvicorn sur le port 8000)."
                )

    with col3:
        pump_status_color = "#44FF44" if st.session_state.pump_status == "RUNNING" else "#FF4444"
        st.markdown(
            f"""
            <div class="pump-control">
                <h2 style="color: {pump_status_color}; margin: 0;">
                    {st.session_state.pump_status}
                </h2>
                <p style="font-size: 12px; color: #AAAAAA; margin-top: 4px;">
                    Zone: {selected_zone or "All"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

