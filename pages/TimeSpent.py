import streamlit as st
from utility.time_spent import main as time_spent
st.set_page_config(layout="wide")


def main():
    st.title("Life Tracker Dashboard")
    time_spent()

if __name__ == "__main__":
    main()