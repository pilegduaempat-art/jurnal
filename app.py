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
FUTURES_FILE = "futures_data.json"
BALANCE_FILE = "balance_data.json"
HOLDINGS_FILE = "holdings_data.json"

# Load passwords from Streamlit secrets (production) or fallback (development)
try:
    ADMIN_PASSWORD = st.secrets["passwords"]["admin"]
    GUEST_PASSWORD = st.secrets["passwords"]["guest"]
except:
    # Fallback for local development
    ADMIN_PASSWORD = "000000"
    GUEST_PASSWORD = "123456"
    st.warning("⚠️ Using default passwords. Please configure secrets for production!")

# Fungsi untuk load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def load_futures_data():
    if os.path.exists(FUTURES_FILE):
        with open(FUTURES_FILE, 'r') as f:
            return json.load(f)
    return []

def load_balance_data():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('initial_balance', 0)
    return 0

# Fungsi untuk save data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_futures_data(data):
    with open(FUTURES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_balance_data(balance):
    with open(BALANCE_FILE, 'w') as f:
        json.dump({'initial_balance': balance}, f, indent=2)

# Fungsi autentikasi
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
    
    if not st.session_state.authenticated:
        st.title("🔐 Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Welcome to Trading Journal")
            st.info("👤 **Admin**: Full access (entry & view)\n\n👁️ **Guest**: View only")
            
            password = st.text_input("Enter Password", type="password", placeholder="")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔑 Login as Admin", use_container_width=True):
                    if password == ADMIN_PASSWORD:
                        st.session_state.authenticated = True
                        st.session_state.user_role = "admin"
                        st.success("✅ Admin login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid admin password!")
            
            with col_btn2:
                if st.button("👁️ Login as Guest", use_container_width=True):
                    if password == GUEST_PASSWORD:
                        st.session_state.authenticated = True
                        st.session_state.user_role = "guest"
                        st.success("✅ Guest login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid guest password!")
        st.stop()

# Fungsi untuk menghitung statistik
def calculate_statistics(data, futures_data):
    # Gabungkan data spot dan futures
    all_data = data.copy()
    
    if not all_data and not futures_data:
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
    
    # Tambahkan futures data ke dalam perhitungan
    df_list = []
    if all_data:
        df_spot = pd.DataFrame(all_data)
        df_spot['date'] = pd.to_datetime(df_spot['date'])
        df_list.append(df_spot)
    
    if futures_data:
        df_futures = pd.DataFrame(futures_data)
        df_futures['date'] = pd.to_datetime(df_futures['date'])
        df_list.append(df_futures)
    
    df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    
    if len(df) == 0:
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
def create_calendar_view(data, year, month, title="Calendar View"):
    if not data:
        return None
    
    df = pd.DataFrame(data)
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
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(size=18, color='#ffffff'),
            x=0.5,
            xanchor='center'
        )
    )
    
    return fig

