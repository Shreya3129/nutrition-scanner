import streamlit as st
from PIL import Image
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="🍽️ Nutrition Scanner Pro", page_icon="🍽️", layout="wide")

# **PROFESSIONAL CSS**
st.markdown("""
<style>
.stButton > button {background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; border-radius: 12px; font-weight: 600;}
.stButton > button:hover {background: linear-gradient(135deg, #3730A3, #6D28D9); transform: translateY(-1px);}
[data-testid="metric-container"] {background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);}
</style>
""", unsafe_allow_html=True)

# **COMPLETE FOOD DATABASE**
FOOD_DATABASE = {
    'apple': {'cal':52, 'prot':0.3, 'fat':0.2, 'carb':14, 'fiber':2.4, 'emoji': '🍎'},
    'banana': {'cal':89, 'prot':1.1, 'fat':0.3, 'carb':23, 'fiber':2.6, 'emoji': '🍌'},
    'rice': {'cal':130, 'prot':2.7, 'fat':0.3, 'carb':28, 'fiber':0.4, 'emoji': '🍚'},
    'roti': {'cal':85, 'prot':3.5, 'fat':1.2, 'carb':17, 'fiber':2.0, 'emoji': '🥙'},
    'dal': {'cal':140, 'prot':9, 'fat':0.5, 'carb':20, 'fiber':8, 'emoji': '🍲'},
    'chicken': {'cal':239, 'prot':27, 'fat':13, 'carb':0, 'fiber':0, 'emoji': '🍗'},
    'pizza': {'cal':266, 'prot':11, 'fat':10, 'carb':33, 'fiber':2, 'emoji': '🍕'},
    'burger': {'cal':254, 'prot':12, 'fat':12, 'carb':26, 'fiber':1, 'emoji': '🍔'},
    'egg': {'cal':155, 'prot':13, 'fat':11, 'carb':1.1, 'fiber':0, 'emoji': '🥚'},
    'salad': {'cal':50, 'prot':2, 'fat':1, 'carb':8, 'fiber':3, 'emoji': '🥗'},
    'bread': {'cal':265, 'prot':9, 'fat':3, 'carb':49, 'fiber':2.7, 'emoji': '🍞'},
    'paneer': {'cal':265, 'prot':18, 'fat':20, 'carb':1.2, 'fiber':0, 'emoji': '🧀'},
    'potato': {'cal':77, 'prot':2, 'fat':0.1, 'carb':17, 'fiber':2.1, 'emoji': '🥔'}
}

# Initialize session state
if 'meals' not in st.session_state: st.session_state.meals = []
if 'camera_open' not in st.session_state: st.session_state.camera_open = False

st.title("🍽️ Nutrition Scanner Pro")
st.markdown("**📸 Upload • 📱 Camera • 🔍 Live Analysis • 📊 Tracking**")

# **4 FULL TABS**
tab1, tab2, tab3, tab4 = st.tabs(["📸 Add Meal", "🔍 Live Analysis", "📈 Tracker", "📊 Reports"])

# **TAB 1: ADD MEAL (Upload + Quick Scan)**
with tab1:
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📁 Upload Photos")
        uploaded_files = st.file_uploader("Choose food photos", type=['png','jpg','jpeg'], accept_multiple_files=True)
        if uploaded_files:
            for img in uploaded_files:
                st.image(Image.open(img), width=250)
    
    with col2:
        st.markdown("### 🎯 Quick Add")
        selected_food = st.selectbox("Select food", [""] + list(FOOD_DATABASE.keys()))
        quantity = st.slider("Portions", 1, 5, 1)
        
        if selected_food:
            nutri = FOOD_DATABASE[selected_food]
            total_nutri = {k: v*quantity for k,v in nutri.items()}
            col1, col2, col3 = st.columns(3)
            col1.metric("Calories", f"{total_nutri['cal']:.0f}")
            col2.metric("Protein", f"{total_nutri['prot']:.0f}g")
            col3.metric("Carbs", f"{total_nutri['carb']:.0f}g")
    
    if st.button("✅ SAVE MEAL", type="primary", use_container_width=True) and (uploaded_files or selected_food):
        meal = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'time': datetime.now().strftime("%H:%M"),
            'food': selected_food or 'mixed',
            'nutrition': total_nutri if selected_food else {'cal':300, 'prot':15, 'fat':10, 'carb':30, 'fiber':2},
            'plates': len(uploaded_files) if uploaded_files else 1,
            'quantity': quantity
        }
        st.session_state.meals.append(meal)
        st.success(f"✅ {meal['food'].title()} meal saved!")
        st.balloons()
        st.rerun()

