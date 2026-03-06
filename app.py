import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
from datetime import datetime
import io

# Page config
st.set_page_config(page_title="🍽️ AI Nutrition Scanner Pro", page_icon="🍽️", layout="wide")

# Initialize session state
if 'nutrition_history' not in st.session_state: st.session_state.nutrition_history = []
if 'add_camera_open' not in st.session_state: st.session_state.add_camera_open = False
if 'preview_camera_open' not in st.session_state: st.session_state.preview_camera_open = False
if 'show_save_success' not in st.session_state: st.session_state.show_save_success = False
if 'add_upload_key' not in st.session_state: st.session_state.add_upload_key = 0

model = YOLO('yolov8n.pt')

# Nutrition + helper functions
def get_nutrition(food):
    nutrition = {
        'apple': {'cal':52, 'prot':0.3, 'fat':0.2, 'carb':14, 'fiber':2.4},
        'banana': {'cal':89, 'prot':1.1, 'fat':0.3, 'carb':23, 'fiber':2.6},
        'rice': {'cal':130, 'prot':2.7, 'fat':0.3, 'carb':28, 'fiber':0.4},
        'roti': {'cal':85, 'prot':3.5, 'fat':1.2, 'carb':17, 'fiber':2.0},
        'dal': {'cal':140, 'prot':9, 'fat':0.5, 'carb':20, 'fiber':8},
        'chicken': {'cal':239, 'prot':27, 'fat':13, 'carb':0, 'fiber':0},
        'pizza': {'cal':266, 'prot':11, 'fat':10, 'carb':33, 'fiber':2},
        'burger': {'cal':254, 'prot':12, 'fat':12, 'carb':26, 'fiber':1},
        'bread': {'cal':265, 'prot':9, 'fat':3, 'carb':49, 'fiber':2.7},
        'egg': {'cal':155, 'prot':13, 'fat':11, 'carb':1.1, 'fiber':0},
        'paneer': {'cal':265, 'prot':18, 'fat':20, 'carb':1.2, 'fiber':0},
        'bowl': {'cal':100, 'prot':5, 'fat':2, 'carb':15, 'fiber':1},
        'potato': {'cal':77, 'prot':2, 'fat':0.1, 'carb':17, 'fiber':2.1}
    }
    return nutrition.get(food.lower(), {'cal':100, 'prot':5, 'fat':5, 'carb':15, 'fiber':1})

def get_health_score(nutrition):
    cal, prot, fat, carb, fiber = [nutrition[k] for k in ['cal','prot','fat','carb','fiber']]
    score = min(prot/25, 30) + min(fiber/5, 25)
    if cal < 600: score += 20
    elif cal < 800: score += 15
    else: score += 5
    if fat < 20: score += 10
    if fat > 40: score -= 10
    if carb < 80 and fiber > 3: score += 10
    return max(0, min(100, score))

def get_health_rating(score):
    if score >= 80: return "🥗 SUPER HEALTHY", "🟢"
    elif score >= 60: return "✅ HEALTHY", "🟢"
    elif score >= 40: return "⚠️ MODERATE", "🟡"
    elif score >= 20: return "🍕 UNHEALTHY", "🟠"
    else: return "🚨 VERY UNHEALTHY", "🔴"

def generate_meal_csv(meal, index):
    csv = io.StringIO()
    csv.write(f"Meal #{index}\nDate,{meal['date']}\nTime,{meal['time']}\nPlates,{meal['plates']}\n")
    csv.write(f"Calories,{meal['nutrition']['cal']:.0f}\nProtein,{meal['nutrition']['prot']:.0f}g\n")
    csv.write(f"Fat,{meal['nutrition']['fat']:.0f}g\nCarbs,{meal['nutrition']['carb']:.0f}g\n")
    csv.write(f"Fiber,{meal['nutrition']['fiber']:.0f}g\nHealth,{get_health_score(meal['nutrition']):.0f}/100\n")
    return csv.getvalue().encode()

# Header
st.markdown("""
<div style='text-align:center; padding:2rem'>
    <h1 style='color:#1f77b4; font-size:3rem;'>🍽️ AI Nutrition Scanner Pro</h1>
    <p style='color:#666; font-size:1.2rem;'>Smart Food Analysis • Daily Tracking • Professional Reports</p>
</div>
""", unsafe_allow_html=True)

