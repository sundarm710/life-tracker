import streamlit as st
import psutil
import platform
from datetime import datetime
import logging
import threading

st.set_page_config(layout="wide")

# Set up logging
logging.basicConfig(filename='uptime.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def log_timestamp():
    logging.info("Application is running")
    # Schedule the next log in 5 minutes
    threading.Timer(300, log_timestamp).start()

# Start the logging timer
log_timestamp()

st.title("Hello World")
st.write("This is a simple Streamlit app.")

st.markdown("## Hi TV. This is Sundar from the other side.")

def get_system_stats():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    stats = {
        "Uptime": str(uptime).split('.')[0],
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "Memory Usage": f"{psutil.virtual_memory().percent}%",
        "Disk Space": f"{psutil.disk_usage('/').percent}%"
    }
    return stats

# In your dashboard
stats = get_system_stats()
col1, col2 = st.columns(2)
col1.metric("Uptime", stats["Uptime"])
col2.metric("CPU", stats["CPU Usage"])

col3, col4 = st.columns(2)
col3.metric("Memory", stats["Memory Usage"])
col4.metric("Disk", stats["Disk Space"])
