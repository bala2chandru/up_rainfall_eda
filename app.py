import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="UP Rainfall & Weather EDA 2005–2025",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .top-banner {
    background: linear-gradient(135deg, #1a3a5c 0%, #1565c0 50%, #0d47a1 100%);
    border-radius: 8px;
    padding: 24px 32px;
    margin-bottom: 20px;
    border-left: 6px solid #29b6f6;
  }
  .banner-title { color: #fff; font-size: 1.8rem; font-weight: 700; }
  .banner-sub   { color: #90caf9; font-size: 0.85rem; margin-top: 4px; }

  .kpi-card {
    background: #fff;
    border-radius: 8px;
    padding: 16px 20px;
    border: 1px solid #e3f2fd;
    border-top: 3px solid #1565c0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .kpi-card.rain  { border-top-color: #29b6f6; }
  .kpi-card.heat  { border-top-color: #ef5350; }
  .kpi-card.green { border-top-color: #26a69a; }
  .kpi-card.warn  { border-top-color: #ffa726; }
  .kpi-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
               letter-spacing: 0.08em; color: #78909c; margin-bottom: 6px; }
  .kpi-value { font-size: 1.7rem; font-weight: 700; color: #1a2b3c; line-height: 1; }
  .kpi-sub   { font-size: 0.73rem; color: #90a4ae; margin-top: 4px; }

  .section-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #1565c0;
    border-left: 3px solid #29b6f6; padding-left: 10px;
    margin-bottom: 14px; margin-top: 6px;
  }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import gdown, os
    file_path = 'UP_rainfall_dataset.csv'
    if not os.path.exists(file_path):
        gdown.download(id='1_RrpvucHC1GINiZ_0udzCR__tbp0XDiQ', output=file_path, quiet=False)
    df = pd.read_csv(file_path)
    df['DISTRICT'] = df['DISTRICT'].str.strip().str.title()
    df['DATE'] = pd.to_datetime(df[['YEAR','MO','DY']].rename(
        columns={'YEAR':'year','MO':'month','DY':'day'}))
    df['SEASON'] = df['MO'].map({
        12:'Winter', 1:'Winter', 2:'Winter',
        3:'Pre-Monsoon', 4:'Pre-Monsoon', 5:'Pre-Monsoon',
        6:'Monsoon', 7:'Monsoon', 8:'Monsoon', 9:'Monsoon',
        10:'Post-Monsoon', 11:'Post-Monsoon'
    })
    df['Rain_Category'] = pd.cut(df['PRECTOTCORR'],
        bins=[-0.01,0,2.5,7.5,35.5,64.5,115.5,1000],
        labels=['No Rain','Light','Moderate','Heavy','Very Heavy','Extremely Heavy','Catastrophic'])
    return df

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌧️ Filters")
    st.markdown("---")

    districts = ["All"] + sorted(df['DISTRICT'].unique().tolist())
    sel_district = st.selectbox("District", districts)

    years = ["All"] + sorted(df['YEAR'].unique().tolist())
    sel_year = st.selectbox("Year", years)

    seasons = ["All", "Monsoon", "Pre-Monsoon", "Post-Monsoon", "Winter"]
    sel_season = st.selectbox("Season", seasons)

    months = ["All"] + list(range(1, 13))
    sel_month = st.selectbox("Month", months)

    rain_min = st.slider("Min Daily Rainfall (mm)", 0.0, 280.0, 0.0, step=1.0)

    st.markdown("---")
    st.caption("Data: NASA POWER Climate Data | 2005–2025")
    st.markdown("**Built with ❤️ using Streamlit**")

# ── APPLY FILTERS ─────────────────────────────────────────────────────
fdf = df.copy()
if sel_district != "All": fdf = fdf[fdf['DISTRICT'] == sel_district]
if sel_year     != "All": fdf = fdf[fdf['YEAR']     == int(sel_year)]
if sel_season   != "All": fdf = fdf[fdf['SEASON']   == sel_season]
if sel_month    != "All": fdf = fdf[fdf['MO']        == int(sel_month)]
if rain_min > 0:          fdf = fdf[fdf['PRECTOTCORR'] >= rain_min]

# ── BANNER ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-banner">
  <div class="banner-title">🌧️ Uttar Pradesh Rainfall & Weather Analytics</div>
  <div class="banner-sub">NASA POWER Climate Data &nbsp;·&nbsp; 2005–2025 &nbsp;·&nbsp;
  {df['DISTRICT'].nunique()} Districts &nbsp;·&nbsp;
  {len(fdf):,} of {len(df):,} records shown</div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────
avg_rain    = fdf['PRECTOTCORR'].mean()
max_rain    = fdf['PRECTOTCORR'].max()
rain_days   = (fdf['PRECTOTCORR'] > 0).mean() * 100
avg_max_t   = fdf['T2M_MAX'].mean()
avg_min_t   = fdf['T2M_MIN'].mean()
extreme_ct  = (fdf['PRECTOTCORR'] >= 64.5).sum()

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.markdown(f'<div class="kpi-card rain"><div class="kpi-label">Avg Daily Rainfall</div><div class="kpi-value">{avg_rain:.2f}</div><div class="kpi-sub">mm per day</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi-card warn"><div class="kpi-label">Max Single Day</div><div class="kpi-value">{max_rain:.1f}</div><div class="kpi-sub">mm recorded</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi-card green"><div class="kpi-label">Rain Day %</div><div class="kpi-value">{rain_days:.1f}%</div><div class="kpi-sub">days with rainfall</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi-card heat"><div class="kpi-label">Avg Max Temp</div><div class="kpi-value">{avg_max_t:.1f}°C</div><div class="kpi-sub">daily maximum</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Min Temp</div><div class="kpi-value">{avg_min_t:.1f}°C</div><div class="kpi-sub">daily minimum</div></div>', unsafe_allow_html=True)
k6.markdown(f'<div class="kpi-card warn"><div class="kpi-label">Extreme Events</div><div class="kpi-value">{extreme_ct:,}</div><div class="kpi-sub">days >64.5mm</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5,t6,t7 = st.tabs([
    "🌧️ Rainfall Overview",
    "📅 Annual Trends",
    "🗓️ Seasonal & Monthly",
    "🗺️ District Analysis",
    "🌡️ Temperature",
    "💨 Humidity & Wind",
    "⚡ Extreme Events"
])

# ─── TAB 1: RAINFALL OVERVIEW ─────────────────────────────────────────
with t1:
    st.markdown('<div class="section-label">Rainfall Distribution & Intensity</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        rain_nz = fdf[fdf['PRECTOTCORR'] > 0]['PRECTOTCORR']
        fig = px.histogram(rain_nz, x='PRECTOTCORR', nbins=60,
                           color_discrete_sequence=['#1565c0'],
                           title='Daily Rainfall Distribution (Rain Days Only)',
                           labels={'PRECTOTCORR':'Rainfall (mm)'})
        fig.add_vline(x=rain_nz.mean(), line_dash='dash', line_color='red',
                      annotation_text=f"Mean: {rain_nz.mean():.1f}mm")
        fig.update_layout(height=380, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        rain_d = (fdf['PRECTOTCORR'] > 0).sum()
        dry_d  = (fdf['PRECTOTCORR'] == 0).sum()
        fig2 = px.pie(values=[rain_d, dry_d],
                      names=['Rain Days', 'Dry Days'],
                      color_discrete_sequence=['#1565c0','#ef5350'],
                      title='Rain Days vs Dry Days', hole=0.45)
        fig2.update_traces(textinfo='label+percent')
        fig2.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Rainfall category distribution
    cat_order = ['No Rain','Light','Moderate','Heavy','Very Heavy','Extremely Heavy','Catastrophic']
    cat_colors = ['#90a4ae','#29b6f6','#26a69a','#ffa726','#ef5350','#8e44ad','#2c3e50']
    cat_df = fdf['Rain_Category'].value_counts().reindex(cat_order).reset_index()
    cat_df.columns = ['Category','Count']
    fig3 = px.bar(cat_df, x='Category', y='Count',
                  color='Category',
                  color_discrete_sequence=cat_colors,
                  title='Rainfall Intensity Category Distribution',
                  text='Count')
    fig3.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig3.update_layout(showlegend=False, height=380,
                       plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig3, use_container_width=True)

# ─── TAB 2: ANNUAL TRENDS ─────────────────────────────────────────────
with t2:
    st.markdown('<div class="section-label">Annual Rainfall & Temperature Trends</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        yr = fdf.groupby('YEAR')['PRECTOTCORR'].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=yr['YEAR'], y=yr['PRECTOTCORR'],
                             name='Annual Rainfall', marker_color='#1565c0', opacity=0.85))
        if len(yr) > 1:
            z = np.polyfit(yr['YEAR'], yr['PRECTOTCORR'], 1)
            p = np.poly1d(z)
        fig.add_trace(go.Scatter(x=yr['YEAR'], y=p(yr['YEAR']),
                                 name='Trend', line=dict(color='red', width=2, dash='dash')))
        fig.update_layout(title='Annual Total Rainfall Across UP (mm)',
                          xaxis_title='Year', yaxis_title='Total Rainfall (mm)',
                          height=400, plot_bgcolor='white', paper_bgcolor='white',
                          legend=dict(orientation='h', y=1.12))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        yt = fdf.groupby('YEAR')[['T2M_MAX','T2M_MIN']].mean().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=yt['YEAR'], y=yt['T2M_MAX'],
                                  name='Avg Max Temp', line=dict(color='#ef5350', width=2.5),
                                  mode='lines+markers', marker=dict(size=6)))
        fig2.add_trace(go.Scatter(x=yt['YEAR'], y=yt['T2M_MIN'],
                                  name='Avg Min Temp', line=dict(color='#29b6f6', width=2.5),
                                  mode='lines+markers', marker=dict(size=6),
                                  fill='tonexty', fillcolor='rgba(0,0,0,0.05)'))
        fig2.update_layout(title='Annual Temperature Trend (°C)',
                           xaxis_title='Year', yaxis_title='Temperature (°C)',
                           height=400, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    # Annual rain days
    yr_rain_days = fdf.groupby('YEAR').apply(lambda x: (x['PRECTOTCORR']>0).sum()).reset_index()
    yr_rain_days.columns = ['Year','Rain Days']
    fig3 = px.line(yr_rain_days, x='Year', y='Rain Days',
                   markers=True, color_discrete_sequence=['#26a69a'],
                   title='Annual Rain Days Count',
                   labels={'Rain Days':'Number of Rain Days'})
    fig3.update_traces(line_width=2.5, marker_size=7)
    fig3.update_layout(height=360, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig3, use_container_width=True)

# ─── TAB 3: SEASONAL & MONTHLY ────────────────────────────────────────
with t3:
    st.markdown('<div class="section-label">Seasonal & Monthly Patterns</div>', unsafe_allow_html=True)

    season_order = ['Winter','Pre-Monsoon','Monsoon','Post-Monsoon']
    season_colors = {'Winter':'#29b6f6','Pre-Monsoon':'#ffa726',
                     'Monsoon':'#26a69a','Post-Monsoon':'#ef5350'}

    c1, c2 = st.columns(2)
    with c1:
        s_rain = fdf.groupby('SEASON')['PRECTOTCORR'].mean().reindex(season_order).reset_index()
        fig = px.bar(s_rain, x='SEASON', y='PRECTOTCORR',
                     color='SEASON', color_discrete_map=season_colors,
                     title='Avg Daily Rainfall by Season (mm)',
                     text='PRECTOTCORR')
        fig.update_traces(texttemplate='%{text:.2f}mm', textposition='outside')
        fig.update_layout(showlegend=False, height=380,
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        month_labels = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                        7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        m_rain = fdf.groupby('MO')['PRECTOTCORR'].mean().reset_index()
        m_rain['Month'] = m_rain['MO'].map(month_labels)
        fig2 = px.bar(m_rain, x='Month', y='PRECTOTCORR',
                      color='PRECTOTCORR', color_continuous_scale='Blues',
                      title='Avg Monthly Daily Rainfall (mm)',
                      text='PRECTOTCORR')
        fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside', textfont_size=9)
        fig2.update_layout(coloraxis_showscale=False, height=380,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        s_temp = fdf.groupby('SEASON')[['T2M_MAX','T2M_MIN']].mean().reindex(season_order).reset_index()
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=s_temp['SEASON'], y=s_temp['T2M_MAX'],
                              name='Max Temp', marker_color='#ef5350', opacity=0.85))
        fig3.add_trace(go.Bar(x=s_temp['SEASON'], y=s_temp['T2M_MIN'],
                              name='Min Temp', marker_color='#29b6f6', opacity=0.85))
        fig3.update_layout(barmode='group', title='Avg Temperature by Season (°C)',
                           height=380, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        m_hum = fdf.groupby('MO')['RH2M'].mean().reset_index()
        m_hum['Month'] = m_hum['MO'].map(month_labels)
        fig4 = px.line(m_hum, x='Month', y='RH2M',
                       markers=True, color_discrete_sequence=['#8e44ad'],
                       title='Avg Monthly Humidity (%)',
                       labels={'RH2M':'Relative Humidity (%)'})
        fig4.update_traces(line_width=2.5, marker_size=8)
        fig4.update_layout(height=380, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True)

# ─── TAB 4: DISTRICT ANALYSIS ─────────────────────────────────────────
with t4:
    st.markdown('<div class="section-label">District-Wise Rainfall Patterns</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        d_rain = fdf.groupby('DISTRICT')['PRECTOTCORR'].sum().sort_values(ascending=False).reset_index()
        d_rain.columns = ['District','Total Rainfall']
        fig = px.bar(d_rain.head(25), x='Total Rainfall', y='District',
                     orientation='h', color='Total Rainfall',
                     color_continuous_scale='Blues',
                     title='Top 25 Districts — Total Rainfall (mm)')
        fig.update_layout(coloraxis_showscale=False, height=600,
                          plot_bgcolor='white', paper_bgcolor='white',
                          yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        d_avg = fdf.groupby('DISTRICT')['PRECTOTCORR'].mean().sort_values(ascending=False).reset_index()
        d_avg.columns = ['District','Avg Daily Rainfall']
        fig2 = px.bar(d_avg.head(25), x='Avg Daily Rainfall', y='District',
                      orientation='h', color='Avg Daily Rainfall',
                      color_continuous_scale='Teal',
                      title='Top 25 Districts — Avg Daily Rainfall (mm)',
                      text='Avg Daily Rainfall')
        fig2.update_traces(texttemplate='%{text:.2f}mm', textposition='outside', textfont_size=9)
        fig2.update_layout(coloraxis_showscale=False, height=600,
                           plot_bgcolor='white', paper_bgcolor='white',
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    # District avg temp
    d_temp = fdf.groupby('DISTRICT')[['T2M_MAX','T2M_MIN']].mean().reset_index()
    d_temp = d_temp.sort_values('T2M_MAX', ascending=False).head(20)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=d_temp['DISTRICT'], y=d_temp['T2M_MAX'],
                          name='Avg Max Temp', marker_color='#ef5350', opacity=0.85))
    fig3.add_trace(go.Bar(x=d_temp['DISTRICT'], y=d_temp['T2M_MIN'],
                          name='Avg Min Temp', marker_color='#29b6f6', opacity=0.85))
    fig3.update_layout(barmode='group', title='Avg Temperature by District (Top 20) °C',
                       height=420, plot_bgcolor='white', paper_bgcolor='white',
                       xaxis_tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)

# ─── TAB 5: TEMPERATURE ───────────────────────────────────────────────
with t5:
    st.markdown('<div class="section-label">Temperature Patterns</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=fdf['T2M_MAX'], name='Max Temp',
                                   marker_color='#ef5350', opacity=0.7, nbinsx=50))
        fig.add_trace(go.Histogram(x=fdf['T2M_MIN'], name='Min Temp',
                                   marker_color='#29b6f6', opacity=0.7, nbinsx=50))
        fig.update_layout(barmode='overlay', title='Temperature Distribution (°C)',
                          height=400, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        month_labels = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                        7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        m_temp = fdf.groupby('MO')[['T2M_MAX','T2M_MIN']].mean().reset_index()
        m_temp['Month'] = m_temp['MO'].map(month_labels)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=m_temp['Month'], y=m_temp['T2M_MAX'],
                                  name='Avg Max Temp', line=dict(color='#ef5350', width=2.5),
                                  mode='lines+markers', marker=dict(size=7)))
        fig2.add_trace(go.Scatter(x=m_temp['Month'], y=m_temp['T2M_MIN'],
                                  name='Avg Min Temp', line=dict(color='#29b6f6', width=2.5),
                                  mode='lines+markers', marker=dict(size=7),
                                  fill='tonexty', fillcolor='rgba(100,150,200,0.1)'))
        fig2.update_layout(title='Monthly Temperature Range (°C)',
                           height=400, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    # Temp vs rainfall scatter
    sample = fdf.sample(min(5000, len(fdf)), random_state=42)
    fig3 = px.scatter(sample, x='T2M_MAX', y='PRECTOTCORR',
                      color='RH2M', color_continuous_scale='Blues',
                      opacity=0.5, size_max=6,
                      title='Max Temperature vs Rainfall (colour = Humidity)',
                      labels={'T2M_MAX':'Max Temp (°C)',
                              'PRECTOTCORR':'Rainfall (mm)',
                              'RH2M':'Humidity (%)'})
    fig3.update_layout(height=420, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig3, use_container_width=True)

# ─── TAB 6: HUMIDITY & WIND ───────────────────────────────────────────
with t6:
    st.markdown('<div class="section-label">Humidity, Wind & Atmospheric Conditions</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(fdf, x='RH2M', nbins=50,
                           color_discrete_sequence=['#8e44ad'],
                           title='Relative Humidity Distribution (%)',
                           labels={'RH2M':'Relative Humidity (%)'})
        fig.add_vline(x=fdf['RH2M'].mean(), line_dash='dash', line_color='red',
                      annotation_text=f"Mean: {fdf['RH2M'].mean():.1f}%")
        fig.update_layout(height=380, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        season_order = ['Winter','Pre-Monsoon','Monsoon','Post-Monsoon']
        season_colors = {'Winter':'#29b6f6','Pre-Monsoon':'#ffa726',
                         'Monsoon':'#26a69a','Post-Monsoon':'#ef5350'}
        s_wind = fdf.groupby('SEASON')['WS50M'].mean().reindex(season_order).reset_index()
        fig2 = px.bar(s_wind, x='SEASON', y='WS50M',
                      color='SEASON', color_discrete_map=season_colors,
                      title='Avg Wind Speed by Season (m/s)',
                      text='WS50M')
        fig2.update_traces(texttemplate='%{text:.2f}m/s', textposition='outside')
        fig2.update_layout(showlegend=False, height=380,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        month_labels = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                        7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        m_hum = fdf.groupby('MO')['RH2M'].mean().reset_index()
        m_hum['Month'] = m_hum['MO'].map(month_labels)
        fig3 = px.area(m_hum, x='Month', y='RH2M',
                       color_discrete_sequence=['#8e44ad'],
                       title='Monthly Relative Humidity (%)',
                       labels={'RH2M':'Humidity (%)'})
        fig3.update_layout(height=380, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        m_uv = fdf.groupby('MO')['ALLSKY_SFC_UV_INDEX'].mean().reset_index()
        m_uv['Month'] = m_uv['MO'].map(month_labels)
        fig4 = px.bar(m_uv, x='Month', y='ALLSKY_SFC_UV_INDEX',
                      color='ALLSKY_SFC_UV_INDEX', color_continuous_scale='YlOrRd',
                      title='Avg Monthly UV Index',
                      text='ALLSKY_SFC_UV_INDEX')
        fig4.update_traces(texttemplate='%{text:.1f}', textposition='outside', textfont_size=9)
        fig4.update_layout(coloraxis_showscale=False, height=380,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True)

# ─── TAB 7: EXTREME EVENTS ────────────────────────────────────────────
with t7:
    st.markdown('<div class="section-label">Extreme Weather Events (>64.5mm/day)</div>', unsafe_allow_html=True)

    extreme = fdf[fdf['PRECTOTCORR'] >= 64.5]

    c1, c2 = st.columns(2)
    with c1:
        ext_yr = extreme.groupby('YEAR').size().reset_index(name='Events')
        fig = px.bar(ext_yr, x='YEAR', y='Events',
                     color='Events', color_continuous_scale='Reds',
                     title='Extreme Rainfall Events by Year',
                     text='Events')
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(coloraxis_showscale=False, height=400,
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        month_labels_s = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                          7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        ext_mo = extreme.groupby('MO').size().reset_index(name='Events')
        ext_mo['Month'] = ext_mo['MO'].map(month_labels_s)
        fig2 = px.bar(ext_mo, x='Month', y='Events',
                      color='Events', color_continuous_scale='Reds',
                      title='Extreme Rainfall Events by Month', text='Events')
        fig2.update_traces(texttemplate='%{text}', textposition='outside')
        fig2.update_layout(coloraxis_showscale=False, height=400,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    # Top districts for extreme events
    ext_dist = extreme.groupby('DISTRICT').size().sort_values(ascending=False).head(20).reset_index(name='Events')
    fig3 = px.bar(ext_dist, x='Events', y='DISTRICT', orientation='h',
                  color='Events', color_continuous_scale='Reds',
                  title='Top 20 Districts — Extreme Rainfall Events',
                  text='Events')
    fig3.update_traces(texttemplate='%{text}', textposition='outside')
    fig3.update_layout(coloraxis_showscale=False, height=500,
                       plot_bgcolor='white', paper_bgcolor='white',
                       yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

    if len(extreme) > 0:
        st.markdown(f"**Total extreme events (>64.5mm) in filtered data: {len(extreme):,}**")
        st.dataframe(
            extreme[['YEAR','MO','DY','DISTRICT','PRECTOTCORR','T2M_MAX','RH2M','SEASON']]
            .sort_values('PRECTOTCORR', ascending=False).head(20)
            .rename(columns={'PRECTOTCORR':'Rainfall(mm)','T2M_MAX':'MaxTemp(°C)',
                             'RH2M':'Humidity(%)'}),
            use_container_width=True
        )

# ── RAW DATA ──────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 View Sample Data (500 rows)"):
    show_cols = ['YEAR','MO','DY','DISTRICT','PRECTOTCORR','T2M_MAX','T2M_MIN',
                 'RH2M','WS50M','SEASON','Rain_Category']
    st.dataframe(fdf[show_cols].head(500), use_container_width=True)
    csv = fdf[show_cols].head(5000).to_csv(index=False)
    st.download_button("⬇️ Download Sample CSV (5K rows)", data=csv,
                       file_name="UP_rainfall_filtered.csv", mime="text/csv")
