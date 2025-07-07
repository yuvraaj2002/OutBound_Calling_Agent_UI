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
from io import BytesIO
from datetime import datetime

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
        <p style='font-size: 18px; color: #555;'>Monitor and analyze your outbound call operations in real time. This dashboard provides a comprehensive overview of call performance, agent effectiveness, and campaign outcomes—all in one place. Track key metrics such as total calls, revenue, and call durations to identify trends and opportunities. Visualize call status and success rates to quickly spot areas for improvement. Use these actionable insights to optimize your outreach strategy, boost agent productivity, and drive business growth.</p>
    </div>
    """,
    unsafe_allow_html=True
)

    with st.spinner("Querying the database and calculating the metrics..."):
        # --- Hardcode original admin panel data for demo/visual effect ---
        admin_panel_stats = {
            "total_calls": 3,
            "status_breakdown": {
                "queued": 1,
                "completed": 2
            },
            "total_costing": 0.58,
            "average_call_duration": 3.2,
            "calls_today": 2,
            "failed_calls": 0,
            "completed_calls": 2,
            "success_rate": 66.67
        }
        admin_panel_data = [
            {"created_at": "2025-07-07T07:24:07.847473", "call_id": "c32fb1cf-6875-4341-8db3-84413a8bec9e", "contact_name": "Yuvraj Singh", "contact_number": "+916239305919", "contact_email": "ys7233831@gmail.com", "tag_type": "cpap lead", "contact_id": "cNjYuT59LETLuxDe4I3T", "call_status": "completed", "agent_name": "David (Male)", "agent_voice_id": "1c1ca816-f457-4dde-a12a-eaf19fb0b523", "call_duration": 3.5},
            {"created_at": "2025-07-07T06:04:36.094957", "call_id": "f7bbbe8f-70f6-4b4c-a4ac-8c4639d2c7b4", "contact_name": "Yuvraj Singh", "contact_number": "+916239305919", "contact_email": "ys7233831@gmail.com", "tag_type": "cgm", "contact_id": "cNjYuT59LETLuxDe4I3T", "call_status": "completed", "agent_name": "Ava (Female)", "agent_voice_id": "fc585787-f5a8-4c3d-a16f-759a895c114a", "call_duration": 3.0}
        ]
        st.dataframe(admin_panel_data)
        # Add Download Report button under the table
        if isinstance(admin_panel_data, list):
            df_download = pd.DataFrame(admin_panel_data)
        else:
            df_download = pd.DataFrame([admin_panel_data])
        output = BytesIO()
        df_download.to_excel(output, index=False)
        output.seek(0)
        today_str = datetime.now().strftime('%Y-%m-%d')
        st.markdown(
            """
            <style>
            .stDownloadButton button {
                background-color: #2563eb !important;
                color: #fff !important;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1.1rem;
                padding: 0.75em 1.5em;
                box-shadow: 0 2px 8px 0 rgba(37,99,235,0.10);
                transition: background 0.2s;
            }
            .stDownloadButton button:hover {
                background-color: #1746a2 !important;
                color: #fff !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.download_button(
            label="Download Report",
            data=output,
            use_container_width=True,
            file_name=f"call_records_{today_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.write("***")

        # --- Beautiful KPI Cards ---
        st.markdown(
            """
            <div style='text-align: left; padding: 0.5rem 0 1rem 0;'>
                <h3 style='margin-bottom: 0.2rem; color:#2563eb;'>Key Metrics Overview</h3>
                <p style='font-size: 18px; color: #444;'>
                    Review your most important call KPIs at a glance to quickly assess performance and spot trends in your outbound campaigns.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        kpi_cols = st.columns(3)
        kpi_cols[0].markdown(f"""
            <div style="background:#fff;padding:20px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                <h4 style="color:#222;">Total Calls</h4>
                <h2 style="color:#2563eb;">{admin_panel_stats['total_calls']}</h2>
            </div>
        """, unsafe_allow_html=True)
        kpi_cols[1].markdown(f"""
            <div style="background:#fff;padding:20px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                <h4 style="color:#222;">Calls Today</h4>
                <h2 style="color:#2563eb;">{admin_panel_stats['calls_today']}</h2>
            </div>
        """, unsafe_allow_html=True)
        kpi_cols[2].markdown(f"""
            <div style="background:#fff;padding:20px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                <h4 style="color:#222;">Completed Calls</h4>
                <h2 style="color:#2563eb;">{admin_panel_stats['completed_calls']}</h2>
            </div>
        """, unsafe_allow_html=True)

        kpi_cols = st.columns(3)
        kpi_cols[0].markdown(f"""
            <div style="background:#fff;padding:20px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                <h4 style="color:#222;">Failed Calls</h4>
                <h2 style="color:#e74c3c;">{admin_panel_stats['failed_calls']}</h2>
            </div>
        """, unsafe_allow_html=True)
        kpi_cols[1].markdown(f"""
            <div style="background:#fff;padding:20px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                <h4 style="color:#222;">Total Costing</h4>
                <h2 style="color:#2563eb;">${admin_panel_stats.get('total_costing', 0.00):.2f}</h2>
            </div>
        """, unsafe_allow_html=True)
        kpi_cols[2].markdown(f"""
            <div style="background:#fff;padding:20px 10px;border-radius:10px;text-align:center;box-shadow:0 2px 8px #e5e7eb;">
                <h4 style="color:#222;">Avg. Call Duration</h4>
                <h2 style="color:#2563eb;">{admin_panel_stats['average_call_duration']}s</h2>
            </div>
        """, unsafe_allow_html=True)

        # Add horizontal space between cards and visualizations
        st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

        # --- Visualization Grid ---
        main_blue = "#2563eb"
        gray = "#e5e7eb"
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            # Pie Chart: Call Status Breakdown
            labels = list(admin_panel_stats['status_breakdown'].keys())
            values = list(admin_panel_stats['status_breakdown'].values())
            colors = [main_blue if l == 'completed' else gray for l in labels]
            fig1 = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors),
                textinfo='percent+label'
            )])
            fig1.update_layout(title_text="Call Status", showlegend=True)
            st.plotly_chart(fig1, use_container_width=True, key="status_pie")
        with col2:
            # Gauge: Call Success Rate
            fig2 = go.Figure(go.Indicator(
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
            fig2.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True, key="success_gauge")
        with col3:
            # Scatter Plot: Call Duration (Each dot = one call, arranged horizontally by call index)
            durations = [row['call_duration'] for row in admin_panel_data if row.get('call_duration') is not None]
            call_indices = list(range(1, len(durations) + 1))
            fig3 = px.scatter(
                x=call_indices,
                y=durations,
                labels={'x': 'Call #', 'y': 'Duration (seconds)'},
                color_discrete_sequence=[main_blue]
            )
            fig3.update_traces(marker=dict(size=10, opacity=0.7))
            fig3.update_layout(
                title="Call Duration per Call",
                xaxis_title="Call #",
                yaxis_title="Duration (seconds)",
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True, key="call_duration_scatter")

dashboard_page()