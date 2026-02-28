import streamlit as st


def render_decision_box(recommendation: dict, zone: str | None = None) -> None:
    """
    Affiche la Smart Action Box avec la décision IA et la raison.
    """
    urgency_colors = {
        "HIGH": "#FF4444",
        "MEDIUM": "#FFAA00",
        "LOW": "#44FF44",
    }

    zone_label = f" | Zone: {zone}" if zone else ""

    st.markdown("### 🤖 Smart Action Box")
    st.markdown(
        f"""
        <div class="recommendation-box">
            <h3 style="color: {urgency_colors.get(recommendation.get('urgency', 'LOW'), '#44FF44')};
                       margin-bottom: 8px;">
                {recommendation.get('action', 'No Action')}
            </h3>
            <p style="font-size: 14px; margin: 0 0 6px 0; color: #CCCCCC;">
                <strong>AI Decision:</strong> {recommendation.get('action', 'No Action')} {zone_label}
            </p>
            <p style="font-size: 14px; margin: 0 0 6px 0;">
                <strong>Recommended Volume:</strong> {recommendation.get('volume', 0):.1f} L
            </p>
            <p style="font-size: 13px; color: #AAAAAA; margin: 0 0 6px 0;">
                <strong>Reasoning:</strong> {recommendation.get('reason', 'N/A')}
            </p>
            <p style="font-size: 12px; color: #888888; margin-top: 8px;">
                Soil Moisture: {recommendation.get('soil_moisture', 0):.1f}% |
                Flow Rate: {recommendation.get('flow_rate', 0):.2f} L/min
                {f" | Water Level: {recommendation.get('water_level'):.1f} m" if recommendation.get('water_level') is not None else ""}
                {f" | Temperature: {recommendation.get('temperature'):.1f} °C" if recommendation.get('temperature') is not None else ""}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

