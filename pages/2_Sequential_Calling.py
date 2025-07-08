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
from src.validations import validate_calling_file

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
        <h2 style='margin-bottom: 0.5rem;'>📞 Sequential Calling Module</h2>
    </div>
    """,
    unsafe_allow_html=True
)

    st.success(
        """
- The file must be either csv, xls or xlsx
- The file must have columns : Tag Type, Contact Number, Contact Name, Contact Email
- There must be 70 rows in the file at most as current plan of BlandAI supports 70 calls a day.
        """
    )

    uploaded_file = st.file_uploader("Upload your calling file", type=["csv", "xls", "xlsx"])
    st.write("***")
    df = None
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file, dtype={'Contact Number': str})
        else:
            st.error("Invalid file type. Please upload a CSV, XLS, or XLSX file.")

        # Creaitng 2 sections for the file and the validation messages
        col1, col2 = st.columns([2,1], gap="large")
        with col1:
            st.dataframe(df)
        with col2:
            if uploaded_file is not None:
                validation_messages = []
                success_messages = []
                if validate_calling_file(df, success_messages, validation_messages):
                    for message in success_messages:
                        st.success(message)
                        time.sleep(0.5)
                    st.success("File uploaded successfully!")

                    # Add a custom-styled Start Calling button
                    st.markdown(
                        """
                        <style>
                        .start-calling-btn button {
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
                        .start-calling-btn button:hover {
                            background-color: #1746a2 !important;
                            color: #fff !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    start_calling = st.button("Start Calling", key="start_calling_btn", use_container_width=True, help="Begin the sequential calling process.", type="primary")
                    if start_calling:
                        st.info("Calling process started!")
                else:
                    for message in validation_messages:
                        st.error(message)
            else:
                st.info("Please upload a file to start the calling process")

    # Add extra bottom padding to ensure space below the page content and button
    st.markdown("<div style='height: 64px;'></div>", unsafe_allow_html=True)

dashboard_page()