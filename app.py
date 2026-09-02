import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="BOQ Price Estimator", layout="centered", page_icon="🏗️")
st.title("🏗️ ระบบคำนวณและสืบราคา BOQ อัตโนมัติ")
st.write("อัปโหลดไฟล์ BOQ ของคุณ ระบบจะตัดราคาแพงสุด-ถูกสุด และหาค่าเฉลี่ยให้อัตโนมัติ")

# 1. ส่วนการจัดการไฟล์เทมเพลตตัวอย่าง
st.subheader("1. ดาวน์โหลดไฟล์เทมเพลตก่อนเริ่มใช้งาน")

# ปรับโครงสร้างข้อมูลตัวอย่างใหม่ทั้งหมด ป้องกันปัญหาพิมพ์ตกหล่น
columns = ['รายการวัสดุ', 'ปริมาณ', 'ร้าน A (ไทวัสดุ)', 'ร้าน B (โกลบอลเฮ้าส์)', 'ร้าน C (ดูโฮม)', 'ร้าน D (OneStockHome)', 'ร้าน E (เมกาโฮม)']
data = [
    ['ปูนซีเมนต์ปอร์ตแลนด์ (ถุง 50กก.)', 100, 145.0, 148.0, 142.0, 150.0, 140.0],
    ['เหล็กเส้นกลม RB9', 50, 120.0, 125.0, 118.0, 122.0, 126.0],
    ['อิฐมวลเบา 7.5 ซม.', 1000, 24.0, 24.5, 23.5, 25.0, 26.0]
]
df_template = pd.DataFrame(data, columns=columns)

template_buffer = io.BytesIO()
with pd.ExcelWriter(template_buffer, engine='openpyxl') as writer:
    df_template.to_excel(writer, index=False, sheet_name='Template_BOQ')

st.download_button(
    label="📥 ดาวน์โหลดไฟล์เทมเพลตตัวอย่าง (.xlsx)",
    data=template_buffer.getvalue(),
    file_name="Construction_BOQ_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 2. ส่วนการอัปโหลดไฟล์ใช้งานจริง
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
            prices = []
            for shop in shop_cols:
                if shop in row and pd.notnull(row[shop]):
                    try:
                        val = float(row[shop])
                        prices.append(val)
                    except ValueError:
                        continue
            
            # เงื่อนไขตัดราคาแพงสุดและถูกสุดออก (Olympic Average)
            if len(prices) >= 3:
                prices.sort()
                return np.mean(prices[1:-1]) 
            elif len(prices) > 0:
                return np.mean(prices) 
            return 0.0

        # เพิ่มคอลัมน์ผลลัพธ์
        df['ราคาเฉลี่ยต่อหน่วย (บาท)'] = df.apply(process_row_prices, axis=1)
        df['ราคารวมสุทธิ (บาท)'] = df['ปริมาณ'] * df['ราคาเฉลี่ยต่อหน่วย (บาท)']
        
        st.subheader("3. ประมวลผลเสร็จสิ้น!")
        st.dataframe(df[['รายการวัสดุ', 'ปริมาณ', 'ราคาเฉลี่ยต่อหน่วย (บาท)', 'ราคารวมสุทธิ (บาท)']].head(5))
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='สรุปราคา BOQ')
        
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์สรุปราคา BOQ (.xlsx)",
            data=buffer.getvalue(),
            file_name="BOQ_Calculated_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