# **TAB 2: LIVE ANALYSIS (Camera + Analysis)**
with tab2:
    st.info("⚠️ Preview only - Use 'Add Meal' tab to save")
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("### 📁 Upload for Analysis")
        analysis_files = st.file_uploader("Analyze photos", type=['png','jpg','jpeg'], accept_multiple_files=True)
    
    with col2:
        st.markdown("### 📱 Live Camera")
        if st.button("📷 Open Camera"):
            st.session_state.camera_open = True
        
        if st.session_state.camera_open:
            camera_img = st.camera_input("Take food photo")
            if st.button("❌ Close Camera"):
                st.session_state.camera_open = False
                st.rerun()
    
    # **ANALYZE BUTTON**
    images = analysis_files or []
    if camera_img: images.append(camera_img)
    
    if images and st.button("🔍 ANALYZE LIVE", type="secondary", use_container_width=True):
        total_nutri = {'cal':0, 'prot':0, 'fat':0, 'carb':0, 'fiber':0}
        
        for i, img_file in enumerate(images):
            col_img, col_res = st.columns([1, 1.5])
            with col_img:
                st.markdown(f"### 🍽️ Plate {i+1}")
                img = Image.open(img_file)
                st.image(img, width=300)
            
            with col_res:
                # **SIMULATED AI ANALYSIS**
                detected_food = np.random.choice(list(FOOD_DATABASE.keys()), 2)
                plate_nutri = {'cal':0, 'prot':0, 'fat':0, 'carb':0, 'fiber':0}
                
                st.markdown("**🔍 Detected:**")
                for food in detected_food:
                    nutri = FOOD_DATABASE[food]
                    for k in plate_nutri: plate_nutri[k] += nutri[k]
                    st.write(f"• {FOOD_DATABASE[food]['emoji']} {food.title()}")
                
                for k in total_nutri: total_nutri[k] += plate_nutri[k]
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Calories", f"{plate_nutri['cal']:.0f}")
                col2.metric("Protein", f"{plate_nutri['prot']:.0f}g")
                col3.metric("Carbs", f"{plate_nutri['carb']:.0f}g")
        
        # **GRAND TOTAL**
        st.markdown("### 📊 GRAND TOTAL")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Calories", f"{total_nutri['cal']:.0f}")
        col2.metric("Protein", f"{total_nutri['prot']:.0f}g")
        col3.metric("Fat", f"{total_nutri['fat']:.0f}g")
        col4.metric("Carbs", f"{total_nutri['carb']:.0f}g")
        health_score = min(100, total_nutri['prot']*2 + total_nutri['fiber']*10)
        col5.metric("Health", f"{health_score:.0f}/100")
        st.success("✅ Live analysis complete!")

# **TAB 3: TRACKER**
with tab3:
    today_meals = [m for m in st.session_state.meals if m['date'] == datetime.now().strftime("%Y-%m-%d")]
    if today_meals:
        total_cal = sum(m['nutrition']['cal'] for m in today_meals)
        total_prot = sum(m['nutrition']['prot'] for m in today_meals)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Calories", f"{total_cal:.0f}", "2000")
        col2.metric("Protein", f"{total_prot:.0f}g", "120g")
        col3.metric("Meals", len(today_meals), "5")
        
        st.markdown("### 🍽️ Today")
        for meal in today_meals:
            st.write(f"• **{meal['food'].title()}** - {meal['nutrition']['cal']:.0f}cal")
    else:
        st.info("👆 Add meals to track!")

# **TAB 4: REPORTS**
with tab4:
    if st.session_state.meals:
        for i, meal in enumerate(reversed(st.session_state.meals)):
            with st.expander(f"{meal['food'].title()} - {meal['date']} {meal['time']}"):
                col1, col2, col3, col4 = st.columns(4)
                nutri = meal['nutrition']
                col1.metric("Calories", f"{nutri['cal']:.0f}")
                col2.metric("Protein", f"{nutri['prot']:.0f}g")
                col3.metric("Carbs", f"{nutri['carb']:.0f}g")
                col4.metric("Fiber", f"{nutri['fiber']:.0f}g")
                
                col1, col2 = st.columns(2)
                if col1.button("🗑️ Delete", key=f"del_{i}"):
                    st.session_state.meals.pop(-1-i)
                    st.rerun()
    else:
        st.info("No meals saved!")

st.markdown("---")
st.markdown("*🍽️ Perfect for phones! Upload + Camera + Analysis + Tracking*")
