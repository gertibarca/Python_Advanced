import streamlit as st

def main():
    st.title("Kalkulatori")

    num1 = st.number_input("Shkruaj numrin e pare", value=0.0)
    num2 = st.number_input("Shkruaj numrin e dyte", value=0.0)

    operatori = st.radio("Zgjedhe veprimin", ["Mbledhje", "Zbritje", "Shumëzim"])

    if st.button("Llogarit"):
        if operatori == "Mbledhje":
            result = num1 + num2
        elif operatori == "Zbritje":
            result = num1 - num2
        elif operatori == "Shumëzim":
            result = num1 * num2
        else:
            result = None

        if result is not None:
            st.success(f"Rezultati është: {result}")

if __name__ == "__main__":
    main()