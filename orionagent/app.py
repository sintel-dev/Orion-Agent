from openai import OpenAI
import random
import plotly.express as px
import pandas as pd
import streamlit as st

from plot import generate_time_series_chart, plot_dataframe
from agents import execute_code, OpenAILLM

import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

st.title("Orion Agent")

# Add file uploader for CSV
uploaded_file = st.file_uploader("Upload a CSV file containing your time series data", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded CSV Data:")
    st.write(df)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "plot generic" in prompt.lower():
            response = "Here's a plot"
            st.write(response)
            fig = generate_time_series_chart()
            st.plotly_chart(fig)

        elif "plot" in prompt.lower():
            if uploaded_file is None:
                response = "Please upload a CSV file first"
                st.write(response)
            else:
                response = "Here's a plot"
                column_mapping_prompt = f"""
                    Given the a csv file that has the following columns: 
                    {str(df.columns.tolist())}
                    which columns represent the time and which one represents the value?
                    return the output as a json object with the following format:
                    {{
                        "time_column": "the name of the time column",
                        "value_column": "the name of the value column"
                    }}
                    do not include any other text in your response.
                """
                column_mapping_response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[{"role": "system", "content": column_mapping_prompt}],
                    response_format={"type": "json_object"}
                )
                column_mapping_response = eval(column_mapping_response.choices[0].message.content)
                time_column = column_mapping_response['time_column']
                value_column = column_mapping_response['value_column']
                fig = plot_dataframe(df, time_column, value_column)
                st.plotly_chart(fig)

        elif "number of rows" in prompt.lower():
            response = f"The number of rows in the uploaded CSV file is {len(df)}"
            st.write(response)

        elif 'detect anomalies' in prompt.lower():
            anomaly_detector = OpenAILLM(client=client)

            if uploaded_file:
                prompt += f'Load the dataframe using csv file : {uploaded_file} '

            st.write('Generating code to perform rag task')
            response_code = anomaly_detector.run_rag(prompt)
            with st.expander("View generated code and execution status"):
                st.write(response_code)

            st.write('Executing code')
            status, anomalies = execute_code(response_code, 'anomalies')
            st.write("execution success", status)
            
            if len(anomalies):
                st.write('Detected anomalies')
                st.write(anomalies)
            else:
                st.write('No anomalies detected')
            response = anomalies


        else:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