# Main App
def main():
    check_password()
    
    # Load data
    data = load_data()
    futures_data = load_futures_data()
    initial_balance = load_balance_data()
    
    # Sidebar untuk navigasi
    st.sidebar.title("📊 Portofolio - Overview PNL")
    
    # Show user role
    if st.session_state.user_role == "admin":
        st.sidebar.success("👤 Logged in as: **Admin**")
        page_options = ["Dashboard", "Entry Report - Spot", "Entry Report - Futures", "Entry Balance", "Data Management"]
    else:
        st.sidebar.info("👁️ Logged in as: **Guest** (View Only)")
        page_options = ["Dashboard"]
    
    page = st.sidebar.radio("Navigation", page_options)
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()
    
    if page == "Dashboard":
        st.title("📈 Portfolio - Overview PNL")
        
        # Calculate statistics
        stats = calculate_statistics(data, futures_data)
        
        # Calculate portfolio value
        current_portfolio = initial_balance + stats['net_pnl']
        portfolio_change_pct = ((stats['net_pnl'] / initial_balance) * 100) if initial_balance > 0 else 0
        
        # Top metrics - Row 1
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Initial Balance", f"{initial_balance:,.2f} USD")
        with col2:
            st.metric("Total Profit", f"{stats['total_profit']:.2f} USD", 
                     delta=None, delta_color="off")
        with col3:
            st.metric("Total Loss", f"{stats['total_loss']:.2f} USD",
                     delta=None, delta_color="off")
        with col4:
            st.metric("Net Profit/Loss", f"{stats['net_pnl']:.2f} USD",
                     delta=f"{portfolio_change_pct:+.2f}%", 
                     delta_color="normal" if stats['net_pnl'] >= 0 else "inverse")
        with col5:
            st.metric("Current Portfolio", f"{current_portfolio:,.2f} USD",
                     delta=f"{stats['net_pnl']:+,.2f}",
                     delta_color="normal" if stats['net_pnl'] >= 0 else "inverse")
        
        st.divider()
        
        # Second row metrics
        col5, col6, col7, col8, col9 = st.columns(5)
        with col5:
            st.metric("Trading Volume", f"{stats['trading_volume']:,.2f}")
        with col6:
            st.metric("Losing Days", f"{stats['losing_days']} Days")
        with col7:
            st.metric("Breakeven Days", f"{stats['breakeven_days']} Days")
        with col8:
            st.metric("Average Profit", f"{stats['avg_profit']:.2f} USD")
        with col9:
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
            
            # Tabel Futures (di atas)
            st.markdown("### 📊 Daily PNL (Futures)")
            if futures_data:
                df_futures = pd.DataFrame(futures_data)
                df_futures['date'] = pd.to_datetime(df_futures['date'])
                
                # Filter by selected month and year
                df_futures_filtered = df_futures[
                    (df_futures['date'].dt.year == selected_year) & 
                    (df_futures['date'].dt.month == selected_month)
                ].copy()
                
                if len(df_futures_filtered) > 0:
                    # Format display
                    df_futures_display = df_futures_filtered.copy()
                    df_futures_display['date'] = df_futures_display['date'].dt.strftime('%Y-%m-%d')
                    df_futures_display['pnl'] = df_futures_display['pnl'].apply(lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}")
                    
                    # Reorder columns
                    display_cols = ['date', 'pnl', 'notes']
                    df_futures_display = df_futures_display[display_cols]
                    df_futures_display.columns = ['Trading Date', 'P&L (USD)', 'Notes']
                    
                    st.dataframe(df_futures_display, use_container_width=True, hide_index=True)
                    
                    # Summary
                    total_futures_pnl = df_futures_filtered['pnl'].sum()
                    st.metric("Total Futures P&L", f"{total_futures_pnl:.2f} USD", 
                             delta=None, 
                             delta_color="normal" if total_futures_pnl >= 0 else "inverse")
                else:
                    st.info("Tidak ada data futures untuk bulan ini")
            else:
                st.info("Belum ada data futures. Silakan tambahkan entry di 'Entry Report - Futures'")
            
            st.divider()
            
            # Calendar View - Futures
            st.markdown("### 📅 Calendar View - Futures Trading")
            if futures_data:
                fig_futures = create_calendar_view(futures_data, selected_year, selected_month, "Futures Trading Calendar")
                if fig_futures:
                    st.plotly_chart(fig_futures, use_container_width=True)
                else:
                    st.info("Tidak ada data futures untuk bulan ini")
            else:
                st.info("Belum ada data futures")
            
            st.divider()
            
            # Calendar View - Spot
            st.markdown("### 📅 Calendar View - Spot Trading")
            if data:
                fig_spot = create_calendar_view(data, selected_year, selected_month, "Spot Trading Calendar")
                if fig_spot:
                    st.plotly_chart(fig_spot, use_container_width=True)
                else:
                    st.info("Tidak ada data spot untuk bulan ini")
            else:
                st.info("Belum ada data spot")
        
        with tab2:
            st.subheader("📋 Trading History")
            
            # Futures History
            st.markdown("#### Futures Trading")
            if futures_data:
                df_futures = pd.DataFrame(futures_data)
                df_futures['date'] = pd.to_datetime(df_futures['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(df_futures, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada data futures")
            
            st.divider()
            
            # Spot History
            st.markdown("#### Spot Trading")
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada data spot")
        
        with tab3:
            st.subheader("📊 Symbol Analysis")
            
            # Combine data
            all_data = []
            if data:
                df_spot = pd.DataFrame(data)
                df_spot['type'] = 'Spot'
                all_data.append(df_spot)
            if futures_data:
                df_futures = pd.DataFrame(futures_data)
                if 'symbol' not in df_futures.columns:
                    df_futures['symbol'] = 'Futures'
                df_futures['type'] = 'Futures'
                all_data.append(df_futures)
            
            if all_data:
                df_combined = pd.concat(all_data, ignore_index=True)
                
                if 'symbol' in df_combined.columns:
                    symbol_stats = df_combined.groupby('symbol').agg({
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
            
            # Combine data
            all_data = []
            if data:
                df_spot = pd.DataFrame(data)
                all_data.append(df_spot)
            if futures_data:
                df_futures = pd.DataFrame(futures_data)
                if 'volume' in df_futures.columns:
                    all_data.append(df_futures)
            
            if all_data:
                df_combined = pd.concat(all_data, ignore_index=True)
                
                if 'volume' in df_combined.columns:
                    total_volume = df_combined['volume'].sum()
                    st.metric("Total Trading Volume", f"{total_volume:,.2f} USD")
                    
                    # Volume over time
                    df_combined['date'] = pd.to_datetime(df_combined['date'])
                    daily_volume = df_combined.groupby('date')['volume'].sum().reset_index()
                    
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
    
    elif page == "Entry Report - Spot":
        # Check if user is admin
        if st.session_state.user_role != "admin":
            st.error("🚫 Access Denied. Admin only.")
            st.stop()
        
        st.title("📝 Daily Trading Report Entry (Spot)")
        
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
    
    elif page == "Entry Report - Futures":
        # Check if user is admin
        if st.session_state.user_role != "admin":
            st.error("🚫 Access Denied. Admin only.")
            st.stop()
        
        st.title("📝 Daily Trading Report Entry (Futures)")
        
        with st.form("futures_entry_form"):
            trade_date = st.date_input("Trading Date", datetime.now())
            pnl = st.number_input("P&L (USD)", step=0.01)
            notes = st.text_area("Notes", placeholder="Trading notes for futures...")
            
            submitted = st.form_submit_button("💾 Save Futures Entry", use_container_width=True)
            
            if submitted:
                new_entry = {
                    "date": trade_date.strftime("%Y-%m-%d"),
                    "pnl": pnl,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
                
                futures_data.append(new_entry)
                save_futures_data(futures_data)
                st.success("✅ Futures entry berhasil disimpan!")
                st.rerun()
    
    elif page == "Entry Balance":
        # Check if user is admin
        if st.session_state.user_role != "admin":
            st.error("🚫 Access Denied. Admin only.")
            st.stop()
        
        st.title("💰 Entry Initial Balance")
        
        # Show current balance
        current_balance = load_balance_data()
        
        if current_balance > 0:
            st.info(f"📊 Current Initial Balance: **${current_balance:,.2f} USD**")
        else:
            st.warning("⚠️ No initial balance set. Please enter your starting capital.")
        
        st.divider()
        
        with st.form("balance_form"):
            st.markdown("### Set Initial Balance")
            st.caption("This is your starting capital before any trading activity.")
            
            new_balance = st.number_input(
                "Initial Balance (USD)", 
                min_value=0.0, 
                value=float(current_balance),
                step=100.0,
                help="Enter your starting capital amount"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("💡 **Tip**: Set this to your account balance before you started trading. Portfolio value will be calculated as: Initial Balance + Net P&L")
            
            submitted = st.form_submit_button("💾 Save Balance", use_container_width=True, type="primary")
            
            if submitted:
                save_balance_data(new_balance)
                st.success(f"✅ Initial balance updated to ${new_balance:,.2f} USD")
                st.balloons()
                st.rerun()
        
        st.divider()
        
        # Show portfolio calculation preview
        st.markdown("### 📈 Portfolio Value Preview")
        stats = calculate_statistics(data, futures_data)
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        with preview_col1:
            st.metric("Initial Balance", f"${new_balance:,.2f}")
        with preview_col2:
            st.metric("Net P&L", f"${stats['net_pnl']:,.2f}", 
                     delta_color="normal" if stats['net_pnl'] >= 0 else "inverse")
        with preview_col3:
            portfolio_value = new_balance + stats['net_pnl']
            change_pct = ((stats['net_pnl'] / new_balance) * 100) if new_balance > 0 else 0
            st.metric("Portfolio Value", f"${portfolio_value:,.2f}", 
                     delta=f"{change_pct:+.2f}%",
                     delta_color="normal" if stats['net_pnl'] >= 0 else "inverse")
    
    else:  # Data Management
        # Check if user is admin
        if st.session_state.user_role != "admin":
            st.error("🚫 Access Denied. Admin only.")
            st.stop()
        
        st.title("🗂️ Data Management")
        
        # Balance Data
        st.subheader("💰 Balance Data")
        initial_balance = load_balance_data()
        if initial_balance > 0:
            st.info(f"Current Initial Balance: **${initial_balance:,.2f} USD**")
            if st.button("🗑️ Reset Balance", type="secondary", key="reset_balance"):
                if st.session_state.get('confirm_reset_balance', False):
                    save_balance_data(0)
                    st.session_state.confirm_reset_balance = False
                    st.success("Balance berhasil direset!")
                    st.rerun()
                else:
                    st.session_state.confirm_reset_balance = True
                    st.warning("Klik sekali lagi untuk konfirmasi")
        else:
            st.info("Balance belum diset. Kunjungi halaman 'Entry Balance'")
        
        st.divider()
        
        # Futures Data Management
        st.subheader("Futures Data")
        if futures_data:
            df_futures = pd.DataFrame(futures_data)
            st.dataframe(df_futures, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Futures Data", type="secondary", key="clear_futures"):
                    if st.session_state.get('confirm_delete_futures', False):
                        save_futures_data([])
                        st.session_state.confirm_delete_futures = False
                        st.success("Futures data berhasil dihapus!")
                        st.rerun()
                    else:
                        st.session_state.confirm_delete_futures = True
                        st.warning("Klik sekali lagi untuk konfirmasi")
            
            with col2:
                csv_futures = df_futures.to_csv(index=False)
                st.download_button(
                    label="📥 Download Futures CSV",
                    data=csv_futures,
                    file_name=f"futures_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Belum ada data futures")
        
        st.divider()
        
        # Spot Data Management
        st.subheader("Spot Data")
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Spot Data", type="secondary", key="clear_spot"):
                    if st.session_state.get('confirm_delete_spot', False):
                        save_data([])
                        st.session_state.confirm_delete_spot = False
                        st.success("Spot data berhasil dihapus!")
                        st.rerun()
                    else:
                        st.session_state.confirm_delete_spot = True
                        st.warning("Klik sekali lagi untuk konfirmasi")
            
            with col2:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Spot CSV",
                    data=csv,
                    file_name=f"spot_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("Belum ada data spot")

if __name__ == "__main__":
    main()