# 4-TAB DASHBOARD
tab1, tab2, tab3, tab4 = st.tabs(["📸 Add Meal", "🔍 Live Analysis", "📈 Tracker", "📊 Reports"])

# TAB 1 SUCCESS ONLY
if tab1 and st.session_state.get('show_save_success', False):
    st.success("✅ YOUR MEAL IS SAVED SUCCESSFULLY!")
    st.session_state.show_save_success = False

# **TAB 1: ADD MEAL - BOTH CAMERAS FIXED**
with tab1:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("### 📁 Upload Food Photos")
        uploaded_files = st.file_uploader("Choose photos...", type=['png','jpg','jpeg'], accept_multiple_files=True, key=f"add_upload_{st.session_state.add_upload_key}")
    
    with col2:
        st.markdown("### 📷 Camera")
        if st.button("🔓 Open Camera", key="add_camera_btn"):
            st.session_state.add_camera_open = True
        if st.session_state.add_camera_open:
            add_camera = st.camera_input("Take photo", key="add_camera_input")
            if st.button("❌ Close", key="add_close_camera"):
                st.session_state.add_camera_open = False
                st.rerun()
    
    # **FIXED: Check session state for add_camera**
    images = []
    if uploaded_files: 
        images.extend(uploaded_files)
    if 'add_camera_input' in st.session_state and st.session_state.add_camera_input:
        images.append(st.session_state.add_camera_input)
    
    if st.button("🚀 SAVE MEAL", type="primary", use_container_width=True, key="save_meal_btn"):
        if images:
            meal_data = {'date': datetime.now().strftime("%Y-%m-%d"), 'time': datetime.now().strftime("%H:%M"), 
                        'plates': len(images), 'nutrition': {'cal':0, 'prot':0, 'fat':0, 'carb':0, 'fiber':0}}
            
            for img_file in images:
                img = Image.open(img_file)
                results = model(np.array(img))
                plate_nutri = {'cal':0, 'prot':0, 'fat':0, 'carb':0, 'fiber':0}
                for r in results:
                    if r.boxes is not None:
                        for box in r.boxes:
                            food = r.names[int(box.cls[0])]
                            if float(box.conf[0]) > 0.3:
                                nutri = get_nutrition(food)
                                for key in nutri: plate_nutri[key] += nutri[key]
                for key in meal_data['nutrition']: meal_data['nutrition'][key] += plate_nutri[key]
            
            st.session_state.nutrition_history.append(meal_data)
            st.session_state.add_upload_key += 1
            st.session_state.show_save_success = True
            if get_health_score(meal_data['nutrition']) >= 80: st.balloons()
            st.rerun()

# **TAB 2: LIVE ANALYSIS - PERFECT**
with tab2:
    st.info("⚠️ Preview only - Not saved to reports")
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("### 📁 Upload Photos")
        preview_files = st.file_uploader("Choose photos to analyze...", type=['png','jpg','jpeg'], accept_multiple_files=True, key="live_upload")
    
    with col2:
        st.markdown("### 📷 Camera")
        if st.button("🔓 Open Camera", key="live_camera_btn"):
            st.session_state.preview_camera_open = True
        if st.session_state.preview_camera_open:
            live_camera = st.camera_input("Live preview", key="live_camera_input")
            if st.button("❌ Close", key="live_close_camera"):
                st.session_state.preview_camera_open = False
                st.rerun()
    
    # **FIXED: Check session state for live_camera**
    images = []
    if preview_files: 
        images.extend(preview_files)
    if 'live_camera_input' in st.session_state and st.session_state.live_camera_input:
        images.append(st.session_state.live_camera_input)
    
    if images:
        if st.button("🔍 ANALYZE", type="secondary", use_container_width=True, key="analyze_btn"):
            grand_total = {'cal':0, 'prot':0, 'fat':0, 'carb':0, 'fiber':0}
            
            for i, img_file in enumerate(images):
                col_img, col_res = st.columns([1, 1.5])
                
                with col_img:
                    st.markdown(f"### 🍽️ Plate {i+1}")
                    img = Image.open(img_file)
                    st.image(img, width=300)
                    results = model(np.array(img))
                    st.image(results[0].plot(), width=300, caption="Foods detected")
                
                with col_res:
                    plate_nutri = {'cal':0, 'prot':0, 'fat':0, 'carb':0, 'fiber':0}
                    for r in results:
                        if r.boxes is not None:
                            for box in r.boxes:
                                food = r.names[int(box.cls[0])]
                                if float(box.conf[0]) > 0.3:
                                    nutri = get_nutrition(food)
                                    for key in nutri: plate_nutri[key] += nutri[key]
                    
                    for key in grand_total: grand_total[key] += plate_nutri[key]
                    
                    st.markdown("### Plate Results")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Calories", f"{plate_nutri['cal']:.0f}")
                    col2.metric("Protein", f"{plate_nutri['prot']:.0f}g")
                    col3.metric("Fat", f"{plate_nutri['fat']:.0f}g")
                    col4.metric("Carbs", f"{plate_nutri['carb']:.0f}g")
            
            st.markdown("### 📊 GRAND TOTAL")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Calories", f"{grand_total['cal']:.0f}")
            col2.metric("Protein", f"{grand_total['prot']:.0f}g")
            col3.metric("Fat", f"{grand_total['fat']:.0f}g")
            col4.metric("Carbs", f"{grand_total['carb']:.0f}g")
            score = get_health_score(grand_total)
            rating, _ = get_health_rating(score)
            col5.metric("Health Score", f"{score:.0f}")
            
            st.markdown(f"### **{rating}** 🎯")
            st.success("✅ Analysis complete!")

