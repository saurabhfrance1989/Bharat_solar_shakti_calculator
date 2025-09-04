import streamlit as st
import pandas as pd
from fpdf2 import FPDF

# -----------------------------
# Load lookup tables
# -----------------------------
panel_prices = pd.read_excel("UP_Residential_Solar_Quotation_Final.xlsx", sheet_name="PanelPriceTable")
inverter_prices = pd.read_excel("UP_Residential_Solar_Quotation_Final.xlsx", sheet_name="InverterPriceTable")
battery_prices = pd.read_excel("UP_Residential_Solar_Quotation_Final.xlsx", sheet_name="BatteryPriceTable")

panel_dict = dict(zip(panel_prices["Brand"], panel_prices["PricePerW"]))
inverter_dict = dict(zip(inverter_prices["Brand"], inverter_prices["Price"]))
battery_dict = dict(zip(battery_prices["Brand"], battery_prices["PricePerkWh"]))

# -----------------------------
# Streamlit Page Setup
# -----------------------------
st.set_page_config(page_title="Solar Quotation - Bharat Solar Shakti",  layout="wide")

# Branding
st.markdown("<h1 style='text-align: center; color: #FF9900;'> Bharat Solar Shakti Pvt Ltd</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Your trusted partner for clean & affordable solar energy</h4>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("📥 Customer Details")

customer_name = st.sidebar.text_input("Customer Name", "Demo User")
monthly_bill = st.sidebar.number_input("Average Monthly Bill (₹)", min_value=500, max_value=50000, value=4000)
tariff = st.sidebar.number_input("DISCOM Tariff (₹/unit)", min_value=1.0, max_value=15.0, value=7.5, step=0.1)

st.sidebar.header("⚙️ System Configuration")
system_type = st.sidebar.selectbox("System Type", ["On-Grid", "Off-Grid", "Hybrid"])
panel_brand = st.sidebar.selectbox("Panel Brand", list(panel_dict.keys()))
inverter_brand = st.sidebar.selectbox("Inverter Brand", list(inverter_dict.keys()))
battery_brand = st.sidebar.selectbox("Battery Brand", list(battery_dict.keys()))

# -----------------------------
# Calculations
# -----------------------------
units = monthly_bill / tariff
system_kw = int(-(-units // 120))   # ceiling division
roof_size = system_kw * 100

panel_cost = system_kw * 1000 * panel_dict[panel_brand]
inverter_cost = inverter_dict[inverter_brand]
bos_cost = system_kw * 10000
battery_cost = system_kw * 2 * battery_dict[battery_brand] if system_type in ["Off-Grid", "Hybrid"] else 0
total_cost = panel_cost + inverter_cost + bos_cost + battery_cost

if system_kw <= 2:
    central_subsidy = system_kw * 30000
elif system_kw == 3:
    central_subsidy = 78000
else:
    central_subsidy = 78000

state_subsidy = min(system_kw * 15000, 30000)
net_payable = total_cost - (central_subsidy + state_subsidy)

monthly_savings = monthly_bill * 0.7
annual_savings = monthly_savings * 12
payback = round(net_payable / annual_savings, 1) if annual_savings > 0 else None
roi = round((annual_savings / net_payable) * 100, 1) if net_payable > 0 else None

# -----------------------------
# Display Results
# -----------------------------
st.subheader("📊 Quotation Summary")
st.markdown(f"**Customer:** {customer_name}")
st.markdown(f"**Recommended System Size:** {system_kw} kW")
st.markdown(f"**Required Roof Size:** {roof_size} sqft")

st.markdown("### 💰 Cost Breakdown")
st.info(f"Panel Cost: ₹{panel_cost:,.0f}\n\n"
        f"Inverter Cost: ₹{inverter_cost:,.0f}\n\n"
        f"BOS Cost: ₹{bos_cost:,.0f}\n\n"
        f"Battery Cost: ₹{battery_cost:,.0f}\n\n"
        f"**Total Cost: ₹{total_cost:,.0f}**")

st.markdown("### 🏛 Subsidy")
st.success(f"Central Subsidy: ₹{central_subsidy:,.0f}\n\n"
           f"State Subsidy (UP): ₹{state_subsidy:,.0f}\n\n"
           f"**Net Payable: ₹{net_payable:,.0f}**")

st.markdown("### 📈 ROI & Payback")
st.warning(f"Estimated Monthly Savings: ₹{monthly_savings:,.0f}\n\n"
           f"Annual Savings: ₹{annual_savings:,.0f}\n\n"
           f"Payback Period: {payback} years\n\n"
           f"ROI: {roi}%")

# -----------------------------
# PDF Generator
# -----------------------------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_pdf(customer_name, system_kw, roof_size, panel_brand, inverter_brand, battery_brand,
                 panel_cost, inverter_cost, bos_cost, battery_cost, total_cost,
                 central_subsidy, state_subsidy, net_payable,
                 monthly_savings, annual_savings, payback, roi):

    file_name = "solar_quotation.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4

    # -----------------------------
    # Header with Logo + Title
    # -----------------------------
    try:
        c.drawImage("logo.png", 50, height - 100, width=80, preserveAspectRatio=True, mask="auto")
    except:
        pass  # if logo not found, skip

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2 + 50, height - 60, "Bharat Solar Shakti Pvt Ltd")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2 + 50, height - 80, "Your trusted partner for clean & affordable solar energy")

    # -----------------------------
    # Customer Info
    # -----------------------------
    c.setFont("Helvetica", 12)
    y = height - 140
    c.drawString(50, y, f"Customer: {customer_name}")
    c.drawString(50, y-20, f"Recommended System Size: {system_kw} kW")
    c.drawString(50, y-40, f"Required Roof Size: {roof_size} sqft")

    # -----------------------------
    # Cost Breakdown
    # -----------------------------
    y -= 80
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Cost Breakdown:")
    c.setFont("Helvetica", 12)
    c.drawString(70, y-20, f"- Panel Brand: {panel_brand}, Cost: Rs.{panel_cost:,.0f}")
    c.drawString(70, y-40, f"- Inverter Brand: {inverter_brand}, Cost: Rs.{inverter_cost:,.0f}")
    c.drawString(70, y-60, f"- BOS Cost: Rs.{bos_cost:,.0f}")
    c.drawString(70, y-80, f"- Battery Brand: {battery_brand}, Cost: Rs.{battery_cost:,.0f}")
    c.drawString(70, y-100, f"Total Cost: Rs.{total_cost:,.0f}")

    # -----------------------------
    # Subsidies
    # -----------------------------
    y -= 140
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Subsidies:")
    c.setFont("Helvetica", 12)
    c.drawString(70, y-20, f"- Central Subsidy: Rs.{central_subsidy:,.0f}")
    c.drawString(70, y-40, f"- State Subsidy (UP): Rs.{state_subsidy:,.0f}")
    c.drawString(70, y-60, f"Net Payable: Rs.{net_payable:,.0f}")

    # -----------------------------
    # Financials
    # -----------------------------
    y -= 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Financials:")
    c.setFont("Helvetica", 12)
    c.drawString(70, y-20, f"- Estimated Monthly Savings: Rs.{monthly_savings:,.0f}")
    c.drawString(70, y-40, f"- Annual Savings: Rs.{annual_savings:,.0f}")
    c.drawString(70, y-60, f"- Payback Period: {payback} years")
    c.drawString(70, y-80, f"- ROI: {roi}%")

    # -----------------------------
    # Footer Contact Info
    # -----------------------------
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 50, "Contact us: +91 6393982201  |  +91 9036126123")
    c.drawCentredString(width/2, 35, "www.bharatsolarshakti.com")

    c.save()
    return file_name

# -----------------------------
# PDF Export Button
# -----------------------------
if st.button("📄 Export Quotation to PDF"):
    pdf_file = generate_pdf(customer_name, system_kw, roof_size, panel_brand, inverter_brand, battery_brand,
                            panel_cost, inverter_cost, bos_cost, battery_cost, total_cost,
                            central_subsidy, state_subsidy, net_payable,
                            monthly_savings, annual_savings, payback, roi)
    with open(pdf_file, "rb") as f:
        st.download_button("⬇️ Download PDF Quotation", f, file_name=pdf_file, mime="application/pdf")

