import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import requests

st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 0.5rem;
                    padding-bottom: 0rem;
                    max-width: 90%;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                .top-margin{
                    margin-top: 1rem;
                    margin-bottom:1rem;
                }
                .block-button{
                    padding: 10px; 
                    width: 100%;
                    background-color: #c4fcce;
                }
                /* Force wide layout */
                .main .block-container {
                    max-width: 100%;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)

def dashboard_page():
    st.markdown(
    """
    <div style='text-align: center; padding: 1.5rem 2rem;'>
        <h2 style='margin-bottom: 0.5rem;'>📊 Admin Analytics Dashboard</h2>
        <p style='font-size: 18px; color: #555;'>
            Monitor outbound call performance, agent effectiveness, and key campaign metrics — all in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True)

    with st.spinner("Querying the database and calculating the metrics..."):
        # Fetch admin panel stats from external API endpoint
        response = requests.get(f"https://{st.secrets.get('BASE_URL')}/admin/dashboard/stats")
        if response.status_code == 200:
            admin_panel_stats = response.json()
        else:
            st.error(f"Failed to fetch admin panel stats. Status code: {response.status_code}")
            admin_panel_stats = {}
        # Fetch admin panel data from external API endpoint
        data_response = requests.get(f"https://{st.secrets.get('BASE_URL')}/admin/calls?page=1&limit=50&status_filter=completed")
        if data_response.status_code == 200:
            admin_panel_data = data_response.json().get('data', [])
        else:
            st.error(f"Failed to fetch admin panel data. Status code: {data_response.status_code}")
            admin_panel_data = []
        st.dataframe(admin_panel_data)
        st.write("***")

        # --- Visualization Grid ---
        main_blue = "#2563eb"
        light_blue = "#60a5fa"
        gray = "#e5e7eb"

        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            # Donut Chart: Call Status Distribution
            if 'status_breakdown' in admin_panel_stats:
                labels = list(admin_panel_stats['status_breakdown'].keys())
                values = list(admin_panel_stats['status_breakdown'].values())
                colors = [main_blue] + [gray] * (len(labels) - 1)
                fig1 = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.6,
                    marker=dict(colors=colors),
                    textinfo='percent+label'
                )])
                fig1.update_layout(title_text="Call Status", showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.error("Admin panel stats are not available or 'status_breakdown' is missing.")

        with col2:
            # Bar Chart: Objective Success/Failure
            achieved = admin_panel_stats.get('objective_achieved_count', 0)
            not_achieved = admin_panel_stats['total_calls'] - achieved
            fig2 = go.Figure(data=[go.Bar(
                x=["Achieved", "Not Achieved"],
                y=[achieved, not_achieved],
                marker_color=main_blue
            )])
            fig2.update_layout(title_text="Objective Success/Failure", xaxis_title="", yaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)

        with col3:
            # Gauge Chart: Call Success Rate
            fig3 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=admin_panel_stats['success_rate'],
                title={"text": "Call Success Rate"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": main_blue},
                    "bgcolor": gray,
                    "steps": [
                        {"range": [0, 100], "color": gray},
                    ],
                }
            ))
            fig3.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig3, use_container_width=True)

        col4, col5, col6 = st.columns(3, gap="large")

        with col4:
            # Scatter Plot: Call Duration (Each dot = one call, arranged horizontally by call index)
            durations = [row['call_duration'] for row in admin_panel_data if row.get('call_duration') is not None]
            call_indices = list(range(1, len(durations) + 1))
            fig4 = px.scatter(
                x=call_indices,
                y=durations,
                labels={'x': 'Call #', 'y': 'Duration (seconds)'},
                color_discrete_sequence=[main_blue]
            )
            fig4.update_traces(marker=dict(size=10, opacity=0.7))
            fig4.update_layout(
                title="Call Duration per Call",
                xaxis_title="Call #",
                yaxis_title="Duration (seconds)",
                showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)

        with col5:
            # KPI Card: Total Revenue
            st.markdown(
                f"""
                <div style="background-color:#fff;padding:30px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                    <h2 style="color:#222;">Total Revenue</h2>
                    <h1 style="color:{main_blue};">${admin_panel_stats['total_revenue']:.2f}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col6:
            # Dual Bar Chart: Call vs. Objective Success Rate
            fig6 = go.Figure(data=[
                go.Bar(name='Call Success Rate', x=['Call Success Rate'], y=[admin_panel_stats['success_rate']], marker_color=main_blue),
                go.Bar(name='Objective Success Rate', x=['Objective Success Rate'], y=[admin_panel_stats.get('objective_success_rate', 0)], marker_color=light_blue)
            ])
            fig6.update_layout(
                barmode='group',
                title_text="Call vs. Objective Success Rate",
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig6, use_container_width=True)

dashboard_page()