import streamlit as st
from utility.time_goals import main as time_goals
st.set_page_config(layout="wide")


def main():
    st.title("Life Tracker Dashboard")
    time_goals()

if __name__ == "__main__":
    main()