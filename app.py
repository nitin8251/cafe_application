import streamlit as st
import os
import shutil
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & SETUP ---
UPLOAD_ROOT = "cafe_uploads"

# Ensure the main upload directory exists
if not os.path.exists(UPLOAD_ROOT):
    os.makedirs(UPLOAD_ROOT)

def cleanup_old_folders():
    """Deletes folders older than 2 days to save space."""
    # Calculate the cutoff date (anything before 2 days ago is deleted)
    cutoff_date = datetime.now() - timedelta(days=2)
    
    if os.path.exists(UPLOAD_ROOT):
        for folder_name in os.listdir(UPLOAD_ROOT):
            folder_path = os.path.join(UPLOAD_ROOT, folder_name)
            
            # We only want to process directories
            if os.path.isdir(folder_path):
                try:
                    # Convert folder name string (YYYY-MM-DD) to a date object
                    folder_date = datetime.strptime(folder_name, "%Y-%m-%d")
                    
                    # Deletion logic
                    if folder_date < cutoff_date:
                        shutil.rmtree(folder_path)
                except ValueError:
                    # If a folder isn't named as a date, ignore it
                    continue

# Run the cleanup every time the app is refreshed
cleanup_old_folders()

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title="Cafe File Portal", page_icon="☕", layout="wide")

# Custom CSS to make it look clean
# Change the line below from unsafe_allow_stdio to unsafe_allow_html
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)
# --- 3. CUSTOMER UPLOAD SECTION ---
st.title("☕ Cafe Customer File Upload")
st.write("Welcome! Please enter your name and upload your files. Files are stored for 48 hours.")

with st.form("upload_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        customer_name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
    with col2:
        uploaded_files = st.file_uploader("Choose Files", accept_multiple_files=True)
    
    submit_button = st.form_submit_button("Submit to Cafe")

    if submit_button:
        if not customer_name:
            st.error("⚠️ Please enter your name.")
        elif not uploaded_files:
            st.error("⚠️ Please select at least one file.")
        else:
            # Folder for TODAY
            today_str = datetime.now().strftime("%Y-%m-%d")
            target_dir = os.path.join(UPLOAD_ROOT, today_str)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for f in uploaded_files:
                # File Prefix: HH-MM-SS
                time_prefix = datetime.now().strftime("%H-%M-%S")
                clean_name = customer_name.replace(" ", "_")
                final_filename = f"{time_prefix}_{clean_name}_{f.name}"
                
                # Save the file
                file_path = os.path.join(target_dir, final_filename)
                with open(file_path, "wb") as save_file:
                    save_file.write(f.getbuffer())
                
                st.success(f"✅ Saved: {final_filename}")
            st.balloons()

# --- 4. MANAGER DASHBOARD (SIDEBAR) ---
st.sidebar.title("🛠 Manager Dashboard")
st.sidebar.markdown("---")

# Show today's files by default
today_folder = datetime.now().strftime("%Y-%m-%d")
today_path = os.path.join(UPLOAD_ROOT, today_folder)

if os.path.exists(today_path):
    st.sidebar.subheader(f"Today's Files ({today_folder})")
    files_list = os.listdir(today_path)
    
    if files_list:
        for file_name in files_list:
            file_path = os.path.join(today_path, file_name)
            with open(file_path, "rb") as f:
                st.sidebar.download_button(
                    label=f"📥 {file_name}",
                    data=f,
                    file_name=file_name,
                    key=file_name # Unique key for Streamlit
                )
    else:
        st.sidebar.write("No files uploaded today.")
else:
    st.sidebar.write("Waiting for today's first upload...")

# Show storage info
total_folders = len([name for name in os.listdir(UPLOAD_ROOT) if os.path.isdir(os.path.join(UPLOAD_ROOT, name))])
st.sidebar.markdown("---")
st.sidebar.write(f"📁 Folders in storage: **{total_folders}**")
st.sidebar.caption("Older folders are deleted automatically.")