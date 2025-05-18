import streamlit as st
import matplotlib.pyplot as plt

def get_color(val, ref):
    return "green" if val > ref else "red" if val < ref else "gray"

def render_price_cards(min_price, max_price, avg, today_price, unit, city="National Average"):
    st.markdown("""
    <style>
    .stat-block {
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        height: 100px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .stat-label {
        font-size: 14px;
        font-weight: 600;
        margin-top: 6px;
        display: block;
    }
    .green { background: #e0f8f1; color: #007e5b; border: 2px solid #9fe1cd; }
    .red { background: #fdeceb; color: #c9302c; border: 2px solid #f5b9b8; }
    .gray { background: #f3f3f3; color: #333; border: 2px solid #ccc; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"##### 📍 City: **{city}**")

    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown(
                f"<div class='stat-block {get_color(min_price, avg)}'>{min_price:.2f} SAR<span class='stat-label'>Min Price</span></div><br>",
                unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"<div class='stat-block {get_color(max_price, avg)}'>{max_price:.2f} SAR<span class='stat-label'>Max Price</span></div><br>",
                unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"<div class='stat-block gray'>{avg:.2f} SAR<span class='stat-label'>Average</span></div><br>",
                unsafe_allow_html=True)
        with col4:
            if today_price:
                st.markdown(
                    f"<div class='stat-block green'>{today_price:.2f} SAR<span class='stat-label'>Estimated Price Today</span></div><br>",
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div class='stat-block red'>—<span class='stat-label'>Estimated Price Today</span></div><br>",
                    unsafe_allow_html=True)
        with col5:
            st.markdown(
                f"<div class='stat-block gray'>{unit}<span class='stat-label'>Unit</span></div><br>",
                unsafe_allow_html=True)


def draw_price_chart(today_price, average_price):
    labels = ["Average Price", "Estimated Today Price"]
    values = [average_price or 0, today_price or 0]
    colors = ["#a9c5bc", "#275e56"]

    diff = values[1] - values[0]
    percent = (diff / values[0]) * 100 if values[0] else 0

    fig, ax = plt.subplots(figsize=(5.8, 4))
    bars = ax.bar(labels, values, color=colors, width=0.5)

    max_val = max(values) or 1

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + (max_val * 0.015),
                f"{yval:.2f} SAR", ha='center', va='bottom', fontsize=11)

    if abs(percent) >= 0.05:
        color = "#007e5b" if diff > 0 else "#c9302c"
        ax.text(
            1 + 0.05,
            max_val * 1.11,
            f"{abs(percent):.1f}%",
            color=color,
            ha='left',
            fontsize=13,
            fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', pad=2)
        )

    ax.set_ylim(0, max_val * 1.15)
    ax.set_title("Estimated Today Price vs Average", fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines[['top', 'right']].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)
