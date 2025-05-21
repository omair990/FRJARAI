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
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.interpolate import make_interp_spline
    import streamlit as st
    import gc

    labels = ["Min", "Average", "Max", "Today"]
    values = [min_price, average_price, max_price, today_price]
    colors = {
        "Min": "#dc3545",      # Red
        "Average": "#ff9900",  # Orange
        "Max": "#28a745",      # Green
        "Today": "#007bff"     # Blue
    }

    x = np.arange(len(labels))
    y = np.array(values)

    x_smooth = np.linspace(x.min(), x.max(), 300)
    y_smooth = make_interp_spline(x, y, k=3)(x_smooth)

    fig, ax = plt.subplots(figsize=(7, 4.5))

    # Smooth trend line
    ax.plot(x_smooth, y_smooth, color="#0E3152", linewidth=2)

    # Draw points and dashed lines
    for i, (label, val) in enumerate(zip(labels, values)):
        ax.scatter(x[i], val, s=130, color=colors[label], zorder=5)
        ax.axhline(y=val, color=colors[label], linestyle="--", linewidth=1.2, alpha=0.6)

    # 📌 Draw all value labels separately (top-right, evenly staggered)
    base_y = max(values) + 4  # Start top position
    spacing = 2.0             # Vertical space between labels

    for i, (label, val) in enumerate(zip(labels, values)):
        ax.text(
            x[-1] + 0.4,
            base_y - i * spacing,
            f"{label}: {val:.2f} SAR",
            va='center',
            fontsize=10,
            color=colors[label],
            fontweight='bold'
        )

    # 📈 Percentage change from average
    if average_price:
        diff = today_price - average_price
        percent = (diff / average_price) * 100
        if abs(percent) >= 0.05:
            color = "#007e5b" if diff > 0 else "#c9302c"
            sign = "+" if diff > 0 else "-"
            ax.annotate(
                f"{sign}{abs(percent):.1f}%",
                (x[3], today_price),
                xytext=(0, 20),
                textcoords="offset points",
                ha="center",
                fontsize=12,
                fontweight="bold",
                color=color,
                bbox=dict(facecolor='white', edgecolor='none', pad=2)
            )

    # Styling
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(min(values) - 5, max(values) + 12)
    ax.set_title("Material Price Trend", fontsize=14, fontweight='bold', color="#0E3152")
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    ax.spines[['top', 'right']].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)
    gc.collect()

    # 🧠 AI Price Note
    st.markdown(
        """
        <div style='
            background-color: #f1f1f1;
            padding: 10px 14px;
            border-left: 4px solid #0E3152;
            border-radius: 5px;
            font-size: 13px;
            color: #333;
            margin-top: 10px;
        '>
        <strong>ℹ️ AI Estimate:</strong> These prices are estimated using historical and market data to assist your decision-making.
        </div>
        """,
        unsafe_allow_html=True
    )


