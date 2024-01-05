import streamlit as st
from PIL import Image

st.set_page_config(layout="centered")

image_1 = Image.open('./data/image_1.JPG')
resize_image_1 = image_1.resize((1000,500))
image_2 = Image.open('./data/image_2.JPG')
resize_image_2 = image_2.resize((1000,500))
image_3 = Image.open('./data/image_3.JPG')
resize_image_3 = image_3.resize((1000,500))

st.title(' ')
st.title('🌎 Dream Closer!')
st.title(' ')
st.header('✈️ A world of exploration and discovery is closer than you think!')
st.title(' ')
col1,col2 = st.columns(2)
with col1:
    st.image(resize_image_1)
with col2:
    st.image(resize_image_3)
st.image(resize_image_2)
st.title(' ')
st.subheader("Are you too tired to plan your trip?")
st.subheader("Or maybe you haven't decided on a destination yet?")
st.subheader("If that's the case, you have an AI service to get recommendations for your next destination and plan an itinerary for you!🔥")



