import streamlit as st
import zipfile
import os
import json
import pandas as pd
from datetime import datetime
import shutil

# Set the title of the app
st.title("They Don't Follow You Back")

# Create a file uploader component
uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False, type=['json', 'html', 'zip'])

# Display the uploaded file
if uploaded_file is not None:
    st.write("File uploaded successfully!")
    
    if uploaded_file.type == "application/x-zip-compressed":
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall("data/processed")
            st.write("Files extracted successfully!")
            
            # Check for the required files
            followers_path = os.path.join("data/processed", "connections", "followers_and_following", "followers_1.json")
            following_path = os.path.join("data/processed", "connections", "followers_and_following", "following.json")
            
            if os.path.exists(followers_path) and os.path.exists(following_path):
                st.write("Required files are present.")
                
                # Load JSON data
                with open(followers_path, 'r') as f:
                    followers_data = json.load(f)
                with open(following_path, 'r') as f:
                    following_data = json.load(f)
                
                # Extract followers and following
                followers = {item['string_list_data'][0]['value'] for item in followers_data}
                following = [
                    {
                        'href': item['string_list_data'][0]['href'],
                        'value': item['string_list_data'][0]['value'],
                        'timestamp': item['string_list_data'][0]['timestamp']
                    }
                    for item in following_data['relationships_following']
                ]
                
                # Find users in following but not in followers
                not_following_back = [user for user in following if user['value'] not in followers]
                
                # Create DataFrame
                df = pd.DataFrame(not_following_back)
                
                # Convert timestamp to date and sort by most recent
                df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
                df = df.sort_values(by='date', ascending=False)
                
                # Drop the timestamp column
                df = df.drop(columns=['timestamp'])
                
                st.subheader("Those bastards...")

                # Display DataFrame with links and nice column names
                st.data_editor(
                    df,
                    column_config={
                        "href": st.column_config.LinkColumn(
                            "Profile Link",
                            display_text="Open Profile"
                        ),
                        "value": "Bastard username",
                        "date": "Date Followed"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.write("Required files are missing.")
    else:     
        st.write(uploaded_file)

# Add a button to end the session and delete all received files
if st.button("End Session"):
    shutil.rmtree("data/processed")
    st.write("Session ended and all files deleted.")


