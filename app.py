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
    .portfolio-preview-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .portfolio-preview-card div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    .portfolio-preview-card div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #f0f0f0 !important;
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

def load_holdings_data():
    if os.path.exists(HOLDINGS_FILE):
        with open(HOLDINGS_FILE, 'r') as f:
            return json.load(f)
    return []

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

def save_holdings_data(data):
    with open(HOLDINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Fungsi autentikasi
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.login_page = "select"  # select, admin, guest
    
    if not st.session_state.authenticated:
        # Landing page - pilih role
        if st.session_state.login_page == "select":
            st.title("🔐 Ruastatement Login")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("### Welcome to Ruastatement")
                st.markdown("---")
                
                st.markdown("#### 👤 Login as Admin")
                st.info("✅ Full access to all features\n\n✅ Add/Edit/Delete entries\n\n✅ Manage portfolio & holdings\n\n✅ View all analytics")
                if st.button("🔑 Continue as Admin", use_container_width=True, type="primary"):
                    st.session_state.login_page = "admin"
                    st.rerun()
                
                st.markdown("---")
                
                st.markdown("#### 👁️ Login as Guest")
                st.info("📊 View-only access\n\n📈 See dashboard & analytics\n\n🔒 Cannot modify data")
                if st.button("👁️ Continue as Guest", use_container_width=True):
                    st.session_state.login_page = "guest"
                    st.rerun()
        
        # Admin login page
        elif st.session_state.login_page == "admin":
            st.title("🔑 Admin Login")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("### Administrator Access")
                st.warning("⚠️ This area is for authorized administrators only")
                
                password = st.text_input("Admin Password", type="password", placeholder="Enter admin password", key="admin_pass")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔓 Login", use_container_width=True, type="primary"):
                        if password == ADMIN_PASSWORD:
                            st.session_state.authenticated = True
                            st.session_state.user_role = "admin"
                            st.success("✅ Admin login successful!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid admin password!")
                
                with col_btn2:
                    if st.button("⬅️ Back", use_container_width=True):
                        st.session_state.login_page = "select"
                        st.rerun()
        
        # Guest login page
        elif st.session_state.login_page == "guest":
            st.title("👁️ Guest Login")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("### Guest Access")
                st.info("💡 Guest users have read-only access to view trading analytics and performance")
                
                password = st.text_input("Guest Password", type="password", placeholder="Enter guest password", key="guest_pass")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔓 Login", use_container_width=True, type="primary"):
                        if password == GUEST_PASSWORD:
                            st.session_state.authenticated = True
                            st.session_state.user_role = "guest"
                            st.success("✅ Guest login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid guest password!")
                
                with col_btn2:
                    if st.button("⬅️ Back", use_container_width=True):
                        st.session_state.login_page = "select"
                        st.rerun()
        
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
    holdings_data = load_holdings_data()
    
    # Sidebar untuk navigasi
    st.sidebar.title("📊 Trading Journal")
    
    # Show user role
    if st.session_state.user_role == "admin":
        st.sidebar.success("👤 Logged in as: **Admin**")
        page_options = ["Dashboard", "Entry Report - Spot", "Entry Report - Futures", "Holdings (Floating)", "Entry Balance", "Data Management"]
    else:
        st.sidebar.info("👁️ Logged in as: **Guest** (View Only)")
        page_options = ["Dashboard"]
    
    page = st.sidebar.radio("Navigation", page_options)
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()
    
    if page == "Dashboard":
        # Calculate statistics FIRST
        stats = calculate_statistics(data, futures_data)
        
        # Calculate total unrealized P&L from holdings
        total_unrealized_pnl = 0
        if holdings_data:
            for holding in holdings_data:
                if holding.get('status') == 'open':
                    total_unrealized_pnl += holding.get('unrealized_pnl', 0)
        
        # Calculate portfolio value
        realized_pnl = stats['net_pnl']
        total_pnl = realized_pnl + total_unrealized_pnl
        current_portfolio = initial_balance + total_pnl
        portfolio_change_pct = ((total_pnl / initial_balance) * 100) if initial_balance > 0 else 0
        
        # PORTFOLIO VALUE PREVIEW - MOVED TO TOP
        st.markdown('<div class="portfolio-preview-card">', unsafe_allow_html=True)
        st.markdown("# 💎 Portfolio Value Overview")
        
        preview_col1, preview_col2, preview_col3, preview_col4 = st.columns(4)
        with preview_col1:
            st.metric("💰 Initial Balance", f"${initial_balance:,.2f}")
        with preview_col2:
            st.metric("📊 Realized P&L", f"${realized_pnl:,.2f}", 
                     delta_color="normal" if realized_pnl >= 0 else "inverse")
        with preview_col3:
            st.metric("📈 Unrealized P&L", f"${total_unrealized_pnl:,.2f}",
                     delta_color="normal" if total_unrealized_pnl >= 0 else "inverse")
        with preview_col4:
            st.metric("💼 Portfolio Value", f"${current_portfolio:,.2f}", 
                     delta=f"{portfolio_change_pct:+.2f}%",
                     delta_color="normal" if total_pnl >= 0 else "inverse")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # PORTFOLIO HISTORY CHART - NEW
        st.subheader("📈 Portfolio Performance History")
        
        # Combine all data for portfolio history
        portfolio_history = []
        
        # Get all dates from spot and futures
        all_dates = set()
        if data:
            df_spot = pd.DataFrame(data)
            df_spot['date'] = pd.to_datetime(df_spot['date'])
            all_dates.update(df_spot['date'].dt.date.tolist())
        
        if futures_data:
            df_futures = pd.DataFrame(futures_data)
            df_futures['date'] = pd.to_datetime(df_futures['date'])
            all_dates.update(df_futures['date'].dt.date.tolist())
        
        if all_dates:
            # Sort dates
            sorted_dates = sorted(list(all_dates))
            
            # Calculate cumulative portfolio value
            cumulative_pnl = 0
            for date in sorted_dates:
                date_dt = pd.Timestamp(date)
                
                # Get PNL for this date from spot
                if data:
                    df_spot = pd.DataFrame(data)
                    df_spot['date'] = pd.to_datetime(df_spot['date'])
                    spot_pnl = df_spot[df_spot['date'].dt.date == date]['pnl'].sum()
                else:
                    spot_pnl = 0
                
                # Get PNL for this date from futures
                if futures_data:
                    df_futures = pd.DataFrame(futures_data)
                    df_futures['date'] = pd.to_datetime(df_futures['date'])
                    futures_pnl = df_futures[df_futures['date'].dt.date == date]['pnl'].sum()
                else:
                    futures_pnl = 0
                
                daily_pnl = spot_pnl + futures_pnl
                cumulative_pnl += daily_pnl
                
                portfolio_history.append({
                    'date': date,
                    'daily_pnl': daily_pnl,
                    'cumulative_pnl': cumulative_pnl,
                    'portfolio_value': initial_balance + cumulative_pnl
                })
            
            # Create DataFrame
            df_portfolio = pd.DataFrame(portfolio_history)
            
            # Create line chart
            fig_portfolio = go.Figure()
            
            # Add portfolio value line
            fig_portfolio.add_trace(go.Scatter(
                x=df_portfolio['date'],
                y=df_portfolio['portfolio_value'],
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#10b981', width=3),
                marker=dict(size=6),
                fill='tonexty',
                fillcolor='rgba(16, 185, 129, 0.1)'
            ))
            
            # Add initial balance reference line
            fig_portfolio.add_hline(
                y=initial_balance,
                line_dash="dash",
                line_color="#fbbf24",
                annotation_text=f"Initial Balance: ${initial_balance:,.2f}",
                annotation_position="right"
            )
            
            fig_portfolio.update_layout(
                title="Daily Portfolio Value",
                xaxis_title="Date",
                yaxis_title="Portfolio Value (USD)",
                plot_bgcolor='#1e1e2e',
                paper_bgcolor='#1e1e2e',
                font_color='#ffffff',
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_portfolio, use_container_width=True)
            
            # Show stats
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                max_portfolio = df_portfolio['portfolio_value'].max()
                st.metric("Peak Portfolio", f"${max_portfolio:,.2f}")
            with col_stat2:
                min_portfolio = df_portfolio['portfolio_value'].min()
                st.metric("Lowest Portfolio", f"${min_portfolio:,.2f}")
            with col_stat3:
                best_day = df_portfolio.loc[df_portfolio['daily_pnl'].idxmax()]
                st.metric("Best Day", f"+${best_day['daily_pnl']:,.2f}", 
                         delta=best_day['date'].strftime('%Y-%m-%d'))
            with col_stat4:
                worst_day = df_portfolio.loc[df_portfolio['daily_pnl'].idxmin()]
                st.metric("Worst Day", f"${worst_day['daily_pnl']:,.2f}",
                         delta=worst_day['date'].strftime('%Y-%m-%d'))
        else:
            st.info("📊 Belum ada data trading untuk menampilkan history portfolio")
        
        st.divider()
        
        # NOW SHOW MAIN TITLE
        st.title("📈 Profit and Loss Analysis")
        
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
            st.metric("Realized P&L", f"{realized_pnl:.2f} USD",
                     delta=None, 
                     delta_color="normal" if realized_pnl >= 0 else "inverse")
        with col5:
            st.metric("Unrealized P&L", f"{total_unrealized_pnl:.2f} USD",
                     delta=None,
                     delta_color="normal" if total_unrealized_pnl >= 0 else "inverse")
        
        st.divider()
        
        # Holdings Data Management
        st.subheader("📊 Holdings Data")
        if holdings_data:
            open_pos = len([h for h in holdings_data if h.get('status') == 'open'])
            closed_pos = len([h for h in holdings_data if h.get('status') == 'closed'])
            st.info(f"Open Positions: **{open_pos}** | Closed Positions: **{closed_pos}**")
            
            df_holdings = pd.DataFrame(holdings_data)
            st.dataframe(df_holdings, use_container_width=True, hide_index=True)
            
            # Admin only buttons
            if st.session_state.user_role == "admin":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Clear Holdings Data", type="secondary", key="clear_holdings"):
                        if st.session_state.get('confirm_delete_holdings', False):
                            save_holdings_data([])
                            st.session_state.confirm_delete_holdings = False
                            st.success("Holdings data berhasil dihapus!")
                            st.rerun()
                        else:
                            st.session_state.confirm_delete_holdings = True
                            st.warning("Klik sekali lagi untuk konfirmasi")
                
                with col2:
                    csv_holdings = df_holdings.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Holdings CSV",
                        data=csv_holdings,
                        file_name=f"holdings_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("Belum ada data holdings")
        
        st.divider()
        
        # Second row metrics
        col5, col6, col7, col8, col9 = st.columns(5)
        with col5:
            st.metric("Trading Volume", f"{stats['trading_volume']:,.2f}")
        with col6:
            st.metric("Worst Trade", f"{stats['losing_days']} Days")
        with col7:
            st.metric("Breakeven Days", f"{stats['breakeven_days']} Days")
        with col8:
            st.metric("Average Profit", f"{stats['avg_profit']:.2f} USD")
        with col9:
            st.metric("Average Loss", f"{stats['avg_loss']:.2f} USD")
        
        # Third row metrics
        col9, col10, col11 = st.columns(3)
        with col9:
            st.metric("PNL Rate", f"{stats['win_rate']:.2f} %")
        with col10:
            st.metric("Best Trade", f"{stats['winning_days']} Days")
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
            
            # CHART SECTION - NEW
            st.markdown("### 📈 Performance Charts")
            
            # Create tabs for different charts
            chart_tab1, chart_tab2, chart_tab3 = st.tabs(["💹 Futures P&L", "💰 Spot P&L", "📊 Floating P&L"])
            
            with chart_tab1:
                st.markdown("#### Futures Trading Performance")
                if futures_data:
                    df_futures_chart = pd.DataFrame(futures_data)
                    df_futures_chart['date'] = pd.to_datetime(df_futures_chart['date'])
                    df_futures_chart = df_futures_chart.sort_values('date')
                    
                    # Calculate cumulative
                    df_futures_chart['cumulative_pnl'] = df_futures_chart['pnl'].cumsum()
                    
                    # Create chart
                    fig_futures = go.Figure()
                    
                    # Daily P&L bars
                    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_futures_chart['pnl']]
                    fig_futures.add_trace(go.Bar(
                        x=df_futures_chart['date'],
                        y=df_futures_chart['pnl'],
                        name='Daily P&L',
                        marker_color=colors,
                        yaxis='y'
                    ))
                    
                    # Cumulative P&L line
                    fig_futures.add_trace(go.Scatter(
                        x=df_futures_chart['date'],
                        y=df_futures_chart['cumulative_pnl'],
                        name='Cumulative P&L',
                        line=dict(color='#fbbf24', width=3),
                        yaxis='y2'
                    ))
                    
                    fig_futures.update_layout(
                        title="Futures: Daily & Cumulative P&L",
                        xaxis_title="Date",
                        yaxis=dict(title="Daily P&L (USD)", side='left'),
                        yaxis2=dict(title="Cumulative P&L (USD)", side='right', overlaying='y'),
                        plot_bgcolor='#1e1e2e',
                        paper_bgcolor='#1e1e2e',
                        font_color='#ffffff',
                        hovermode='x unified',
                        height=400,
                        legend=dict(x=0.01, y=0.99)
                    )
                    
                    st.plotly_chart(fig_futures, use_container_width=True)
                    
                    # Stats
                    col_f1, col_f2, col_f3 = st.columns(3)
                    with col_f1:
                        total_futures = df_futures_chart['pnl'].sum()
                        st.metric("Total Futures P&L", f"${total_futures:,.2f}")
                    with col_f2:
                        avg_futures = df_futures_chart['pnl'].mean()
                        st.metric("Average Daily P&L", f"${avg_futures:,.2f}")
                    with col_f3:
                        win_rate_futures = (df_futures_chart['pnl'] > 0).sum() / len(df_futures_chart) * 100
                        st.metric("PNL Rate", f"{win_rate_futures:.1f}%")
                else:
                    st.info("Belum ada data futures untuk ditampilkan")
            
            with chart_tab2:
                st.markdown("#### Spot Trading Performance")
                if data:
                    df_spot_chart = pd.DataFrame(data)
                    df_spot_chart['date'] = pd.to_datetime(df_spot_chart['date'])
                    
                    # Group by date
                    df_spot_daily = df_spot_chart.groupby('date')['pnl'].sum().reset_index()
                    df_spot_daily = df_spot_daily.sort_values('date')
                    
                    # Calculate cumulative
                    df_spot_daily['cumulative_pnl'] = df_spot_daily['pnl'].cumsum()
                    
                    # Create chart
                    fig_spot = go.Figure()
                    
                    # Daily P&L bars
                    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_spot_daily['pnl']]
                    fig_spot.add_trace(go.Bar(
                        x=df_spot_daily['date'],
                        y=df_spot_daily['pnl'],
                        name='Daily P&L',
                        marker_color=colors,
                        yaxis='y'
                    ))
                    
                    # Cumulative P&L line
                    fig_spot.add_trace(go.Scatter(
                        x=df_spot_daily['date'],
                        y=df_spot_daily['cumulative_pnl'],
                        name='Cumulative P&L',
                        line=dict(color='#fbbf24', width=3),
                        yaxis='y2'
                    ))
                    
                    fig_spot.update_layout(
                        title="Spot: Daily & Cumulative P&L",
                        xaxis_title="Date",
                        yaxis=dict(title="Daily P&L (USD)", side='left'),
                        yaxis2=dict(title="Cumulative P&L (USD)", side='right', overlaying='y'),
                        plot_bgcolor='#1e1e2e',
                        paper_bgcolor='#1e1e2e',
                        font_color='#ffffff',
                        hovermode='x unified',
                        height=400,
                        legend=dict(x=0.01, y=0.99)
                    )
                    
                    st.plotly_chart(fig_spot, use_container_width=True)
                    
                    # Stats
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        total_spot = df_spot_daily['pnl'].sum()
                        st.metric("Total Spot P&L", f"${total_spot:,.2f}")
                    with col_s2:
                        avg_spot = df_spot_daily['pnl'].mean()
                        st.metric("Average Daily P&L", f"${avg_spot:,.2f}")
                    with col_s3:
                        win_rate_spot = (df_spot_daily['pnl'] > 0).sum() / len(df_spot_daily) * 100
                        st.metric("PNL Rate", f"{win_rate_spot:.1f}%")
                else:
                    st.info("Belum ada data spot untuk ditampilkan")
            
            with chart_tab3:
                st.markdown("#### Floating Positions Performance")
                if holdings_data:
                    open_holdings = [h for h in holdings_data if h.get('status') == 'open']
                    if open_holdings:
                        df_float = pd.DataFrame(open_holdings)
                        
                        # Create chart - P&L by symbol
                        fig_float = go.Figure()
                        
                        colors = ['#10b981' if x > 0 else '#ef4444' for x in df_float['unrealized_pnl']]
                        fig_float.add_trace(go.Bar(
                            x=df_float['symbol'],
                            y=df_float['unrealized_pnl'],
                            name='Unrealized P&L',
                            marker_color=colors,
                            text=df_float['unrealized_pnl'].apply(lambda x: f"${x:,.2f}"),
                            textposition='outside'
                        ))
                        
                        fig_float.update_layout(
                            title="Floating: Unrealized P&L by Symbol",
                            xaxis_title="Symbol",
                            yaxis_title="Unrealized P&L (USD)",
                            plot_bgcolor='#1e1e2e',
                            paper_bgcolor='#1e1e2e',
                            font_color='#ffffff',
                            height=400
                        )
                        
                        st.plotly_chart(fig_float, use_container_width=True)
                        
                        # Stats
                        col_fl1, col_fl2, col_fl3 = st.columns(3)
                        with col_fl1:
                            total_float = df_float['unrealized_pnl'].sum()
                            st.metric("Total Unrealized P&L", f"${total_float:,.2f}")
                        with col_fl2:
                            profitable = (df_float['unrealized_pnl'] > 0).sum()
                            st.metric("Profitable Positions", f"{profitable}/{len(df_float)}")
                        with col_fl3:
                            total_value = (df_float['quantity'] * df_float['current_price']).sum()
                            st.metric("Total Holdings Value", f"${total_value:,.2f}")
                    else:
                        st.info("Tidak ada posisi floating terbuka")
                else:
                    st.info("Belum ada data holdings untuk ditampilkan")
            
            st.divider()
            
            # EXISTING TABLES SECTION
            st.markdown("### 📊 Detailed Data Tables")
            
            # Holdings/Open Positions
            st.markdown("#### 📊 Open Positions (Floating)")
            if holdings_data:
                open_holdings = [h for h in holdings_data if h.get('status') == 'open']
                if open_holdings:
                    df_holdings = pd.DataFrame(open_holdings)
                    # Format display
                    display_cols = ['symbol', 'quantity', 'entry_price', 'current_price', 'unrealized_pnl', 'entry_date']
                    df_holdings_display = df_holdings[display_cols].copy()
                    df_holdings_display.columns = ['Symbol', 'Quantity', 'Entry Price', 'Current Price', 'Unrealized P&L', 'Entry Date']
                    st.dataframe(df_holdings_display, use_container_width=True, hide_index=True)
                    
                    # Summary
                    total_value = df_holdings['quantity'].sum() * df_holdings['current_price'].mean()
                    st.metric("Total Holdings Value", f"${total_value:,.2f} USD")
                else:
                    st.info("Tidak ada posisi terbuka")
            else:
                st.info("Belum ada data holdings")
            
            st.divider()
            
            # Futures History
            st.markdown("#### Futures Trading")
            if futures_data:
                df_futures = pd.DataFrame(futures_data)
                df_futures['date'] = pd.to_datetime(df_futures['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(df_futures, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada data futures")
            
            st.divider()
            
            # Spot History (Closed Trades)
            st.markdown("#### Spot Trading (Closed)")
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
    
    elif page == "Holdings (Floating)":
        # Check if user is admin
        if st.session_state.user_role != "admin":
            st.error("🚫 Access Denied. Admin only.")
            st.stop()
        
        st.title("📊 Holdings Management (Floating Positions)")
        
        # Tabs for Add and View
        tab1, tab2 = st.tabs(["➕ Add New Position", "📋 Manage Positions"])
        
        with tab1:
            st.markdown("### Add New Holding Position")
            
            with st.form("holdings_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    symbol = st.text_input("Symbol/Pair", placeholder="e.g., BTC, ETH, BNB")
                    quantity = st.number_input("Quantity", min_value=0.0, step=0.01)
                    entry_price = st.number_input("Entry Price (USD)", min_value=0.0, step=0.01)
                    entry_date = st.date_input("Entry Date", datetime.now())
                
                with col2:
                    current_price = st.number_input("Current Price (USD)", min_value=0.0, step=0.01)
                    notes = st.text_area("Notes", placeholder="Optional notes about this position...")
                
                # Calculate unrealized P&L
                if quantity > 0 and entry_price > 0 and current_price > 0:
                    cost_basis = quantity * entry_price
                    current_value = quantity * current_price
                    unrealized_pnl = current_value - cost_basis
                    pnl_percent = ((current_price - entry_price) / entry_price) * 100
                    
                    st.divider()
                    st.markdown("#### 💹 Position Summary")
                    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                    with col_sum1:
                        st.metric("Cost Basis", f"${cost_basis:,.2f}")
                    with col_sum2:
                        st.metric("Current Value", f"${current_value:,.2f}")
                    with col_sum3:
                        st.metric("Unrealized P&L", f"${unrealized_pnl:,.2f}",
                                 delta=f"{pnl_percent:+.2f}%",
                                 delta_color="normal" if unrealized_pnl >= 0 else "inverse")
                    with col_sum4:
                        st.metric("Break Even Price", f"${entry_price:.2f}")
                else:
                    unrealized_pnl = 0
                
                submitted = st.form_submit_button("💾 Add Position", use_container_width=True)
                
                if submitted and symbol and quantity > 0 and entry_price > 0:
                    new_holding = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "symbol": symbol,
                        "quantity": quantity,
                        "entry_price": entry_price,
                        "current_price": current_price,
                        "entry_date": entry_date.strftime("%Y-%m-%d"),
                        "unrealized_pnl": unrealized_pnl,
                        "status": "open",
                        "notes": notes,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    holdings_data.append(new_holding)
                    save_holdings_data(holdings_data)
                    st.success("✅ Position berhasil ditambahkan!")
                    st.rerun()
        
        with tab2:
            st.markdown("### Current Holdings")
            
            if holdings_data:
                open_holdings = [h for h in holdings_data if h.get('status') == 'open']
                
                if open_holdings:
                    # Summary cards
                    total_cost = sum(h['quantity'] * h['entry_price'] for h in open_holdings)
                    total_current = sum(h['quantity'] * h['current_price'] for h in open_holdings)
                    total_unrealized = total_current - total_cost
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Cost Basis", f"${total_cost:,.2f}")
                    with col2:
                        st.metric("Total Current Value", f"${total_current:,.2f}")
                    with col3:
                        st.metric("Total Unrealized P&L", f"${total_unrealized:,.2f}",
                                 delta_color="normal" if total_unrealized >= 0 else "inverse")
                    
                    st.divider()
                    
                    # Display each holding with update/close options
                    for idx, holding in enumerate(open_holdings):
                        with st.expander(f"📊 {holding['symbol']} - Qty: {holding['quantity']} | Entry: ${holding['entry_price']:.2f}", expanded=False):
                            col_info1, col_info2, col_info3 = st.columns(3)
                            
                            with col_info1:
                                st.write(f"**Entry Date:** {holding['entry_date']}")
                                st.write(f"**Cost Basis:** ${holding['quantity'] * holding['entry_price']:,.2f}")
                            
                            with col_info2:
                                st.write(f"**Current Price:** ${holding['current_price']:.2f}")
                                st.write(f"**Current Value:** ${holding['quantity'] * holding['current_price']:,.2f}")
                            
                            with col_info3:
                                pnl = holding.get('unrealized_pnl', 0)
                                pnl_pct = ((holding['current_price'] - holding['entry_price']) / holding['entry_price'] * 100) if holding['entry_price'] > 0 else 0
                                st.metric("Unrealized P&L", f"${pnl:.2f}", delta=f"{pnl_pct:+.2f}%")
                            
                            if holding.get('notes'):
                                st.info(f"📝 **Notes:** {holding['notes']}")
                            
                            st.divider()
                            
                            # Update price
                            col_action1, col_action2 = st.columns(2)
                            with col_action1:
                                new_price = st.number_input(
                                    "Update Current Price",
                                    min_value=0.0,
                                    value=float(holding['current_price']),
                                    step=0.01,
                                    key=f"price_{holding['id']}"
                                )
                                if st.button("🔄 Update Price", key=f"update_{holding['id']}"):
                                    holding['current_price'] = new_price
                                    holding['unrealized_pnl'] = (holding['quantity'] * new_price) - (holding['quantity'] * holding['entry_price'])
                                    save_holdings_data(holdings_data)
                                    st.success("Price updated!")
                                    st.rerun()
                            
                            with col_action2:
                                close_price = st.number_input(
                                    "Close Position Price",
                                    min_value=0.0,
                                    value=float(holding['current_price']),
                                    step=0.01,
                                    key=f"close_price_{holding['id']}"
                                )
                                if st.button("✅ Close Position", key=f"close_{holding['id']}", type="primary"):
                                    # Calculate realized P&L
                                    realized_pnl = (holding['quantity'] * close_price) - (holding['quantity'] * holding['entry_price'])
                                    
                                    # Add to closed trades
                                    closed_trade = {
                                        "date": datetime.now().strftime("%Y-%m-%d"),
                                        "symbol": holding['symbol'],
                                        "position": "Long",
                                        "entry_price": holding['entry_price'],
                                        "exit_price": close_price,
                                        "volume": holding['quantity'] * close_price,
                                        "pnl": realized_pnl,
                                        "notes": f"Closed from holdings. {holding.get('notes', '')}",
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    
                                    # Update data
                                    data.append(closed_trade)
                                    save_data(data)
                                    
                                    # Mark as closed
                                    holding['status'] = 'closed'
                                    holding['close_price'] = close_price
                                    holding['close_date'] = datetime.now().strftime("%Y-%m-%d")
                                    save_holdings_data(holdings_data)
                                    
                                    st.success(f"✅ Position closed! Realized P&L: ${realized_pnl:.2f}")
                                    st.balloons()
                                    st.rerun()
                else:
                    st.info("📭 Tidak ada posisi terbuka. Tambahkan posisi baru di tab 'Add New Position'")
                
                # Show closed positions
                closed_holdings = [h for h in holdings_data if h.get('status') == 'closed']
                if closed_holdings:
                    st.divider()
                    st.markdown("### 📜 Closed Positions History")
                    df_closed = pd.DataFrame(closed_holdings)
                    display_cols = ['symbol', 'quantity', 'entry_price', 'close_price', 'close_date']
                    df_closed_display = df_closed[display_cols].copy()
                    df_closed_display.columns = ['Symbol', 'Quantity', 'Entry Price', 'Close Price', 'Close Date']
                    st.dataframe(df_closed_display, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Belum ada holdings. Mulai tambahkan posisi di tab 'Add New Position'")
    
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
        
        # Calculate unrealized P&L
        total_unrealized_pnl = 0
        if holdings_data:
            for holding in holdings_data:
                if holding.get('status') == 'open':
                    total_unrealized_pnl += holding.get('unrealized_pnl', 0)
        
        realized_pnl = stats['net_pnl']
        total_pnl = realized_pnl + total_unrealized_pnl
        portfolio_value = new_balance + total_pnl
        change_pct = ((total_pnl / new_balance) * 100) if new_balance > 0 else 0
        
        preview_col1, preview_col2, preview_col3, preview_col4 = st.columns(4)
        with preview_col1:
            st.metric("Initial Balance", f"${new_balance:,.2f}")
        with preview_col2:
            st.metric("Realized P&L", f"${realized_pnl:,.2f}", 
                     delta_color="normal" if realized_pnl >= 0 else "inverse")
        with preview_col3:
            st.metric("Unrealized P&L", f"${total_unrealized_pnl:,.2f}",
                     delta_color="normal" if total_unrealized_pnl >= 0 else "inverse")
        with preview_col4:
            st.metric("Portfolio Value", f"${portfolio_value:,.2f}", 
                     delta=f"{change_pct:+.2f}%",
                     delta_color="normal" if total_pnl >= 0 else "inverse")
    
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
