"""Public professional profile for Smart Inventory Analytics.
Place this file at pages/1_About_Me.py in the same repository as app.py.
"""
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="About Me | Hongyu Pan", page_icon="👤", layout="wide")

EMAIL = "1192335104@qq.com"
GITHUB = "https://github.com/sharkie-204218"
DEMO = "https://smart-inventory-analytics.streamlit.app"

st.title("Hongyu Pan")
st.caption("International Business Postgraduate | Supply Chain Operations · Business Analytics · AI-Assisted Development")
st.write("""I am an International Business postgraduate with hands-on experience in inventory reconciliation,
order coordination, logistics planning, and cross-functional project support. I enjoy translating
operational business challenges into practical, data-driven tools.""")

left, right = st.columns(2)
with left:
    st.subheader("Education")
    st.markdown("**CAITEC × UIBE — Graduate studies (2026–Present)**")
    st.write("International Business; coursework includes cross-border logistics, digital trade and business quantitative analysis.")
    st.markdown("**Chongqing Technology and Business University (2022–2026)**")
    st.write("B.A. in International Business")
with right:
    st.subheader("Focus Areas")
    st.markdown("- Inventory & supply chain operations\n- Business data analysis\n- Project coordination\n- AI-assisted application development")

st.divider()
st.subheader("Industry Experience")
st.markdown("**Chongqing Shangran Medical Equipment Co., Ltd. | Apr–Jun 2026**")
st.write("Supported warehouse stock counts, inventory ledger reconciliation, data verification, bidding documentation and project progress tracking.")
st.markdown("**Xinjiang Wujiaqu Jiuxinjun Carton Packaging Co., Ltd. | Oct 2025–Jan 2026**")
st.write("Supported raw-material order follow-up, logistics research, freight comparisons and transportation planning.")

st.divider()
st.subheader("Featured Project · Smart Inventory Analytics")
st.write("A deployed inventory analytics dashboard featuring inventory KPIs, category and stock visualizations, low-stock alerts, purchasing/sales trends and rule-based replenishment planning. Built using simulated data and AI-assisted coding.")
st.link_button("Open Live Dashboard", DEMO)
st.link_button("View GitHub", GITHUB)

st.divider()
st.subheader("Contact & Resume")
st.markdown(f"**Professional email:** [{EMAIL}](mailto:{EMAIL})")
resume_path = Path(__file__).resolve().parents[1] / "assets" / "Hongyu_Pan_Public_Resume.pdf"
if resume_path.is_file():
    st.download_button(
        "Download Public English Resume (PDF)",
        data=resume_path.read_bytes(),
        file_name="Hongyu_Pan_Public_Resume.pdf",
        mime="application/pdf",
    )
else:
    st.warning("Resume PDF not found. Upload assets/Hongyu_Pan_Public_Resume.pdf to enable downloads.")
st.caption("Public portfolio: simulated project data. No personal phone number is displayed.")
