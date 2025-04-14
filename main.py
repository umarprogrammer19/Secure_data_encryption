import streamlit as st
import hashlib
from cryptography.fernet import Fernet

if "KEY" not in st.session_state:
    st.session_state.KEY = Fernet.generate_key()
cipher = Fernet(st.session_state.KEY)

if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "needs_login" not in st.session_state:
    st.session_state.needs_login = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


# Function to hash the passkey using SHA-256
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()


# Function to encrypt data using Fernet
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()


# Function to decrypt data with passkey verification
def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)
    if encrypted_text in st.session_state.stored_data:
        if st.session_state.stored_data[encrypted_text] == hashed_passkey:
            st.session_state.failed_attempts = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
        else:
            st.session_state.failed_attempts += 1
            if st.session_state.failed_attempts >= 3:
                st.session_state.needs_login = True
            return None
    else:
        st.session_state.failed_attempts += 1
        if st.session_state.failed_attempts >= 3:
            st.session_state.needs_login = True
        return None


st.title("🔒 Secure Data Encryption System")

menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.selectbox(
    "Navigate to:", menu, index=menu.index(st.session_state.current_page)
)
st.session_state.current_page = choice

if st.session_state.needs_login:
    st.subheader("🔑 Reauthorization Required")
    login_pass = st.text_input("Enter Master Password:", type="password")
    if st.button("Login"):
        if login_pass == "admin123":
            st.session_state.needs_login = False
            st.session_state.failed_attempts = 0
            st.success("✅ Reauthorized successfully! You can now retrieve data.")
            st.session_state.current_page = "Retrieve Data"
        else:
            st.error("❌ Incorrect password!")
else:
    if choice == "Home":
        st.subheader("🏠 Welcome to the Secure Data System")
        st.write(
            "Use this app to **securely store and retrieve data** using unique passkeys."
        )

    elif choice == "Store Data":
        st.subheader("📂 Store Data Securely")
        user_data = st.text_area("Enter Data:")
        passkey = st.text_input("Enter Passkey:", type="password")
        if st.button("Encrypt & Save"):
            if user_data and passkey:
                hashed_passkey = hash_passkey(passkey)
                encrypted_text = encrypt_data(user_data)
                st.session_state.stored_data[encrypted_text] = hashed_passkey
                st.success("✅ Data stored securely!")
                st.write(f"🔑 Your encrypted data (save this!): {encrypted_text}")
            else:
                st.error("⚠️ Both fields are required!")

    elif choice == "Retrieve Data":
        st.subheader("🔍 Retrieve Your Data")
        encrypted_text = st.text_area("Enter Encrypted Data:")
        passkey = st.text_input("Enter Passkey:", type="password")
        if st.button("Decrypt"):
            if encrypted_text and passkey:
                decrypted_text = decrypt_data(encrypted_text, passkey)
                if decrypted_text:
                    st.success(f"✅ Decrypted Data: {decrypted_text}")
                else:
                    st.error(
                        f"❌ Incorrect passkey! Attempts: {st.session_state.failed_attempts}/3"
                    )
            else:
                st.error("⚠️ Both fields are required!")

    elif choice == "Login":
        st.subheader("🔑 Login Page")
        st.write("This page is for reauthorization after too many failed attempts.")
