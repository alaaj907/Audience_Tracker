
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(page_title="Audience Tracker", page_icon="📊", layout="wide")

# Team Members Authentication
USERS = {
    "admin": "password123",
    "Alaa": "alaa123",
    "Ashley": "beyonce101",
    "Flora": "truffle",
    "Tom": "excel101",
    "Sebastian": "databricks101",
}

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_data' not in st.session_state:
    # Store data separately for each user
    st.session_state.user_data = {user: {'upload_history': [], 'audience_dict': {}} for user in USERS.keys()}

def get_user_data():
    """Get current user's data"""
    return st.session_state.user_data[st.session_state.username]

def update_user_data(upload_history, audience_dict):
    """Update current user's data"""
    st.session_state.user_data[st.session_state.username]['upload_history'] = upload_history
    st.session_state.user_data[st.session_state.username]['audience_dict'] = audience_dict

def login_page():
    st.title("🔐 Audience Data Tracker - Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        username = st.selectbox(
            "Select Your Name",
            options=list(USERS.keys()),
            key="login_username"
        )
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid password")
        
        st.markdown("---")

def process_excel(uploaded_file):
    """Process uploaded Excel file and extract audience data"""
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)
        
        # Show debug info
        st.write("**📋 File Info:**")
        st.write(f"- Total rows: {len(df)}")
        st.write(f"- Columns found: {list(df.columns)}")
        
        # Show first few rows
        with st.expander("View first 3 rows of your file"):
            st.dataframe(df.head(3))
        
        # Clean column names (strip whitespace and make case-insensitive matching)
        df.columns = df.columns.str.strip()
        
        # Try to find the columns (case-insensitive)
        col_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'audience name' in col_lower or col_lower == 'name':
                col_mapping['audience_name'] = col
            elif 'audience size' in col_lower or col_lower == 'size':
                col_mapping['audience_size'] = col
            elif 'creation date' in col_lower or 'created' in col_lower:
                col_mapping['creation_date'] = col
            elif 'refresh date' in col_lower or 'refreshed' in col_lower:
                col_mapping['refresh_date'] = col
        
        st.write(f"**✅ Columns matched:** {col_mapping}")
        
        # Check if we found the audience name column
        if 'audience_name' not in col_mapping:
            st.error("❌ Could not find 'Audience Name' column. Please make sure your Excel file has a column named 'Audience Name'")
            return None
        
        # Create dictionary from dataframe
        audience_dict = {}
        
        for _, row in df.iterrows():
            audience_name = row.get(col_mapping['audience_name'], None)
            
            if pd.notna(audience_name):
                audience_dict[str(audience_name)] = {
                    'audienceSize': int(row.get(col_mapping.get('audience_size', ''), 0)) if pd.notna(row.get(col_mapping.get('audience_size', ''), 0)) else 0,
                    'creationDate': str(row.get(col_mapping.get('creation_date', ''), '')) if pd.notna(row.get(col_mapping.get('creation_date', ''), '')) else '',
                    'refreshDate': str(row.get(col_mapping.get('refresh_date', ''), '')) if pd.notna(row.get(col_mapping.get('refresh_date', ''), '')) else ''
                }
        
        if len(audience_dict) == 0:
            st.warning("⚠️ No valid audience data found. Check if 'Audience Name' column has data.")
            return None
        
        st.write(f"**🎉 Successfully extracted {len(audience_dict)} audiences!**")
        
        return audience_dict
    
    except ImportError:
        st.error("⚠️ Missing dependency! Please install openpyxl:")
        st.code("pip install openpyxl")
        st.info("After installing, restart the Streamlit app.")
        return None
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.write("Full error details:")
        st.exception(e)
        return None

