import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import json
import os

# Konfigurasi halaman
st.set_page_config(page_title="Trading Journal", layout="wide", initial_sidebar_state="collapsed")

# CSS Custom
st.markdown("""
<style>
    .main {
        background-color: #1e1e2e;
        color: #ffffff;
    }
    .stApp {
        background-color: #1e1e2e;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #ffffff;
    }
    div[data-testid="stMetricLabel"] {
        color: #a0a0b0;
    }
    .profit-card {
        background-color: #2d2d3d;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #2d2d3d;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0a0b0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #fbbf24 !important;
        border-bottom-color: #fbbf24 !important;
    }
</style>
""", unsafe_allow_html=True)

# File untuk menyimpan data
DATA_FILE = "trading_data.json"
PASSWORD = "000000"

# Fungsi untuk load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Fungsi untuk save data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Fungsi autentikasi
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Admin Login")
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if password == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Password salah!")
        st.stop()

# Fungsi untuk menghitung statistik
def calculate_statistics(data):
    if not data:
        return {
            "total_profit": 0,
            "total_loss": 0,
            "net_pnl": 0,
            "trading_volume": 0,
            "win_rate": 0,
            "winning_days": 0,
            "losing_days": 0,
            "breakeven_days": 0,
            "avg_profit": 0,
            "avg_loss": 0,
            "profit_loss_ratio": 0
        }
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Hitung daily PNL
    daily_pnl = df.groupby('date')['pnl'].sum().reset_index()
    
    profits = daily_pnl[daily_pnl['pnl'] > 0]['pnl']
    losses = daily_pnl[daily_pnl['pnl'] < 0]['pnl']
    
    total_profit = profits.sum() if len(profits) > 0 else 0
    total_loss = abs(losses.sum()) if len(losses) > 0 else 0
    
    winning_days = len(profits)
    losing_days = len(losses)
    breakeven_days = len(daily_pnl[daily_pnl['pnl'] == 0])
    
    total_days = len(daily_pnl)
    win_rate = (winning_days / total_days * 100) if total_days > 0 else 0
    
    avg_profit = profits.mean() if len(profits) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
    
    profit_loss_ratio = (avg_profit / avg_loss) if avg_loss > 0 else 0
    
    return {
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_pnl": total_profit - total_loss,
        "trading_volume": df['volume'].sum() if 'volume' in df.columns else 0,
        "win_rate": win_rate,
        "winning_days": winning_days,
        "losing_days": losing_days,
        "breakeven_days": breakeven_days,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "profit_loss_ratio": profit_loss_ratio
    }

