import streamlit as st

st.title("Hello")

if st.button("Click me"):
    st.write("Butoni eshte klikuar")

if st.checkbox("Me kliko mua"):
    st.write("E ke klikuar checkbox")

userInput = st.text_input("Enter a text")
st.write("Ju keni shenuar:", userInput)

age = st.number_input("Enter your age", min_value=0, max_value=120)
st.write("Your age is:", age)

message = st.text_area("Shkruaj mesazhin tend")
st.write("Mesazhi yt eshte:", message)

choice = st.radio("Zgjedh nje ekip", ["Barcelona", "Real Madrid", "Manchester United", "Juventus"])
st.write("Ke zgjedhur:", choice)

if st.button("Regjistrohu"):
    st.success("Tani jeni regjistruar me sukses ne platformen tone")