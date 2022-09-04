# =========================================
# H2O AutoML Training with MLflow Tracking
# Inspired from Kenneth Leung
# =========================================
# Command to execute script locally: streamlit run app.py
# Command to run Docker image: docker run -d -p 8501:8501 <streamlit-app-name>:latest

import io
import json

import database as db
import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="End-to-End AutoML Project: Insurance Cross-Sell", layout="wide")

# 

# --- USER AUTHENTICATION ---
users = db.fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

credentials = {"usernames":{}}

for un, name, pw in zip(usernames, names, hashed_passwords):
    user_dict = {"name":name,"password":pw}
    credentials["usernames"].update({un:user_dict})

authenticator = stauth.Authenticate(credentials,
    "insurance_cross_sell", "abcdef", cookie_expiry_days=30)


name, authentication_status, username = authenticator.login("Login", "sidebar")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.title('End-to-End AutoML Project: Insurance Cross-Sell')

    # ---- SIDEBAR ----
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.markdown("## Description")
    st.sidebar.markdown("""Cross-selling in insurance is the practice of promoting products that are complementary 
    to the policies that customers already own.Cross-selling creates a win-win situation where customers obtain 
    comprehensive protection at a lower bundled cost. At the same time, insurers can boost revenue through enhanced policy conversions.
    This project aims to make cross-selling more efficient and targeted by building an ML pipeline to identify health insurance customers 
    interested in purchasing additional vehicle insurance.""")

    # Set FastAPI endpoint
    endpoint = 'http://localhost:8001/predict'
    # endpoint = 'http://host.docker.internal:8001/predict' # Specify this path for Dockerization to work

    test_csv = st.file_uploader('', type=['csv'], accept_multiple_files=False)

    # Upon upload of file (to test using test.csv from data/processed folder)
    if test_csv:
        test_df = pd.read_csv(test_csv)
        st.subheader('Sample of Uploaded Dataset')
        st.write(test_df.head())

        # Convert dataframe to BytesIO object (for parsing as file into FastAPI later)
        test_bytes_obj = io.BytesIO()
        test_df.to_csv(test_bytes_obj, index=False)  # write to BytesIO buffer
        test_bytes_obj.seek(0) # Reset pointer to avoid EmptyDataError

        files = {"file": ('test_dataset.csv', test_bytes_obj, "multipart/form-data")}

        # Upon click of button
        if st.button('Start Prediction'):
            if len(test_df) == 0:
                st.write("Please upload a valid test dataset!")  # handle case with no image
            else:
                with st.spinner('Prediction in Progress. Please Wait...'):
                    output = requests.post(endpoint, 
                                        files=files,
                                        timeout=8000)
                st.success('Success! Click Download button below to get prediction results (in JSON format)')
                print(output)
                df_output = test_df.copy()
                df_output["pred"] = eval(json.dumps(output.json()))
                st.write(df_output.iloc[:, [0,1,2,3,-1]].head())
                st.download_button(
                    label='Download',
                    data=json.dumps(output.json()), # Download as JSON file object
                    file_name='automl_prediction_results.json'
                )
    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
