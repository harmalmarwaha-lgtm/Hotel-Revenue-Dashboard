import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
     page_title="Hotel Revenue Dashboard",
    page_icon='📊',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Complete Data Analysis Dashboard\nBuilt with Streamlit, NumPy, Pandas, Matplotlib, Seaborn, and Plotly"
    }
)
st.title("🏨 Hotel Revenue 2024 Dashboard")
# Custom styling
st.markdown("""
<style>
       .main {
            padding-top: 2rem;
            }
            .metric-card{
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .header-style{
                color: #1f77b4;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 1rem;
            }
    </style>
    """,unsafe_allow_html=True)
# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("hotelrevenue.csv")
    return df
df = load_data()
st.dataframe(df)
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

     
