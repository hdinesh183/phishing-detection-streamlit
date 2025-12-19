import streamlit as st
from auth import create_users_table, register_user, login_user
from utils import load_model, predict_text, html_to_text



st.set_page_config(page_title="Phishing Detection System", layout="centered")

create_users_table()

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ---------- AUTH UI ----------
def auth_ui():
    st.title("🔐 User Authentication")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------- LOGIN TAB ----------
    with tab1:
        st.subheader("Login")

        login_identifier = st.text_input(
            "Username or Email",
            key="login_identifier"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", key="login_button"):
            if login_user(login_identifier, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_identifier
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username/email or password")

    # ---------- REGISTER TAB ----------
    with tab2:
        st.subheader("Register")

        reg_username = st.text_input(
            "Username",
            key="reg_username"
        )

        reg_email = st.text_input(
            "Email",
            key="reg_email"
        )

        reg_password = st.text_input(
            "Password",
            type="password",
            key="reg_password"
        )

        reg_confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="reg_confirm"
        )

        if st.button("Register", key="register_button"):
            success, message = register_user(
                reg_username,
                reg_email,
                reg_password,
                reg_confirm
            )

            if success:
                st.success(message)
            else:
                st.error(message)


# ---------- PROTECTED APP ----------
def phishing_app():
    st.sidebar.success(f"Logged in as {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("🔐 Phishing Detection System")
    st.write("Detect phishing using **NLP & BERT**")

    @st.cache_resource
    def load_all_models():
        return (
            load_model("models/best_model.pt"),
            load_model("models/best_model.pt"),
            load_model("models/website_phishing_model.pt"),
        )

    url_model, email_model, website_model = load_all_models()

    option = st.selectbox(
        "Select Detection Type",
        ["URL Detection", "Email Detection", "Website HTML Detection"]
    )

    if option == "URL Detection":
        url = st.text_input("Enter URL")
        if st.button("Check URL"):
            pred, prob = predict_text(url_model, url, max_len=128)
            st.error("⚠️ Phishing URL") if pred else st.success("✅ Legitimate URL")

    elif option == "Email Detection":
        email = st.text_area("Paste Email Content", height=200)
        if st.button("Check Email"):
            pred, prob = predict_text(email_model, email)
            st.error("⚠️ Phishing Email") if pred else st.success("✅ Safe Email")

    else:
        html = st.text_area("Paste Website HTML", height=250)
        if st.button("Check Website"):
            clean = html_to_text(html)
            pred, prob = predict_text(website_model, clean, max_len=512)
            st.error("⚠️ Phishing Website") if pred else st.success("✅ Legitimate Website")

# ---------- ROUTER ----------
if not st.session_state.logged_in:
    auth_ui()
else:
    phishing_app()
