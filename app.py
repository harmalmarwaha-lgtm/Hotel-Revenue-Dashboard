"""
Hotel Revenue Analysis Dashboard
Developed using Python, Streamlit, Pandas, and Plotly.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime
import base64
from pathlib import Path


DATA_FILE = Path(__file__).resolve().with_name("hotelrevenue.csv")

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Hotel Revenue Analysis Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM CSS
# ==========================================
def apply_custom_css():
     """
    Injects custom CSS to style the Streamlit app with a modern, 
    professional gradient theme, glassmorphism containers, 
    hover effects, and KPI cards.
    """
st.markdown(
        """
        <style>
        /* Main background and font */
        .stApp {
            background: linear-gradient(to right bottom, #f8f9fa, #e9ecef);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* KPI Cards */
        .kpi-container {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 25px;
        }
        .kpi-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            flex: 1;
            min-width: 150px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #1f77b4;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        .kpi-title {
            color: #6c757d;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-value {
            color: #212529;
            font-size: 1.8rem;
            font-weight: bold;
            margin: 0;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #dee2e6;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        }
        [data-testid="stSidebar"] h1 {
            color: #1f77b4;
            font-weight: 700;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            background-color: #1f77b4;
            color: white;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #155787;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #2c3e50;
            font-weight: 700;
        }
        
        /* Chart Containers */
        .stPlotlyChart {
            background-color: white;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            margin-bottom: 20px;
        }
        
        /* Dataframes */
        [data-testid="stDataFrame"] {
            background-color: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #e9ecef;
            border-bottom: 3px solid #1f77b4;
            color: #1f77b4;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATA LOADING & PREPROCESSING
# ==========================================
@st.cache_data
def load_data(uploaded_file=None):
    """Loads and preprocesses the hotel revenue dataset."""
    try:
        source = uploaded_file if uploaded_file is not None else DATA_FILE
        # Resolve the bundled CSV from the app's folder, not Streamlit's
        # current working directory (which varies depending on how it is run).
        df = pd.read_csv(source, encoding="utf-8-sig")
            
        # Convert date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
            
        # Handle Missing Values Gracefully
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Calculate Profit if missing but Revenue and Costs exist
        if 'Profit' in df.columns and df['Profit'].isna().all():
            if 'Total_Revenue' in df.columns and 'Total_Costs' in df.columns:
                df['Profit'] = df['Total_Revenue'] - df['Total_Costs']
                
        # Fill remaining missing numeric values with 0
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Fill missing categorical values with 'Unknown'
        df[categorical_cols] = df[categorical_cols].fillna('Unknown')
        
        return df
        
    except FileNotFoundError:
        st.error(f"Error: Dataset not found at {DATA_FILE}. Please upload a CSV in the sidebar.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return pd.DataFrame()

# ==========================================
# 4. SIDEBAR & FILTERS
# ==========================================
def render_sidebar(df):
    """Renders the sidebar and returns filtered dataset."""
    st.sidebar.title("🏨 Hotel Dashboard")
    st.sidebar.markdown("---")
    
    if df.empty:
        return pd.DataFrame(), "Home Dashboard"
        
    # Navigation
    st.sidebar.markdown("### Navigation")
    pages = [
        "Home Dashboard",
        "Dataset Viewer",
        "Exploratory Data Analysis",
        "Business Insights",
        "Prediction Engine",
        "Contact & Feedback",
    ]
    selected_page = st.sidebar.radio("Go to:", pages)
    st.sidebar.markdown("---")
    
    # Initialize session state for filters to allow reset
    if 'reset_filters' not in st.session_state:
        st.session_state.reset_filters = False

    if st.sidebar.button("🔄 Reset Filters"):
        st.session_state.reset_filters = not st.session_state.reset_filters
        st.rerun()

    # Dynamic Filters (Mapping requested filters to existing columns)
    st.sidebar.markdown("### Data Filters")
    
    # Date processing for Year and Month filters
    available_years = []
    available_months = []
    if 'Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Date']):
        available_years = df['Date'].dt.year.dropna().unique().tolist()
        available_months = sorted(df['Month'].dropna().unique().tolist())
    
    selected_years = st.sidebar.multiselect("Select Year", options=available_years, default=available_years)
    selected_months = st.sidebar.multiselect("Select Month", options=available_months, default=available_months)
    
    # Categorical Filters using actual dataset columns
    col_mappings = {
        'Guest_Country': 'City/Country',
        'Market_Segment': 'Room/Market Type',
        'Guest_Type': 'Guest Type',
        'Booking_Channel': 'Booking Status/Channel'
    }
    
    filters = {}
    for col, alias in col_mappings.items():
        if col in df.columns:
            unique_vals = df[col].unique().tolist()
            filters[col] = st.sidebar.multiselect(f"Select {alias}", options=unique_vals, default=unique_vals)
            
    # Apply Filters
    filtered_df = df.copy()
    
    if 'Date' in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df['Date']):
        if selected_years:
            filtered_df = filtered_df[filtered_df['Date'].dt.year.isin(selected_years)]
    if selected_months and 'Month' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]
        
    for col, selected_vals in filters.items():
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]
            
    return filtered_df, selected_page

