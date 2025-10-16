import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(page_title="Audience Tracker", page_icon="📊", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'audience_dict' not in st.session_state:
    st.session_state.audience_dict = {}

# Simple authentication (for demo - use proper auth in production)
USERS = {
    "admin": "password123",
    "user": "demo123"
}

def login_page():
    st.title("🔐 Audience Data Tracker - Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Login", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with col_btn2:
            if st.button("Demo Login", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.username = "demo_user"
                st.rerun()
        
        st.markdown("---")
        st.info("💡 Demo credentials: username=`user`, password=`demo123`")

def process_excel(uploaded_file):
    """Process uploaded Excel file and extract audience data"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Create dictionary from dataframe
        audience_dict = {}
        
        for _, row in df.iterrows():
            audience_name = row.get('Audience Name', None)
            
            if pd.notna(audience_name):
                audience_dict[str(audience_name)] = {
                    'audienceSize': int(row.get('Audience Size', 0)) if pd.notna(row.get('Audience Size', 0)) else 0,
                    'creationDate': str(row.get('Audience Creation Date', '')) if pd.notna(row.get('Audience Creation Date', '')) else '',
                    'refreshDate': str(row.get('Audience Refresh Date', '')) if pd.notna(row.get('Audience Refresh Date', '')) else ''
                }
        
        return audience_dict
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def get_changes():
    """Calculate additions and removals between last two uploads"""
    if len(st.session_state.upload_history) < 2:
        return [], []
    
    previous_dict = st.session_state.upload_history[-2]['data']
    current_dict = st.session_state.upload_history[-1]['data']
    
    previous_names = set(previous_dict.keys())
    current_names = set(current_dict.keys())
    
    added = list(current_names - previous_names)
    removed = list(previous_names - current_names)
    
    return added, removed

def main_app():
    # Header
    st.markdown(f"""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>📊 Audience Data Tracker</h1>
            <p style='color: #e0e7ff; margin: 0.5rem 0 0 0;'>Welcome, {st.session_state.username}!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    if st.button("Logout", key="logout"):
        st.session_state.logged_in = False
        st.session_state.upload_history = []
        st.session_state.audience_dict = {}
        st.rerun()
    
    # File uploader
    st.markdown("### 📁 Upload Excel File")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Expected columns: Audience Name, Audience Size, Audience Creation Date, Audience Refresh Date"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            audience_dict = process_excel(uploaded_file)
            
            if audience_dict:
                timestamp = datetime.now()
                
                # Store upload
                st.session_state.upload_history.append({
                    'data': audience_dict,
                    'timestamp': timestamp,
                    'count': len(audience_dict)
                })
                
                st.session_state.audience_dict = audience_dict
                st.success(f"✅ Successfully uploaded {len(audience_dict)} audiences!")
                st.rerun()
    
    # Display stats if data exists
    if st.session_state.upload_history:
        st.markdown("---")
        st.markdown("### 📈 Statistics")
        
        current_data = st.session_state.upload_history[-1]['data']
        added, removed = get_changes()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Audiences", len(current_data))
        
        with col2:
            st.metric("Added (Latest)", len(added), delta=len(added) if len(added) > 0 else None)
        
        with col3:
            st.metric("Removed (Latest)", len(removed), delta=f"-{len(removed)}" if len(removed) > 0 else None)
        
        with col4:
            st.metric("Total Uploads", len(st.session_state.upload_history))
        
        if st.session_state.upload_history:
            last_update = st.session_state.upload_history[-1]['timestamp']
            st.caption(f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show changes
        if added or removed:
            st.markdown("---")
            col_add, col_rem = st.columns(2)
            
            with col_add:
                if added:
                    st.markdown("#### ✅ Added Audiences")
                    for name in added:
                        st.success(f"• {name}")
            
            with col_rem:
                if removed:
                    st.markdown("#### ❌ Removed Audiences")
                    for name in removed:
                        st.error(f"• {name}")
        
        # Display dictionary
        st.markdown("---")
        st.markdown("### 📖 Audience Dictionary (Current Data)")
        
        # Display as formatted JSON
        with st.expander("View as JSON", expanded=True):
            st.json(current_data)
        
        # Display as table
        with st.expander("View as Table"):
            table_data = []
            for name, data in current_data.items():
                table_data.append({
                    'Audience Name': name,
                    'Audience Size': data['audienceSize'],
                    'Creation Date': data['creationDate'],
                    'Refresh Date': data['refreshDate']
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
        
        # Display as formatted dictionary
        with st.expander("View as Formatted Dictionary"):
            st.markdown("```python")
            for name, data in current_data.items():
                st.write(f'"{name}": {{')
                st.write(f'    "audienceSize": {data["audienceSize"]},')
                st.write(f'    "creationDate": "{data["creationDate"]}",')
                st.write(f'    "refreshDate": "{data["refreshDate"]}"')
                st.write('},')
            st.markdown("```")
        
        # Upload history
        if len(st.session_state.upload_history) > 1:
            st.markdown("---")
            st.markdown("### 📅 Upload History (First → Latest)")
            
            for idx, upload in enumerate(st.session_state.upload_history):
                with st.expander(f"Upload #{idx + 1} - {upload['count']} audiences - {upload['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
                    if st.button(f"View Upload #{idx + 1}", key=f"view_{idx}"):
                        st.session_state.audience_dict = upload['data']
                        st.rerun()
                    
                    st.json(upload['data'])

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
