import streamlit as st
from PIL import Image
import numpy as np
import io
from datetime import datetime

st.set_page_config(page_title="🍽️ Nutrition Scanner Pro", page_icon="🍽️", layout="wide")

# **SIMPLE CSS**
st.markdown("""
<style>
.stButton > button {background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; border-radius: 12px;}
[data-testid="metric-container"] {background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);}
</style>
""", unsafe_allow_html=True)

# **MOCK FOOD DATABASE** (Works everywhere!)
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
    'salad': {'cal':50, 'prot':2, 'fat':1, 'carb':8, 'fiber':3, 'emoji': '🥗'}
}

# Initialize
if 'meals' not in st.session_state: st.session_state.meals = []

st.title("🍽️ Nutrition Scanner Pro")
st.markdown("**Smart Meal Analysis • Daily Tracking • Works on Phones!**")

tab1, tab2, tab3 = st.tabs(["📸 Scan Meal", "📈 Tracker", "📊 Reports"])

# TAB 1: SCAN MEAL
with tab1:
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📁 Upload Food Photo")
        uploaded_file = st.file_uploader("Choose photo...", type=['png','jpg','jpeg'])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, width=400)
    
    with col2:
        st.markdown("### 🎯 Quick Scan")
        selected_food = st.selectbox("What food is this?", list(FOOD_DATABASE.keys()))
        preview_nutri = FOOD_DATABASE[selected_food]
        col1, col2, col3 = st.columns(3)
        col1.metric("Calories", f"{preview_nutri['cal']}")
        col2.metric("Protein", f"{preview_nutri['prot']}g")
        col3.metric("Health", f"{min(100, preview_nutri['prot']*3 + preview_nutri['fiber']*10):.0f}")
    
    if st.button("✅ ADD MEAL", type="primary"):
        if uploaded_file or selected_food:
            meal = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime("%H:%M"),
                'food': selected_food,
                'nutrition': preview_nutri,
                'plates': 1
            }
            st.session_state.meals.append(meal)
            st.success("✅ Meal saved!")
            st.balloons()
            st.rerun()

# TAB 2: TRACKER
with tab2:
    st.markdown("### 📊 Today's Progress")
    today_meals = [m for m in st.session_state.meals if m['date'] == datetime.now().strftime("%Y-%m-%d")]
    
    if today_meals:
        total_cal = sum(m['nutrition']['cal'] for m in today_meals)
        total_prot = sum(m['nutrition']['prot'] for m in today_meals)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Calories", f"{total_cal:.0f}", "2000")
        col2.metric("Protein", f"{total_prot:.0f}g", "120g")
        col3.metric("Meals", len(today_meals))
        col4.metric("Avg Health", f"{sum(min(100, m['nutrition']['prot']*3 + m['nutrition']['fiber']*10) for m in today_meals)/len(today_meals):.0f}")
        
        st.markdown("### 🍽️ Today's Meals")
        for meal in today_meals:
            col1, col2 = st.columns([1,3])
            col1.markdown(f"**{FOOD_DATABASE[meal['food']]['emoji']}** {meal['food'].title()}")
            col2.caption(f"{meal['time']} | {meal['nutrition']['cal']:.0f}cal | {meal['nutrition']['prot']:.0f}g protein")
    else:
        st.info("👆 Add your first meal to start tracking!")

# TAB 3: REPORTS
with tab3:
    if st.session_state.meals:
        st.markdown("### 📋 All Saved Meals")
        for i, meal in enumerate(reversed(st.session_state.meals)):
            with st.expander(f"{FOOD_DATABASE[meal['food']]['emoji']} {meal['food'].title()} - {meal['date']} {meal['time']}"):
                col1, col2, col3, col4 = st.columns(4)
                nutri = meal['nutrition']
                col1.metric("Calories", f"{nutri['cal']:.0f}")
                col2.metric("Protein", f"{nutri['prot']:.0f}g")
                col3.metric("Carbs", f"{nutri['carb']:.0f}g")
                col4.metric("Fiber", f"{nutri['fiber']:.0f}g")
                
                if st.button(f"🗑️ Delete", key=f"del_{i}"):
                    st.session_state.meals.pop(len(st.session_state.meals)-1-i)
                    st.success("Deleted!")
                    st.rerun()
        
        # CSV Export
        csv = "Food,Date,Time,Calories,Protein,Fat,Carbs,Fiber\n"
        for meal in st.session_state.meals:
            nutri = meal['nutrition']
            csv += f"{meal['food']},{meal['date']},{meal['time']},{nutri['cal']:.0f},{nutri['prot']:.0f},{nutri['fat']:.0f},{nutri['carb']:.0f},{nutri['fiber']:.0f}\n"
        st.download_button("📥 Download Report", csv, "nutrition_report.csv", "📊")
    else:
        st.info("📱 No meals saved yet!")

st.markdown("---")
st.markdown("*🍽️ Nutrition Scanner Pro - Works perfectly on phones & cloud!*")
