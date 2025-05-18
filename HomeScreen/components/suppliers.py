import streamlit as st

def render_suppliers_tabs(product, selected_city):
    suppliers = product.get("suppliers", [])
    second_layer = product.get("second_layer_wholesale_suppliers", [])
    retail = product.get("retail_suppliers", [])
    all_wholesale = suppliers + second_layer

    # Filter by city
    filtered_wholesale = _filter_by_city(all_wholesale, selected_city)
    filtered_retail = _filter_by_city(retail, selected_city)

    tabs = st.tabs([
        f"🏢 Wholesale Suppliers ({len(filtered_wholesale)})",
        f"🛒 Retail Suppliers ({len(filtered_retail)})"
    ])

    with tabs[0]:
        _render_supplier_list(filtered_wholesale, highlight_color="#4db8ff")
    with tabs[1]:
        _render_supplier_list(filtered_retail, highlight_color="#ffcc00")

def _filter_by_city(suppliers, selected_city):
    if selected_city == "National Average":
        return suppliers
    return [s for s in suppliers if selected_city.lower() in s.get("location", "").lower()]

def _render_supplier_list(suppliers, highlight_color):
    if not suppliers:
        st.info("No suppliers listed.")
        return

    for sup in suppliers:
        name = sup.get("name", "—")
        loc = sup.get("location", "—")
        desc = sup.get("description", "")
        website = sup.get("website")
        email = sup.get("email")
        sales_email = sup.get("sales_email")
        phone = sup.get("phone")

        contact_html = ""
        if email:
            contact_html += f"<p>📧 <strong>Email:</strong> <a href='mailto:{email}' style='color:{highlight_color};'>{email}</a></p>"
        if sales_email:
            contact_html += f"<p>📧 <strong>Sales Email:</strong> <a href='mailto:{sales_email}' style='color:{highlight_color};'>{sales_email}</a></p>"
        if phone:
            contact_html += f"<p>📞 <strong>Phone:</strong> <a href='tel:{phone}' style='color:{highlight_color};'>{phone}</a></p>"
        if not contact_html:
            contact_html = "<p style='color:#888;'>No contact information available.</p>"

        st.markdown(f"""
        <div style="border:2px solid #444; border-radius:10px; padding:12px; margin-bottom:10px; background-color:#222;">
            <strong style="font-size:17px; color:{highlight_color};">{name}</strong><br>
            <span style="color:#ccc;">📍 {loc}</span><br>
            <em style="color:#aaa;">{desc}</em><br><br>
            {"🌐 <a href='" + website + "' target='_blank' style='color:{highlight_color};'>Visit Website</a><br>" if website else ""}
            {contact_html}
        </div>
        """, unsafe_allow_html=True)
