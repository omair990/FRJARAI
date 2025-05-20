import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.interpolate import make_interp_spline
import gc  # ✅ Required for memory cleanup

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


def draw_price_chart(min_price, average_price, max_price, today_price):
    labels = ["Min", "Average", "Max", "Today"]
    values = [min_price, average_price, max_price, today_price]  # ✔️ must match label order

    point_colors = {
        "Min": "#dc3545",      # red
        "Average": "#ff9900",  # orange
        "Max": "#28a745",      # green
        "Today": "#007bff"     # blue
    }

    x = np.arange(len(labels))
    y = np.array(values)

    # Smooth curved line
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spline = make_interp_spline(x, y, k=3)
    y_smooth = spline(x_smooth)

    # Calculate % difference from Average
    diff = today_price - average_price
    percent = (diff / average_price) * 100 if average_price else 0

    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Plot the smooth line
    ax.plot(x_smooth, y_smooth, color="#0E3152", linewidth=2.5)

    # Draw all points with colored markers
    for i, (label, val) in enumerate(zip(labels, values)):
        ax.scatter(x[i], val, s=160, color=point_colors[label], edgecolors='white', linewidth=2, zorder=5)

    # 🎯 Today price label (right of dot)
    ax.annotate(
        f"{today_price:,.2f} SAR",
        (x[3], today_price),
        xytext=(8, -20),  # ➡️ Right side, slightly below center
        textcoords='offset points',
        ha='left',
        fontsize=11,
        fontweight='bold',
        color='#000'
    )

    # 📈 Percentage difference from average (above dot)
    diff = today_price - average_price
    percent = (diff / average_price) * 100 if average_price else 0

    if abs(percent) >= 0.05:
        color = "#007e5b" if diff > 0 else "#c9302c"
        sign = "+" if diff > 0 else "-"
        ax.annotate(
            f"{sign}{abs(percent):.1f}%",
            (x[3], today_price),
            xytext=(0, 22),  # ⬆️ Above the dot
            textcoords='offset points',
            ha='center',
            fontsize=13,
            fontweight='bold',
            color=color,
            bbox=dict(facecolor='white', edgecolor='none', pad=2)
        )

    # Style
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    y_padding = (max(values) - min(values)) * 0.2
    ax.set_ylim(min(values) - y_padding * 0.5, max(values) + y_padding * 1.5)
    ax.set_title("Material Price Trend", fontsize=15, fontweight='bold', color="#0E3152")
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines[['top', 'right']].set_visible(False)

    # Render
    st.pyplot(fig)
    plt.close(fig)
    del fig
    gc.collect()
    # 📌 AI-based price estimation note
    st.markdown(
        """
        <div style='
            background-color: #f8f9fa;
            padding: 12px 16px;
            border-left: 4px solid #0E3152;
            border-radius: 6px;
            font-size: 14px;
            color: #333;
            margin-top: 12px;
        '>
        <strong>ℹ️ Note:</strong> The prices displayed are <strong>AI-generated estimates</strong> based on historical data and market trends for informational purposes.
        </div>
        """,
        unsafe_allow_html=True
    )

