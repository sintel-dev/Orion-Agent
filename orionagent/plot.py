import pandas as pd
import plotly.express as px
import random

def generate_time_series_chart():
    df = pd.DataFrame({
        "time": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "value": [random.randint(0, 100) for _ in range(10)]
    })
    fig = px.line(df, x="time", y="value", title="Random Time Series Chart")
    return fig

def plot_dataframe(df, time_column, value_column):
    fig = px.line(df, x=time_column, y=value_column, title="Time Series Chart")
    return fig