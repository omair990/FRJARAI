import streamlit as st
import matplotlib.pyplot as plt

def make_sparkline(data):
    if not data or not isinstance(data, list):
        return
    fig, ax = plt.subplots(figsize=(2, 0.5))
    ax.plot(data, linewidth=2)
    ax.axis('off')
    st.pyplot(fig)