# Fungsi untuk membuat calendar view
def create_calendar_view(data, year, month):
    df = pd.DataFrame(data)
    if len(df) == 0:
        return None
    
    df['date'] = pd.to_datetime(df['date'])
    daily_pnl = df.groupby('date')['pnl'].sum().reset_index()
    
    # Filter by year and month
    daily_pnl = daily_pnl[(daily_pnl['date'].dt.year == year) & 
                          (daily_pnl['date'].dt.month == month)]
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    
    fig = go.Figure()
    
    # Hari dalam seminggu
    days = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
    
    # Plot calendar grid
    for week_idx, week in enumerate(cal):
        for day_idx, day in enumerate(week):
            if day == 0:
                continue
            
            date = datetime(year, month, day)
            pnl_data = daily_pnl[daily_pnl['date'] == date]
            
            if len(pnl_data) > 0:
                pnl = pnl_data['pnl'].values[0]
                color = '#166534' if pnl > 0 else '#991b1b' if pnl < 0 else '#374151'
                text_color = '#10b981' if pnl > 0 else '#ef4444' if pnl < 0 else '#9ca3af'
                pnl_text = f"+{pnl:.2f}" if pnl > 0 else f"{pnl:.2f}"
            else:
                color = '#2d2d3d'
                text_color = '#ffffff'
                pnl_text = ""
            
            # Draw cell
            fig.add_shape(
                type="rect",
                x0=day_idx, y0=-week_idx,
                x1=day_idx + 0.9, y1=-week_idx - 0.9,
                fillcolor=color,
                line=dict(color="#1e1e2e", width=2)
            )
            
            # Add day number
            fig.add_annotation(
                x=day_idx + 0.15, y=-week_idx - 0.2,
                text=str(day),
                showarrow=False,
                font=dict(size=16, color="#ffffff"),
                xanchor="left",
                yanchor="top"
            )
            
            # Add PNL
            if pnl_text:
                fig.add_annotation(
                    x=day_idx + 0.45, y=-week_idx - 0.6,
                    text=pnl_text,
                    showarrow=False,
                    font=dict(size=12, color=text_color, family="monospace"),
                    xanchor="center"
                )
    
    # Add day headers
    for idx, day in enumerate(days):
        fig.add_annotation(
            x=idx + 0.45, y=0.5,
            text=day,
            showarrow=False,
            font=dict(size=14, color="#a0a0b0", weight="bold")
        )
    
    fig.update_xaxes(range=[-0.5, 7], showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(range=[-len(cal) - 0.5, 1], showgrid=False, zeroline=False, visible=False)
    
    fig.update_layout(
        height=500,
        plot_bgcolor='#1e1e2e',
        paper_bgcolor='#1e1e2e',
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    
    return fig

# Main App
def main():
    check_password()
    
    # Load data
    data = load_data()
    
    # Sidebar untuk navigasi
    st.sidebar.title("📊 Trading Journal")
    page = st.sidebar.radio("Navigation", ["Dashboard", "Entry Report", "Data Management"])
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    if page == "Dashboard":
        st.title("📈 Profit and Loss Analysis")
        
        # Calculate statistics
        stats = calculate_statistics(data)
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Profit", f"{stats['total_profit']:.2f} USD", 
                     delta=None, delta_color="off")
        with col2:
            st.metric("Total Loss", f"{stats['total_loss']:.2f} USD",
                     delta=None, delta_color="off")
        with col3:
            st.metric("Net Profit/Loss", f"{stats['net_pnl']:.2f} USD",
                     delta=None, delta_color="normal" if stats['net_pnl'] >= 0 else "inverse")
        with col4:
            st.metric("Trading Volume", f"{stats['trading_volume']:,.2f}",
                     delta=None, delta_color="off")
        
        st.divider()
        
        # Second row metrics
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Losing Days", f"{stats['losing_days']} Days")
        with col6:
            st.metric("Breakeven Days", f"{stats['breakeven_days']} Days")
        with col7:
            st.metric("Average Profit", f"{stats['avg_profit']:.2f} USD")
        with col8:
            st.metric("Average Loss", f"{stats['avg_loss']:.2f} USD")
        
        # Third row metrics
        col9, col10, col11 = st.columns(3)
        with col9:
            st.metric("Win Rate", f"{stats['win_rate']:.2f} %")
        with col10:
            st.metric("Winning Days", f"{stats['winning_days']} Days")
        with col11:
            st.metric("Profit/Loss Ratio", f"{stats['profit_loss_ratio']:.2f}")
        
        st.divider()
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Details", "Symbol Analysis", "Funding & Transaction"])
        
        with tab1:
            st.subheader("📅 Daily PNL")
            
            # Month/Year selector
            col_date1, col_date2 = st.columns([1, 3])
            with col_date1:
                current_year = datetime.now().year
                selected_year = st.selectbox("Year", range(current_year - 2, current_year + 2), 
                                            index=2, key="year_select")
            with col_date2:
                current_month = datetime.now().month
                selected_month = st.selectbox("Month", range(1, 13), 
                                             index=current_month - 1, 
                                             format_func=lambda x: calendar.month_name[x],
                                             key="month_select")
            
            # Create and display calendar
            if data:
                fig = create_calendar_view(data, selected_year, selected_month)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Tidak ada data untuk bulan ini")
            else:
                st.info("Belum ada data trading. Silakan tambahkan entry di halaman 'Entry Report'")
        
        with tab2:
            st.subheader("📋 Trading History")
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada data")
        
        with tab3:
            st.subheader("📊 Symbol Analysis")
            if data:
                df = pd.DataFrame(data)
                if 'symbol' in df.columns:
                    symbol_stats = df.groupby('symbol').agg({
                        'pnl': ['sum', 'mean', 'count']
                    }).round(2)
                    symbol_stats.columns = ['Total PNL', 'Avg PNL', 'Trades']
                    st.dataframe(symbol_stats, use_container_width=True)
                    
                    # Chart
                    fig = px.bar(symbol_stats.reset_index(), x='symbol', y='Total PNL',
                                color='Total PNL',
                                color_continuous_scale=['red', 'yellow', 'green'],
                                title="PNL by Symbol")
                    fig.update_layout(
                        plot_bgcolor='#1e1e2e',
                        paper_bgcolor='#1e1e2e',
                        font_color='#ffffff'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Belum ada data")
        
        with tab4:
            st.subheader("💰 Funding & Transaction Summary")
            if data:
                df = pd.DataFrame(data)
                if 'volume' in df.columns:
                    total_volume = df['volume'].sum()
                    st.metric("Total Trading Volume", f"{total_volume:,.2f} USD")
                    
                    # Volume over time
                    df['date'] = pd.to_datetime(df['date'])
                    daily_volume = df.groupby('date')['volume'].sum().reset_index()
                    
                    fig = px.line(daily_volume, x='date', y='volume',
                                 title="Daily Trading Volume")
                    fig.update_layout(
                        plot_bgcolor='#1e1e2e',
                        paper_bgcolor='#1e1e2e',
                        font_color='#ffffff'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Belum ada data")
    
    elif page == "Entry Report":
        st.title("📝 Daily Trading Report Entry")
        
        with st.form("entry_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                trade_date = st.date_input("Trading Date", datetime.now())
                symbol = st.text_input("Symbol/Pair", placeholder="e.g., BTC/USD, EUR/USD")
                entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01)
                exit_price = st.number_input("Exit Price", min_value=0.0, step=0.01)
            
            with col2:
                position = st.selectbox("Position", ["Long", "Short"])
                volume = st.number_input("Volume", min_value=0.0, step=0.01)
                pnl = st.number_input("P&L (USD)", step=0.01)
                notes = st.text_area("Notes", placeholder="Trading notes...")
            
            submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)
            
            if submitted:
                new_entry = {
                    "date": trade_date.strftime("%Y-%m-%d"),
                    "symbol": symbol,
                    "position": position,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "volume": volume,
                    "pnl": pnl,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
                
                data.append(new_entry)
                save_data(data)
                st.success("✅ Entry berhasil disimpan!")
                st.rerun()
    
    else:  # Data Management
        st.title("🗂️ Data Management")
        
        if data:
            st.subheader("All Entries")
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear All Data", type="secondary"):
                    if st.session_state.get('confirm_delete', False):
                        save_data([])
                        st.session_state.confirm_delete = False
                        st.success("Data berhasil dihapus!")
                        st.rerun()
                    else:
                        st.session_state.confirm_delete = True
                        st.warning("Klik sekali lagi untuk konfirmasi")
            
            with col2:
                # Export to CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"trading_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Belum ada data")

if __name__ == "__main__":
    main()
