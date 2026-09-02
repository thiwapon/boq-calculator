import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="BOQ Price Estimator", layout="centered", page_icon="🏗️")
st.title("🏗️ ระบบคำนวณและสืบราคา BOQ อัตโนมัติ")
st.write("อัปโหลดไฟล์ BOQ ของคุณ ระบบจะตัดราคาแพงสุด-ถูกสุด และหาค่าเฉลี่ยให้อัตโนมัติ")

# 1. สร้างตัวอย่างข้อมูลเพื่อให้โหลดเทมเพลตได้ในเว็บเลย
st.subheader("1. ดาวน์โหลดไฟล์เทมเพลตก่อนเริ่มใช้งาน")

template_data = {
    'รายการวัสดุ': ['ปูนซีเมนต์ปอร์ตแลนด์ (ถุง 50กก.)', 'เหล็กเส้นกลม RB9', 'อิฐมวลเบา 7.5 ซม.'],
    'ปริมาณ':,
    'ร้าน A (ไทวัสดุ)':,
    'ร้าน B (โกลบอลเฮ้าส์)': [148, 125, 24.5],
    'ร้าน C (ดูโฮม)': [142, 118, 23.5],
    'ร้าน D (OneStockHome)':,
    'ร้าน E (เมกาโฮม)': [146, 122, 26]
}
df_template = pd.DataFrame(template_data)

template_buffer = io.BytesIO()
with pd.ExcelWriter(template_buffer, engine='openpyxl') as writer:
    df_template.to_excel(writer, index=False, sheet_name='Template_BOQ')

st.download_button(
    label="📥 ดาวน์โหลดไฟล์เทมเพลตตัวอย่าง (.xlsx)",
    data=template_buffer.getvalue(),
    file_name="Construction_BOQ_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 2. ฟอร์มสำหรับโหลด BOQ (Upload File)
st.subheader("2. อัปโหลดไฟล์ BOQ ที่ใส่ราคาครบ 5 ร้านแล้ว")
uploaded_file = st.file_uploader("เลือกไฟล์ .xlsx ที่ต้องการประมวลผล", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("โหลดข้อมูล BOQ สำเร็จ!")
    st.write("ตัวอย่างข้อมูลที่อัปโหลด:")
    st.dataframe(df.head(5))
    
    if st.button("🚀 เริ่มคำนวณราคาเฉลี่ยกลาง"):
        shop_cols = ['ร้าน A (ไทวัสดุ)', 'ร้าน B (โกลบอลเฮ้าส์)', 'ร้าน C (ดูโฮม)', 'ร้าน D (OneStockHome)', 'ร้าน E (เมกาโฮม)']
        
        def process_row_prices(row):
            # ดึงเฉพาะค่าที่เป็นตัวเลขและไม่ว่าง
            prices = [row[shop] for shop in shop_cols if pd.notnull(row[shop]) and isinstance(row[shop], (int, float))]
            if len(prices) >= 3:
                prices.sort()
                return np.mean(prices[1:-1]) # ตัดหัว (ต่ำสุด) และท้าย (สูงสุด)
            elif len(prices) > 0:
                return np.mean(prices)
            return 0

        # คำนวณข้อมูล
        df['ราคาเฉลี่ยต่อหน่วย (บาท)'] = df.apply(process_row_prices, axis=1)
        df['ราคารวมสุทธิ (บาท)'] = df['ปริมาณ'] * df['ราคาเฉลี่ยต่อหน่วย (บาท)']
        
        st.subheader("3. ประมวลผลเสร็จสิ้น!")
        st.dataframe(df[['รายการวัสดุ', 'ปริมาณ', 'ราคาเฉลี่ยต่อหน่วย (บาท)', 'ราคารวมสุทธิ (บาท)']].head(5))
        
        # แปลงข้อมูลเป็นบัฟเฟอร์เพื่อส่งให้ดาวน์โหลด
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='สรุปราคา BOQ')
        
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์สรุปราคา BOQ (.xlsx)",
            data=buffer.getvalue(),
            file_name="BOQ_Calculated_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