# ==========================================
# 5. KPI CARDS
# ==========================================
def render_kpis(df):
    """Calculates and renders Key Performance Indicators."""
    if df.empty:
        return
        
    # Calculations strictly using existing columns
    total_rev = df['Total_Revenue'].sum() if 'Total_Revenue' in df.columns else 0
    total_bookings = df['Bookings'].sum() if 'Bookings' in df.columns else 0
    avg_booking_val = total_rev / total_bookings if total_bookings > 0 else 0
    occ_rate = df['Occupancy_Rate'].mean() * 100 if 'Occupancy_Rate' in df.columns else 0
    
    cancellations = df['Cancellations'].sum() if 'Cancellations' in df.columns else 0
    cancel_rate = (cancellations / total_bookings) * 100 if total_bookings > 0 else 0
    
    avg_adr = df['ADR'].mean() if 'ADR' in df.columns else 0
    avg_review = df['Average_Review_Score'].mean() if 'Average_Review_Score' in df.columns else 0
    
    # Format numbers dynamically
    def format_num(num, is_currency=False, is_percent=False):
        if is_currency:
            return f"${num:,.0f}" if num >= 1000 else f"${num:,.2f}"
        if is_percent:
            return f"{num:.1f}%"
        return f"{num:,.0f}"

    # HTML structure for cards
    html_content = f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value">{format_num(total_rev, is_currency=True)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total Bookings</div>
            <div class="kpi-value">{format_num(total_bookings)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Avg Booking Value</div>
            <div class="kpi-value">{format_num(avg_booking_val, is_currency=True)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Avg Occupancy Rate</div>
            <div class="kpi-value">{format_num(occ_rate, is_percent=True)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Cancellation Rate</div>
            <div class="kpi-value">{format_num(cancel_rate, is_percent=True)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Avg Daily Rate (ADR)</div>
            <div class="kpi-value">{format_num(avg_adr, is_currency=True)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Avg Review Score</div>
            <div class="kpi-value">{format_num(avg_review, is_percent=False)} / 10</div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# ==========================================
# 6. PLOTLY CHARTS
# ==========================================
def render_home_dashboard(df):
    """Renders the main dashboard charts mapping user requirements to existing columns."""
    st.markdown("## 📊 Hotel Revenue Analysis Dashboard")
    render_kpis(df)
    
    if df.empty:
        st.warning("No data available for the selected filters.")
        return

    st.markdown("### Core Analytics")
    
    # Generic Chart Layout Updater
    def update_layout(fig, title):
        fig.update_layout(
            title={'text': title, 'font': {'size': 18, 'color': '#2c3e50'}, 'x': 0.05},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, l=10, r=10, b=10),
            hovermode='closest',
            font=dict(family="Segoe UI")
        )
        fig.update_xaxes(showgrid=False, linecolor='#e9ecef')
        fig.update_yaxes(showgrid=True, gridcolor='#e9ecef', linecolor='#e9ecef')
        return fig

    # Layout using Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Revenue Analytics", "📈 Booking & Occupancy", "👥 Guest Demographics", "⚙️ Operations & Costs"])

    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Monthly Revenue Trend
            try:
                monthly_rev = df.groupby('Month')['Total_Revenue'].sum().reset_index()
                fig1 = px.line(monthly_rev, x='Month', y='Total_Revenue', markers=True, 
                              line_shape='spline', color_discrete_sequence=['#1f77b4'])
                fig1.update_traces(fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.2)')
                st.plotly_chart(update_layout(fig1, "Monthly Revenue Trend"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 2. Revenue by 'Hotel' mapped to Booking_Channel
            try:
                channel_rev = df.groupby('Booking_Channel')['Total_Revenue'].sum().reset_index().sort_values('Total_Revenue', ascending=False)
                fig2 = px.bar(channel_rev, x='Booking_Channel', y='Total_Revenue', color='Booking_Channel',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(update_layout(fig2, "Revenue by Channel (Hotel Substitute)"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
        with col2:
            # 3. Revenue by 'City' mapped to Guest_Country
            try:
                country_rev = df.groupby('Guest_Country')['Total_Revenue'].sum().reset_index().sort_values('Total_Revenue', ascending=False).head(10)
                fig3 = px.bar(country_rev, y='Guest_Country', x='Total_Revenue', orientation='h', color='Total_Revenue', color_continuous_scale='Blues')
                st.plotly_chart(update_layout(fig3, "Top 10 Revenue by Country (City Substitute)"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 4. Revenue by 'Room Type' mapped to Market_Segment
            try:
                segment_rev = df.groupby('Market_Segment')['Total_Revenue'].sum().reset_index()
                fig4 = px.pie(segment_rev, names='Market_Segment', values='Total_Revenue', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(update_layout(fig4, "Revenue by Market Segment (Room Type Substitute)"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")

    with tab2:
        col3, col4 = st.columns(2)
        
        with col3:
            # 5. Booking Status Pie Chart (Bookings vs Cancellations vs No Shows)
            try:
                b_sum = df['Bookings'].sum()
                c_sum = df['Cancellations'].sum()
                n_sum = df['No_Shows'].sum()
                status_df = pd.DataFrame({'Status': ['Completed', 'Cancelled', 'No Show'], 'Count': [b_sum, c_sum, n_sum]})
                fig5 = px.pie(status_df, names='Status', values='Count', color='Status', 
                             color_discrete_map={'Completed':'#2ca02c', 'Cancelled':'#d62728', 'No Show':'#ff7f0e'})
                st.plotly_chart(update_layout(fig5, "Booking Status Distribution"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 6. Monthly Booking Trend
            try:
                monthly_bookings = df.groupby('Month')['Bookings'].sum().reset_index()
                fig6 = px.bar(monthly_bookings, x='Month', y='Bookings', text='Bookings', color_discrete_sequence=['#9467bd'])
                fig6.update_traces(textposition='outside')
                st.plotly_chart(update_layout(fig6, "Monthly Booking Trend"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 7. Cancellation Analysis (Month vs Cancellations)
            try:
                monthly_cancel = df.groupby('Month')['Cancellations'].sum().reset_index()
                fig7 = go.Figure()
                fig7.add_trace(go.Scatter(x=monthly_cancel['Month'], y=monthly_cancel['Cancellations'], mode='lines+markers',
                                         line=dict(color='red', width=3), marker=dict(size=8)))
                st.plotly_chart(update_layout(fig7, "Cancellation Analysis Trend"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
        with col4:
            # 8. Occupancy Analysis
            try:
                occ_trend = df.groupby('Date')['Occupancy_Rate'].mean().reset_index()
                fig8 = px.area(occ_trend, x='Date', y='Occupancy_Rate', color_discrete_sequence=['#17becf'])
                st.plotly_chart(update_layout(fig8, "Daily Occupancy Rate Analysis"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 9. Weekend vs Weekday Revenue
            try:
                wd_rev = df.groupby('Weekday')['Total_Revenue'].mean().reset_index()
                fig9 = px.bar(wd_rev, x='Weekday', y='Total_Revenue', color='Total_Revenue', color_continuous_scale='Viridis')
                st.plotly_chart(update_layout(fig9, "Average Revenue: Weekday vs Weekend"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 10. Stay Duration Proxy (Checkouts vs Checkins correlation or ADR distribution)
            try:
                fig10 = px.histogram(df, x='ADR', nbins=20, marginal="box", color_discrete_sequence=['#e377c2'])
                st.plotly_chart(update_layout(fig10, "ADR Distribution (Stay Value Proxy)"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")

    with tab3:
        col5, col6 = st.columns(2)
        
        with col5:
            # 11. Guest Type Distribution
            try:
                guest_type = df.groupby('Guest_Type')['Bookings'].sum().reset_index()
                fig11 = px.pie(guest_type, names='Guest_Type', values='Bookings', hole=0.5,
                              color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(update_layout(fig11, "Guest Type Distribution"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 12. Payment Method mapped to Season
            try:
                season_rev = df.groupby('Season')['Total_Revenue'].sum().reset_index()
                fig12 = px.bar(season_rev, x='Season', y='Total_Revenue', color='Season',
                              color_discrete_sequence=px.colors.qualitative.Vivid)
                st.plotly_chart(update_layout(fig12, "Revenue by Season (Payment Proxy)"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
        with col6:
            # 13. Review Score Distribution
            try:
                fig13 = px.histogram(df, x='Average_Review_Score', nbins=10, color_discrete_sequence=['#bcbd22'])
                st.plotly_chart(update_layout(fig13, "Review Score Distribution"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
            # 14. Room Revenue Comparison
            try:
                fig14 = px.scatter(df, x='Room_Revenue', y='Total_Revenue', color='Season', size='Occupancy_Rate',
                                  hover_data=['Date'])
                st.plotly_chart(update_layout(fig14, "Room Revenue vs Total Revenue"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")

    with tab4:
        col7, col8 = st.columns(2)
        
        with col7:
            # 15. Revenue Heatmap (Correlation of numeric values)
            try:
                numeric_df = df[['Total_Revenue', 'Room_Revenue', 'Profit', 'Occupancy_Rate', 'ADR', 'Marketing_Spend']].dropna()
                corr = numeric_df.corr().round(2)
                fig15 = ff.create_annotated_heatmap(
                    z=corr.values,
                    x=list(corr.columns),
                    y=list(corr.index),
                    colorscale='RdBu',
                    showscale=True
                )
                fig15 = update_layout(fig15, "Financial Metrics Correlation Heatmap")
                st.plotly_chart(fig15, use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")
            
        with col8:
            # 16. Costs Breakdown
            try:
                costs_df = df[['Operating_Expenses', 'Fixed_Costs', 'Variable_Costs']].sum().reset_index()
                costs_df.columns = ['Cost_Type', 'Amount']
                fig16 = px.bar(costs_df, x='Cost_Type', y='Amount', color='Cost_Type', text_auto=True,
                              color_discrete_sequence=['#ff9896', '#c5b0d5', '#c49c94'])
                st.plotly_chart(update_layout(fig16, "Overall Costs Distribution"), use_container_width=True)
            except Exception as e: st.error(f"Chart error: {e}")

# ==========================================
# 7. DATASET VIEWER PAGE
# ==========================================
def render_dataset_page(df):
    st.markdown("## 🗃️ Dataset Viewer")
    st.markdown("Explore the raw data, structure, and summary statistics.")
    
    if df.empty:
        st.warning("No data available.")
        return

    # Dataset Summary Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", df.isna().sum().sum())
    col4.metric("Duplicate Rows", df.duplicated().sum())
    col5.metric("Numeric Features", len(df.select_dtypes(include=np.number).columns))
    
    st.markdown("### Raw Data")
    st.dataframe(df, use_container_width=True, height=400)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Data Types")
        dtypes_df = pd.DataFrame(df.dtypes, columns=['Data Type']).astype(str)
        st.dataframe(dtypes_df, use_container_width=True)
        
    with col_b:
        st.markdown("### Summary Statistics")
        st.dataframe(df.describe().T, use_container_width=True)

# ==========================================
# 8. EXPLORATORY DATA ANALYSIS (EDA)
# ==========================================
def render_eda_page(df):
    st.markdown("## 🔬 Exploratory Data Analysis")
    st.markdown("Create custom visualizations on the fly to uncover hidden patterns.")
    
    if df.empty:
        st.warning("No data available.")
        return

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    all_cols = numeric_cols + categorical_cols

    with st.container():
        st.markdown("<div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        chart_type = col1.selectbox("Chart Type", ["Scatter Plot", "Bar Chart", "Histogram", "Box Plot", "Violin Plot", "Pair Plot (Numeric)"])
        
        if chart_type != "Pair Plot (Numeric)":
            x_axis = col2.selectbox("X-Axis", options=all_cols, index=all_cols.index('Month') if 'Month' in all_cols else 0)
            y_axis = col3.selectbox("Y-Axis", options=numeric_cols, index=numeric_cols.index('Total_Revenue') if 'Total_Revenue' in numeric_cols else 0)
            color_split = col4.selectbox("Color By (Optional)", options=["None"] + categorical_cols)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        color_arg = None if chart_type == "Pair Plot (Numeric)" or color_split == "None" else color_split
        
        try:
            if chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, color=color_arg, hover_data=['Date'] if 'Date' in df.columns else None)
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Bar Chart":
                grouped = df.groupby([x_axis]) if color_arg is None else df.groupby([x_axis, color_arg])
                grouped = grouped[y_axis].mean().reset_index()
                fig = px.bar(grouped, x=x_axis, y=y_axis, color=color_arg, barmode='group')
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x_axis, y=y_axis, color=color_arg, marginal="box")
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Box Plot":
                fig = px.box(df, x=x_axis, y=y_axis, color=color_arg)
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Violin Plot":
                fig = px.violin(df, x=x_axis, y=y_axis, color=color_arg, box=True, points="all")
                st.plotly_chart(fig, use_container_width=True)
                
            elif chart_type == "Pair Plot (Numeric)":
                st.info("Generating Pair Plot... This may take a moment for large datasets.")
                selected_num = st.multiselect("Select columns for Pair Plot", options=numeric_cols, default=numeric_cols[:4])
                if len(selected_num) > 1:
                    fig = px.scatter_matrix(df, dimensions=selected_num, color=categorical_cols[0] if categorical_cols else None)
                    fig.update_layout(height=800)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select at least 2 numeric columns.")
                    
        except Exception as e:
            st.error(f"Could not render {chart_type}. Error: {e}")

# ==========================================
# 9. BUSINESS INSIGHTS PAGE
# ==========================================
def render_insights_page(df):
    st.markdown("## 💡 Automated Business Insights")
    st.markdown("Actionable intelligence generated from your current dataset constraints.")
    
    if df.empty:
        st.warning("No data available.")
        return

    # Helper for safe aggregation
    def get_max_record(groupby_col, target_col, method='sum'):
        if groupby_col not in df.columns or target_col not in df.columns:
            return "N/A", 0
        if method == 'sum':
            grouped = df.groupby(groupby_col)[target_col].sum()
        else:
            grouped = df.groupby(groupby_col)[target_col].mean()
        
        if grouped.empty: return "N/A", 0
        idx = grouped.idxmax()
        val = grouped.max()
        return idx, val

    def get_min_record(groupby_col, target_col, method='sum'):
        if groupby_col not in df.columns or target_col not in df.columns:
            return "N/A", 0
        if method == 'sum':
            grouped = df.groupby(groupby_col)[target_col].sum()
        else:
            grouped = df.groupby(groupby_col)[target_col].mean()
            
        if grouped.empty: return "N/A", 0
        idx = grouped.idxmin()
        val = grouped.min()
        return idx, val

    # Generating Insights
    best_season, bs_val = get_max_record('Season', 'Total_Revenue', 'sum')
    high_month, hm_val = get_max_record('Month', 'Total_Revenue', 'sum')
    low_month, lm_val = get_min_record('Month', 'Total_Revenue', 'sum')
    high_occ_channel, hoc_val = get_max_record('Booking_Channel', 'Occupancy_Rate', 'mean')
    most_cancel_country, mcc_val = get_max_record('Guest_Country', 'Cancellations', 'sum')
    best_market, bm_val = get_max_record('Market_Segment', 'Total_Revenue', 'sum')
    high_rated_guest, hrg_val = get_max_record('Guest_Type', 'Average_Review_Score', 'mean')

    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"**🌟 Best Performing Season:** {best_season} (${bs_val:,.2f} Revenue)")
        st.info(f"**📅 Highest Revenue Month:** Month {high_month} (${hm_val:,.2f})")
        st.error(f"**📉 Lowest Revenue Month:** Month {low_month} (${lm_val:,.2f})")
        st.warning(f"**🚫 Highest Cancellations Origin:** {most_cancel_country} ({mcc_val:,.0f} cancelled)")
        
    with col2:
        st.success(f"**🛌 Best Market Segment:** {best_market} (${bm_val:,.2f} Revenue)")
        st.info(f"**📈 Highest Occupancy Channel:** {high_occ_channel} ({(hoc_val*100):.1f}%)")
        st.success(f"**⭐ Highest Rated Guest Type:** {high_rated_guest} ({hrg_val:.2f}/10)")
        
    st.markdown("---")
    st.markdown("### Suggested Actions")
    st.markdown(f"""
    - **Marketing Focus:** Double down on marketing campaigns during **Season {best_season}**, which currently yields the highest revenue.
    - **Retention Strategy:** Investigate the high cancellation rates originating from **{most_cancel_country}** and offer non-refundable discounted rates.
    - **Channel Optimization:** Since **{high_occ_channel}** brings the highest occupancy, negotiate better commission structures or allocate more inventory to this channel.
    - **Off-Peak Tactics:** Implement targeted promotions for **Month {low_month}** to offset seasonal revenue dips.
    """)

# ==========================================
# 10. PREDICTION PAGE
# ==========================================
def render_prediction_page(df):
    st.markdown("## 🤖 Revenue Prediction Engine")
    st.markdown("Enter simulated parameters to predict estimated total revenue. *(UI Interface Only)*")
    
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📅 Operational Metrics**")
            month = st.selectbox("Month", options=range(1, 13))
            season = st.selectbox("Season", options=["Winter", "Spring", "Summer", "Autumn"])
            holiday = st.selectbox("Holiday Period?", options=[1, 0], format_func=lambda x: "Yes" if x==1 else "No")
            
        with col2:
            st.markdown("**💰 Financial Inputs**")
            mkt_spend = st.number_input("Marketing Spend ($)", min_value=0, value=50000, step=1000)
            adr = st.number_input("Target ADR ($)", min_value=0.0, value=150.0, step=10.0)
            fixed_costs = st.number_input("Fixed Costs ($)", min_value=0, value=10000, step=1000)
            
        with col3:
            st.markdown("**📈 Market Conditions**")
            target_occ = st.slider("Expected Occupancy Rate", 0.0, 1.0, 0.75, 0.01)
            avail_rooms = st.number_input("Available Rooms", min_value=1, value=200, step=10)
            channel = st.selectbox("Primary Booking Channel", options=["Direct", "OTA", "Corporate", "Agency"])

        st.markdown("---")
        submit_btn = st.form_submit_button("Predict Revenue 🚀")
        
        if submit_btn:
            # Dummy ML calculation logic for UI completeness
            base_revenue = avail_rooms * adr * target_occ * 30  # Monthly approx
            marketing_lift = mkt_spend * 0.15
            holiday_multiplier = 1.2 if holiday == 1 else 1.0
            
            predicted_rev = (base_revenue + marketing_lift) * holiday_multiplier
            predicted_profit = predicted_rev - (fixed_costs + (avail_rooms * target_occ * 30 * 20)) # Assuming $20 var cost per occupied room
            
            st.markdown("### 📊 Prediction Results")
            res_col1, res_col2 = st.columns(2)
            res_col1.metric("Estimated Total Revenue", f"${predicted_rev:,.2f}")
            res_col2.metric("Estimated Net Profit", f"${predicted_profit:,.2f}")
            
            st.progress(min(int((target_occ) * 100), 100), text=f"Occupancy Utilization: {target_occ*100:.1f}%")


# ==========================================
# 11. PAGE: CONTACT & FEEDBACK
# ==========================================
def render_feedback_page():
    st.title("📬 Contact & Dashboard Feedback")
    st.markdown("We value your input! Please rate your experience using the Hotel Dashboard.")

    # Added explicit contact email display
    st.info("📧 **Direct Contact Email is:** support@hotelrevenue.com")

    st.markdown("<div class='feedback-form'>", unsafe_allow_html=True)
    
    with st.form("feedback_form"):
        st.markdown("#### User Feedback Form")
        
        # User's contact email input
        user_email = st.text_input("Your Contact Email", placeholder="user@example.com")
        
        rating = st.radio(
            "Rate your dashboard experience:",
            ["⭐ (Poor)", "⭐⭐ (Fair)", "⭐⭐⭐ (Good)", "⭐⭐⭐⭐ (Very Good)", "⭐⭐⭐⭐⭐ (Excellent)"],
            index=4
        )
        
        comments = st.text_area("Additional Comments / Feature Requests", placeholder="I would love to see...")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if user_email:
                st.success(f"Thank you! Your feedback ({rating}) has been recorded. We will reach out to {user_email} if needed.")
            else:
                st.error("Please provide a valid email address.")
                
    st.markdown("</div>", unsafe_allow_html=True)
# ==========================================
# 11. DOWNLOAD SECTION & FOOTER
# ==========================================
def render_footer_and_downloads(df):
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if not df.empty:
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="filtered_hotel_revenue.csv" class="stButton" style="text-decoration:none;"><button style="width: auto;">📥 Download Filtered Data (CSV)</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            
    with col2:
        st.markdown(
            """
            <div style='text-align: right; color: #6c757d; font-size: 0.9rem;'>
                <strong>Hotel Revenue Analysis Dashboard</strong><br>
                Developed using Python, Streamlit, Pandas and Plotly
            </div>
            """, 
            unsafe_allow_html=True
        )

# ==========================================
# 12. MAIN APP EXECUTION
# ==========================================
def main():
    apply_custom_css()
    
    # An uploaded CSV takes precedence; otherwise use the CSV beside this file.
    uploaded_file = st.sidebar.file_uploader("Upload Dataset (CSV)", type=['csv'])
    df_raw = load_data(uploaded_file)
    
    # Render Sidebar and get filtered data
    filtered_df, selected_page = render_sidebar(df_raw)

    # Route to selected page
    if selected_page == "Home Dashboard":
        render_home_dashboard(filtered_df)
    elif selected_page == "Dataset Viewer":
        render_dataset_page(filtered_df)
    elif selected_page == "Exploratory Data Analysis":
        render_eda_page(filtered_df)
    elif selected_page == "Business Insights":
        render_insights_page(filtered_df)
    elif selected_page == "Prediction Engine":
        render_prediction_page(filtered_df)
    elif selected_page == "Contact & Feedback":
        render_feedback_page()

if __name__ == "__main__":
    main()