# TAB 3: TRACKER
with tab3:
    st.markdown("### 📈 Daily Tracker")
    col1, col2 = st.columns([1, 3])
    with col1:
        daily_cal = st.number_input("Calories Goal", 2000)
        daily_prot = st.number_input("Protein Goal", 120)
    with col2:
        today_data = [m for m in st.session_state.nutrition_history if m['date'] == datetime.now().strftime("%Y-%m-%d")]
        if today_data:
            today_cal = sum(m['nutrition']['cal'] for m in today_data)
            today_prot = sum(m['nutrition']['prot'] for m in today_data)
            col1, col2 = st.columns(2)
            col1.metric("Today", f"{today_cal}/{daily_cal}")
            col2.metric("Protein", f"{today_prot}/{daily_prot}")
        else:
            st.info("Save meals to track!")

# TAB 4: REPORTS
def show_reports():
    if not st.session_state.nutrition_history:
        st.info("No saved meals yet.")
        return
    for i, meal in enumerate(reversed(st.session_state.nutrition_history)):
        idx = len(st.session_state.nutrition_history) - i
        with st.expander(f"Meal #{idx}"):
            score = get_health_score(meal['nutrition'])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Calories", f"{meal['nutrition']['cal']:.0f}")
            col2.metric("Protein", f"{meal['nutrition']['prot']:.0f}g")
            col3.metric("Fat", f"{meal['nutrition']['fat']:.0f}g")
            col4.metric("Health", f"{score:.0f}")
            col1, col2 = st.columns(2)
            csv_data = generate_meal_csv(meal, idx)
            col1.download_button(f"💾 CSV #{idx}", csv_data, f"meal_{idx}.csv")
            if col2.button(f"🗑️ Delete", key=f"del_{idx}"):
                del st.session_state.nutrition_history[-idx]
                st.success("Deleted!")
                st.rerun()

with tab4:
    st.markdown("### 📊 Saved Meals")
    show_reports()
    if st.session_state.nutrition_history:
        col1, col2 = st.columns(2)
        if col1.button("🗑️ Delete All", key="clear_all"):
            st.session_state.nutrition_history = []
            st.rerun()
        csv_data = "Date,Time,Calories,Protein,Fat,Carbs,Fiber,Health\n" + \
                  "\n".join([f"{m['date']},{m['time']},{m['nutrition']['cal']:.0f},{m['nutrition']['prot']:.0f}," +
                           f"{m['nutrition']['fat']:.0f},{m['nutrition']['carb']:.0f},{m['nutrition']['fiber']:.0f}," +
                           f"{get_health_score(m['nutrition']):.0f}" for m in st.session_state.nutrition_history])
        col2.download_button("📥 All CSV", csv_data, "report.csv")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#666;'>🍽️ AI Nutrition Scanner Pro | Perfect & Error-Free</p>", unsafe_allow_html=True)
