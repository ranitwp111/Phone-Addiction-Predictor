import pickle
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import sklearn

# Load the trained KNN model (optional, as we now use rules for the main output)
with open("knn_model.pkl", "rb") as f:
    model = pickle.load(f)

# --- UI Configuration ---
st.set_page_config(
    page_title="Smartphone Addiction Predictor",
    page_icon="📱",
    layout="wide"
)

# --- Custom CSS for a modern look ---
st.markdown("""
<style>
    /* General font and layout improvements */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .st-emotion-cache-10trblm { /* Input label font */
        font-size: 1.1rem;
    }
    .st-emotion-cache-16txtl3 { /* Header font */
        font-size: 1.2rem;
        font-weight: bold;
    }
    div[data-testid="stMetric"] {
        text-align: center;
    }
    /* Custom Button Style */
    .stButton>button {
        background: linear-gradient(45deg, #007bff, #4e54c8);
        color: white;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: bold;
        padding: 12px 20px;
        border: none;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 123, 255, 0.5);
    }
    .stButton>button:active {
        transform: translateY(0px);
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# --- App Title and Description ---
st.title("📱 Smartphone Addiction Prediction")
st.markdown("### How much is your phone a part of you? Enter your habits to find out.")

st.divider()

# --- Input Section with Card-like UI ---
with st.container(border=True):
    st.header("✍️ Enter Your Daily Habits")
    col1, col2 = st.columns(2)

    with col1:
        daily_usage = st.number_input("🕒 Total Daily Usage (in hours)", min_value=0.0, max_value=24.0, step=0.1, value=4.0)
        social_media = st.number_input("💬 Time on Social Media (in hours)", min_value=0.0, max_value=24.0, step=0.1, value=2.0)
        gaming = st.number_input("🎮 Time on Gaming (in hours)", min_value=0.0, max_value=24.0, step=0.1, value=1.0)

    with col2:
        apps_used = st.number_input("📲 Number of Apps Used Daily", min_value=0, step=1, value=15)
        phone_checks = st.number_input("👀 Number of Phone Checks Per Day", min_value=0, step=1, value=50)
        sleep_hours = st.number_input("😴 Hours of Sleep per Night", min_value=0.0, max_value=24.0, step=0.1, value=7.0)

st.write("") # Add a little space

# --- Prediction and Visualization Section ---
if st.button("Analyze My Habits", use_container_width=True):
    st.divider()
    st.header("📊 Your Results")

    # --- Rule-based logic with reference point for delta ---
    reference_value = 0
    if daily_usage <= 3:
        level = "Low Risk"
        color = "#00C49F"  # Vibrant Teal
        reference_value = 3 # Compare to the next threshold
    elif 3 < daily_usage <= 5:
        level = "Moderate Risk"
        color = "#FFBB28"  # Amber/Gold
        reference_value = 3 # Compare to the low risk threshold
    else:
        level = "High Risk"
        color = "#FF8042"  # Coral Red
        reference_value = 5 # Compare to the moderate risk threshold
        
    score_for_gauge = daily_usage

    # --- Results are now displayed vertically ---
    
    # --- Gauge Chart ---
    st.subheader("Risk Level Gauge")
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score_for_gauge,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Daily Usage (Hours)", 'font': {'size': 20}},
        delta = {
            'reference': reference_value,
            'increasing': {'color': "#FF8042"},
            'decreasing': {'color': "#00C49F"},
            'suffix': ' hrs'
        },
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 3], 'color': 'rgba(0, 196, 159, 0.7)'},   # Teal
                {'range': [3, 5], 'color': 'rgba(255, 187, 40, 0.7)'}, # Amber
                {'range': [5, 10], 'color': 'rgba(255, 128, 66, 0.7)'}  # Coral
            ],
        }
    ))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
    
    delta_text_explanation = ""
    if level == "Moderate Risk":
        delta_text_explanation = f"You are **{score_for_gauge - reference_value:.1f} hours** into the moderate risk zone."
    elif level == "High Risk":
        delta_text_explanation = f"You are **{score_for_gauge - reference_value:.1f} hours** into the high risk zone."
    else: # Low Risk
        delta_text_explanation = f"You are **{reference_value - score_for_gauge:.1f} hours** away from the moderate risk zone."

    st.markdown(f"<h4 style='text-align: center;'>Your estimated risk is <span style='color:{color};'>{level}</span>.</h4>", unsafe_allow_html=True)
    st.info(delta_text_explanation)

    st.write("") # Add some space

    # --- Bar Chart ---
    st.subheader("Breakdown of Daily Usage")
    chart_data = pd.DataFrame({
        'Category': ['Social Media', 'Gaming', 'Other'],
        'Hours': [social_media, gaming, daily_usage - social_media - gaming]
    })
    chart_data = chart_data[chart_data['Hours'] >= 0]

    bar_chart = alt.Chart(chart_data).mark_bar(
        cornerRadius=5,
        opacity=0.9
    ).encode(
        x=alt.X('Hours:Q', title='Hours Per Day'),
        y=alt.Y('Category:N', sort=None, title=None),
        color=alt.Color('Category:N',
                        scale=alt.Scale(
                            domain=['Social Media', 'Gaming', 'Other'],
                            range=['#1DA1F2', '#FF4B4B', '#A9A9A9'])
                       ),
        tooltip=['Category', 'Hours']
    ).properties(
        title='How You Spend Your Screen Time'
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # --- Personalized Recommendations Section ---
    st.divider()
    st.header("💡 Actionable Advice")
    if level == "Low Risk":
        st.success("#### You have a healthy relationship with your phone! 🎉")
        with st.expander("See tips to maintain this balance"):
            st.markdown("""
            - **Continue Being Mindful**: You're doing great. Keep being aware of when and why you use your phone.
            - **Help Others**: Share your healthy habits with friends or family who might be struggling.
            - **Explore Offline Hobbies**: Continue investing time in activities that don't involve screens.
            """)
    elif level == "Moderate Risk":
        st.warning("#### You're at a moderate risk. It's a good time to build healthier habits. 🤔")
        with st.expander("See tips to improve your digital well-being"):
            st.markdown("""
            - **Set 'No-Phone' Times**: Designate specific times, like during meals or the first hour after waking up, as phone-free.
            - **Turn Off Non-Essential Notifications**: Go to your settings and disable notifications for apps that aren't urgent. This reduces the number of times you're pulled back to your phone.
            - **Use Grayscale Mode**: Making your screen black and white makes it less appealing and can help curb mindless scrolling.
            """)
    else: # High Risk
        st.error("#### You are at a high risk. It's crucial to take steps to regain control. 🚩")
        with st.expander("See tips for a digital detox"):
            st.markdown("""
            - **Identify Trigger Apps**: Find out which apps consume most of your time and consider deleting them for a short period (e.g., one week).
            - **Use Digital Wellbeing/Screen Time Tools**: Set daily time limits for your most-used apps directly in your phone's settings.
            - **Create Physical Distance**: When you need to focus, leave your phone in another room. Charge it overnight somewhere other than your bedroom.
            - **Seek Support**: Talk to a friend, family member, or a professional about your concerns. You're not alone in this.
            """)