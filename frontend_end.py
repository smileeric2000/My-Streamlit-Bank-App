"""
frontend_end.py
UI helpers and shared UI elements for My Streamlit Bank App
"""

import streamlit as st
import base64
from pathlib import Path

#opay logo

LOGO_BASE64 = "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"

blank_profile_img = r"C:\Users\USER\data_science\bank_project\blank_profile.jpeg"


def img_converter(_img):
    
    #Function that converts image path OR Streamlit UploadedFile to base64
    
    #Streamlit UploadedFile (camera / uploader)
    if hasattr(_img, "read"):
        img_bytes = _img.read()

    #File path (default image)
    else:
        img_path = Path(_img)
        with open(img_path, "rb") as f:
            img_bytes = f.read()

    encoded = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{encoded}"


def logo_image():
    #Return a data URI for the small white square logo.
    return f"data:image/png;base64,{LOGO_BASE64}"

import base64

def inject_global_css():
    #Read image and convert to base64
    with open("assets/global_back.png", "rb") as f:
        img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode()

    #Inject CSS with background
    st.markdown(
        f"""
        <style>
        /* page background */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;          /* cover entire page */
            background-repeat: no-repeat;
            background-attachment: fixed;    /* stay fixed when scrolling */
            color: #00010;                     /* default text color */
        }}

        /* container width responsive */
        .main {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 16px;
        }}

        /* balance card */
        .balance-card {{
            background: linear-gradient(90deg,#b894,#00cec9);
            color: white;
            padding: 18px;
            border-radius: 12px;
        }}

        .txn-card {{
            background: #b899;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 8px;
        }}

        .action-btn {{
            border-radius: 10px;
            padding: 12px 8px;
            width: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def header_with_logo(user_name: str, balance: float, profile_img):
    col1, col2, col3 = st.columns([2, 6, 1])

    with col1:
        #USE THE PARSED PROFILE IMAGE
        if profile_img and isinstance(profile_img, str) and profile_img.startswith("data:image"):
            st.image(profile_img, width=120)
        else:
            st.image(img_converter(blank_profile_img), width=120)

    with col3: 
        st.image(logo_image(), width=60)

    with col2:
        st.markdown(f"### Hi, {user_name}")
        st.markdown(f"##### Available Balance\n\n₦{balance:,.2f}")


def transactions_list(txns):
    st.markdown("### Transaction History")
    for t in txns:
        direction = t.get('direction', '')
        amount = t.get('amount', 0)
        note = t.get('note') or ''
        created = t.get('created_at') or ''
        sign = '+' if direction == 'in' else '-'
        st.markdown(f"<div class='txn-card'><b>{sign}</b> ₦{amount:,.2f} — {note} <br /><small>{created}</small></div>", unsafe_allow_html=True)