def get_changes(upload_history):
    """Calculate additions and removals between last two uploads"""
    if len(upload_history) < 2:
        return [], []
    
    previous_dict = upload_history[-2]['data']
    current_dict = upload_history[-1]['data']
    
    previous_names = set(previous_dict.keys())
    current_names = set(current_dict.keys())
    
    added = list(current_names - previous_names)
    removed = list(previous_names - current_names)
    
    return added, removed

def main_app():
    # Get current user's data
    user_data = get_user_data()
    upload_history = user_data['upload_history']
    audience_dict = user_data['audience_dict']
    
    # Header
    st.markdown(f"""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>📊 Audience Data Tracker</h1>
            <p style='color: #e0e7ff; margin: 0.5rem 0 0 0;'>Welcome, {st.session_state.username}! (Your private workspace)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # Show audience count at the top
    if audience_dict:
        st.markdown("### 📊 Your Audience Count")
        st.metric("Total Audiences", len(audience_dict), label_visibility="visible")
        
        if upload_history:
            last_update = upload_history[-1]['timestamp']
            st.caption(f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
    
    # File uploader
    st.markdown("### 📁 Upload Excel File")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Expected columns: Audience Name, Audience Size, Audience Creation Date, Audience Refresh Date"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            new_audience_dict = process_excel(uploaded_file)
            
            if new_audience_dict:
                timestamp = datetime.now()
                
                # Store upload in user's private data
                upload_history.append({
                    'data': new_audience_dict,
                    'timestamp': timestamp,
                    'count': len(new_audience_dict)
                })
                
                # Update user's data
                update_user_data(upload_history, new_audience_dict)
                
                st.success(f"✅ Successfully uploaded {len(new_audience_dict)} audiences!")
                st.rerun()
    
    # Display changes if there's history
    if len(upload_history) > 1:
        added, removed = get_changes(upload_history)
        
        if added or removed:
            st.markdown("### 📈 Changes from Last Upload")
            
            col_add, col_rem = st.columns(2)
            
            with col_add:
                if added:
                    st.success(f"**✅ Added: {len(added)}**")
                    for name in added:
                        st.write(f"• {name}")
            
            with col_rem:
                if removed:
                    st.error(f"**❌ Removed: {len(removed)}**")
                    for name in removed:
                        st.write(f"• {name}")
            
            st.markdown("---")
    
    # Display dictionary
    if audience_dict:
        st.markdown("### 📖 Your Audience Dictionary")
        
        # Display as formatted JSON
        with st.expander("View as JSON Format", expanded=True):
            st.json(audience_dict)
        
        # Display as table
        with st.expander("View as Data Table"):
            table_data = []
            for name, data in audience_dict.items():
                table_data.append({
                    'Audience Name': name,
                    'Audience Size': data['audienceSize'],
                    'Creation Date': data['creationDate'],
                    'Refresh Date': data['refreshDate']
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Display as formatted dictionary code
        with st.expander("View as Python Dictionary"):
            dict_str = "{\n"
            for idx, (name, data) in enumerate(audience_dict.items()):
                dict_str += f'    "{name}": {{\n'
                dict_str += f'        "audienceSize": {data["audienceSize"]},\n'
                dict_str += f'        "creationDate": "{data["creationDate"]}",\n'
                dict_str += f'        "refreshDate": "{data["refreshDate"]}"\n'
                dict_str += '    }' + (',' if idx < len(audience_dict) - 1 else '') + '\n'
            dict_str += "}"
            st.code(dict_str, language="python")
        
        # Upload history
        if len(upload_history) > 1:
            st.markdown("---")
            st.markdown("### 📅 Your Upload History (First → Latest)")
            
            for idx, upload in enumerate(upload_history):
                with st.expander(f"Upload #{idx + 1} - {upload['count']} audiences - {upload['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
                    if st.button(f"Load This Upload", key=f"view_{idx}"):
                        update_user_data(upload_history, upload['data'])
                        st.rerun()
                    
                    st.json(upload['data'])
    else:
        st.info("👆 Upload an Excel file to get started!")

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
