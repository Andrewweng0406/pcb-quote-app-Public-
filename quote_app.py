from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import streamlit as st
import pandas as pd

file_path = "Quote.xlsx"

st.title("PCB 報價計算器")

# 讀 Excel sheet 名稱
xls = pd.ExcelFile(file_path)
st.write("Excel sheets:", xls.sheet_names)

# 讀 Excel
df_rules = pd.read_excel(file_path, sheet_name="參考資料有埋程式")

# 客戶資料
st.subheader("客戶資料")

customer_name = st.text_input("客戶名稱", value="ABC Company")
quote_no = st.text_input("報價單編號", value="Q-2026-001")
sales_name = st.text_input("業務名稱", value="Andrew")

# 基本輸入
length = st.number_input("長度 inch", value=12.0)
width = st.number_input("寬度 inch", value=12.0)
layer = st.selectbox("Layer", [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58])
material = st.selectbox("材質", ["FR4", "Low Loss", "Very Low Loss"])
quantity = st.number_input("數量", value=1)

area = length * width

df_price = pd.read_excel(file_path, sheet_name="價格表")

row = df_price[df_price["Layer"] == layer]

if row.empty:
    st.error("找不到這個 Layer")
    st.stop()

base_price = row[material].values[0]
base_total = area * base_price

# 特殊條件
st.subheader("特殊條件")

pitch = st.selectbox("Pitch", ["正常", "0.47~0.55mm (+20%)", "0.4~0.46mm (+45%)"])
impedance = st.selectbox("阻抗", ["無", "+/-10% (+20%)", "+/-5% (+45%)"])
gold = st.selectbox("鍍金", ["無", "5u (+3000)", "10u (+6000)"])

vip = st.checkbox("VIP 樹脂塞孔 (+5000)")
back_drill = st.checkbox("背鑽 (+5000)")

extra_percent = 0

if pitch == "0.47~0.55mm (+20%)":
    extra_percent += 0.2
elif pitch == "0.4~0.46mm (+45%)":
    extra_percent += 0.45

if impedance == "+/-10% (+20%)":
    extra_percent += 0.2
elif impedance == "+/-5% (+45%)":
    extra_percent += 0.45

extra_cost = base_total * extra_percent

fixed_cost = 0

if gold == "5u (+3000)":
    fixed_cost += 3000
elif gold == "10u (+6000)":
    fixed_cost += 6000

if vip:
    fixed_cost += 5000

if back_drill:
    fixed_cost += 5000

unit_price = base_total + extra_cost + fixed_cost
total = unit_price * quantity

# 報價結果
st.subheader("報價結果")

st.write(f"客戶名稱：{customer_name}")
st.write(f"報價單編號：{quote_no}")
st.write(f"業務名稱：{sales_name}")
st.write("---")

st.metric("總價", f"NTD {total:,.0f}")
st.metric("單片價格", f"NTD {unit_price:,.0f}")

st.write("---")

st.write(f"面積：{area:.2f} in²")
st.write(f"Layer 單價：NTD {base_price:,.0f}")
st.write(f"基礎價格：NTD {base_total:,.0f}")
st.write(f"加價比例：{extra_percent * 100:.0f}%")
st.write(f"加價金額：NTD {extra_cost:,.0f}")
st.write(f"固定費用：NTD {fixed_cost:,.0f}")
st.write(f"數量：{quantity}")

# PDF
def create_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(220, 750, "QUOTATION")

    c.setFont("Helvetica", 10)
    c.drawString(50, 720, "Company: Your Company Name")
    c.drawString(50, 705, "Address: Your Address")
    c.drawString(50, 690, "Tel: 123-456-7890")

    c.drawString(50, 650, f"Customer: {customer_name}")
    c.drawString(50, 635, f"Quote No: {quote_no}")
    c.drawString(50, 620, f"Sales: {sales_name}")

    c.line(50, 610, 550, 610)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 580, "Product Specification")

    c.setFont("Helvetica", 10)
    c.drawString(50, 560, f"Size: {length} x {width} inch")
    c.drawString(50, 545, f"Layer: {layer}")
    c.drawString(50, 530, f"Material: {material}")
    c.drawString(50, 515, f"Area: {area:.2f} in2")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 485, "Pricing")

    c.setFont("Helvetica", 10)
    c.drawString(50, 465, f"Base Price: NTD {base_total:,.0f}")
    c.drawString(50, 450, f"Extra Cost: NTD {extra_cost:,.0f}")
    c.drawString(50, 435, f"Fixed Cost: NTD {fixed_cost:,.0f}")
    c.drawString(50, 420, f"Unit Price: NTD {unit_price:,.0f}")
    c.drawString(50, 405, f"Quantity: {quantity}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 375, f"TOTAL: NTD {total:,.0f}")

    c.setFont("Helvetica", 9)
    c.drawString(50, 335, "Note:")
    c.drawString(50, 320, "1. Lead time: 7-10 days")
    c.drawString(50, 305, "2. Price valid for 30 days")

    c.save()
    buffer.seek(0)
    return buffer

pdf = create_pdf()

st.download_button(
    label="下載報價單 PDF",
    data=pdf,
    file_name=f"{quote_no}.pdf",
    mime="application/pdf"
)