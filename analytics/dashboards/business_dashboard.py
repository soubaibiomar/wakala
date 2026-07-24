import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Configuration de la page
st.set_page_config(page_title="Wakala Business Dashboard", layout="wide")

st.title("📊 Wakala - Business Dashboard")
st.markdown("Vue analytique de la marketplace (Géospatial, KPI, Séries Temporelles, A/B Testing)")

# Mock des données (dans la réalité, issues du Gold layer via PostgreSQL/dbt)
@st.cache_data
def load_mock_data():
    dates = pd.date_range(start="2023-01-01", periods=100, freq='D')
    demand = np.random.poisson(lam=50, size=100) + np.linspace(0, 20, 100)
    
    cities = ["Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir"]
    listings_geo = pd.DataFrame({
        "city": np.random.choice(cities, 500, p=[0.4, 0.2, 0.15, 0.15, 0.1]),
        "price": np.random.normal(150000, 50000, 500),
        "lat": np.random.choice([33.57, 34.02, 31.62, 35.75, 30.42], 500),
        "lon": np.random.choice([-7.58, -6.83, -7.98, -5.83, -9.59], 500)
    })
    
    ab_test_data = pd.DataFrame({
        "variant": ["A (Content)", "B (Collab)"],
        "ctr": [0.08, 0.12],
        "conversion_rate": [0.02, 0.035]
    })
    
    return dates, demand, listings_geo, ab_test_data

dates, demand, listings_geo, ab_test_data = load_mock_data()

# --- Section 1: KPIs & LTV ---
st.header("📈 Indicateurs Clés (KPIs)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Annonces Actives", "12,450", "+5.2%")
col2.metric("Taux de Conversion", "3.2%", "+0.4%")
col3.metric("LTV Moyen Acheteur", "850 MAD", "+12 MAD")
col4.metric("Marge Estimée", "1.2M MAD", "+8%")

st.divider()

# --- Section 2: Analyse Géospatiale ---
st.header("🗺️ Cartographie des Annonces (Géospatial)")
st.markdown("Répartition des véhicules par ville et prix moyen.")
fig_map = px.scatter_mapbox(
    listings_geo, lat="lat", lon="lon", color="price", size="price",
    color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=4,
    mapbox_style="carto-positron", hover_name="city"
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# --- Section 3: Prévision de la demande (Séries Temporelles) ---
st.header("🔮 Prévision de la Demande (Forecasting)")
st.markdown("Modèle Holt-Winters (Lissage Exponentiel) sur les requêtes de recherche.")

ts_data = pd.Series(demand, index=dates)
model = ExponentialSmoothing(ts_data, trend="add", seasonal=None, initialization_method="estimated")
fit_model = model.fit()
forecast = fit_model.forecast(15)

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(x=dates, y=demand, mode='lines', name='Demande Historique'))
fig_ts.add_trace(go.Scatter(x=forecast.index, y=forecast, mode='lines', name='Prévision (15j)', line=dict(dash='dash', color='red')))
st.plotly_chart(fig_ts, use_container_width=True)

st.divider()

# --- Section 4: Élasticité Prix ---
st.header("📉 Élasticité Prix & Attribution Marketing")
st.markdown("Corrélation entre le prix des véhicules (MAD) et le taux de clic (CTR).")

# Mock elasticity
prices = np.linspace(50000, 400000, 20)
ctr = 0.2 - (prices / 1000000) + np.random.normal(0, 0.01, 20)
fig_elast = px.scatter(x=prices, y=ctr, trendline="ols", labels={"x": "Prix (MAD)", "y": "Taux de Clic (CTR)"})
st.plotly_chart(fig_elast, use_container_width=True)

st.divider()

# --- Section 5: A/B Testing Recommandation ---
st.header("⚖️ A/B Testing - Moteur Hybride")
st.markdown("Comparaison des variantes du moteur de recommandation.")

fig_ab = px.bar(ab_test_data, x="variant", y=["ctr", "conversion_rate"], barmode="group",
                labels={"value": "Taux", "variable": "Métrique"},
                title="Performance par Variante")
st.plotly_chart(fig_ab, use_container_width=True)
