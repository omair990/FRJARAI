import plotly.graph_objects as go
import streamlit as st
import gc


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

def draw_price_chart(today_price, average_price, min_price, max_price, dark_mode=False):
    labels = ["Min", "Average", "Max", "Today"]
    values = [min_price or 0, average_price or 0, max_price or 0, today_price or 0]

    point_colors = {
        "Min": "#FF4B4B",       # Red
        "Average": "#17BECF",   # Teal
        "Max": "#FFB347",       # Orange
        "Today": "#28A745"      # Green
    }

    line_color = "#0E3152"

    # Theme settings
    background = "#111111" if dark_mode else "#FFFFFF"
    font_color = "#FFFFFF" if dark_mode else "#111111"
    grid_color = "#333333" if dark_mode else "rgba(0,0,0,0.05)"
    label_text_color = "#FFFFFF" if dark_mode else "#000000"

    fig = go.Figure()

    # Main line (no hover, no text)
    fig.add_trace(go.Scatter(
        x=labels,
        y=values,
        mode="lines",
        line=dict(color=line_color, width=3),
        hoverinfo="skip",
        showlegend=False
    ))

    # Points with text
    for i, label in enumerate(labels):
        fig.add_trace(go.Scatter(
            x=[label],
            y=[values[i]],
            mode="markers+text",
            name=label,
            marker=dict(size=16, color=point_colors[label], line=dict(width=2, color='white')),
            text=[f"{values[i]:,.2f} SAR"],
            textposition="top center",
            textfont=dict(size=12, color=label_text_color),
            hovertemplate=f"<b>{label} Price</b><br>{values[i]:,.2f} SAR<extra></extra>"
        ))

    # Layout styling
    fig.update_layout(
        title=dict(
            text="📊 <b>Material Price Breakdown</b>",
            font=dict(size=20, color=font_color)
        ),
        xaxis=dict(
            title=dict(text="Price Type", font=dict(size=14, color=font_color)),
            tickfont=dict(size=12, color=font_color),
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="Price in SAR", font=dict(size=14, color=font_color)),
            tickfont=dict(size=12, color=font_color),
            gridcolor=grid_color
        ),
        plot_bgcolor=background,
        paper_bgcolor=background,
        font=dict(color=font_color),
        height=450,
        margin=dict(l=50, r=50, t=70, b=40),
        legend=dict(font=dict(color=font_color))
    )

    st.plotly_chart(fig, use_container_width=True)
    del fig  # 🧹 Clear memory
    gc.collect()