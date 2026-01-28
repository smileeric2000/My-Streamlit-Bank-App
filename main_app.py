#Streamlit entrypoint for the Bank App "main_app.py"

#Import libraries and all other dependencies

import streamlit as st
from Utils import (init_db, create_user, authenticate, get_user,
    add_transaction, update_balance, get_transactions,
    transfer, get_connection, update_profile_img
)
import importlib
import frontend_end as fe
importlib.reload(fe)
import time
from pathlib import Path
import base64
import re

#importlib.reload(Utils)

blank_profile_img = r"C:\Users\USER\data_science\bank_project\blank_profile.jpeg"

st.set_page_config(page_title="Diamond Bank (Demo)", layout="centered", page_icon=":bank:", initial_sidebar_state="collapsed")

#initialize Database

init_db()

#PAGE CONTROLLER
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page):
    st.session_state.page = page
    st.rerun()

def back_to_home():
    if st.button("⬅ Return", key=f"back_home_{st.session_state.page}"):
        go_to("home")

# ------------------------------------------------

fe.inject_global_css()

st.markdown("""
<style>

/* ----------- MOBILE FIRST ----------- */
@media (max-width: 768px) {

    .block-container {
        padding: 1rem 0.8rem !important;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    button[kind="primary"],
    button[kind="secondary"] {
        width: 100% !important;
    }

    form {
        padding: 0 !important;
    }

    img {
        max-width: 100%;
        height: auto;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }
}

/* ----------- DESKTOP ----------- */
@media (min-width: 769px) {
    section[data-testid="stSidebar"] {
        display: block;
    }
}

</style>
""", unsafe_allow_html=True)

#HELPERS
def register_user_form():
    st.subheader("Create Account")

    with st.form("register_form", clear_on_submit=False):
        account_name = st.text_input(
            "Account Name",
            placeholder="Enter your full name"
        )

        account_num = st.text_input(
            "Account Number",
            placeholder="Account number must be 10 digits",
            max_chars=10
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Choose a secure password"
        )

        submit = st.form_submit_button("Register")

        if submit:
            #Validation: digits only & exactly 10 characters
            if not account_num.isdigit():
                st.error("Account number must contain digits only.")
                return

            if len(account_num) != 10:
                st.error("Account number must be exactly 10 digits.")
                return

            if not account_name.strip():
                st.error("Account name cannot be empty.")
                return

            if len(password) < 4:
                st.error("Password must be at least 4 characters.")
                return

            #Convert AFTER validation
            account_num = int(account_num)

            #Proceed with DB creation
            success = create_user(
                account_num=account_num,
                account_name=account_name,
                account_password=password
            )

            if success:
                st.success("Account created successfully 🎉")
            else:
                st.error("Account number already exists.")


def login_form():
    st.markdown("## Login")
    with st.form("login_form"):
        acc_num = st.text_input("Account number", placeholder="Enter digits only")
        password = st.text_input("Password / PIN", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            with st.spinner("Logging in..."):
                time.sleep(4)  #simulate network / DB delay
            user = authenticate(int(acc_num), str(password).strip())
            if user:
                st.session_state.user = user
                st.session_state.logged_in = True
                st.success("Login successful!")
                time.sleep(2)
                #Redirect to navigation guide sub-page
                st.session_state.page = None
                go_to("navigation")
                
                st.rerun()
                
            else:
                st.error("Incorrect account number or password.")



def navigation():
    #Function that teaches user how to navigate through the app

    #IMAGE PATH
    nav_img_path = Path("assets/navigation_dark.png")

    if nav_img_path.exists():
        #Encode image to base64
        with open(nav_img_path, "rb") as f:
            data = f.read()
            data_url = base64.b64encode(data).decode()

        #Inject CSS for full background
        st.markdown(
            f"""
            <style>
            .full-bg {{
                background-image: url("data:image/png;base64,{data_url}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                height: 100vh;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: white;
            }}
            .overlay-box {{
                background-color: rgba(0, 0, 0, 0.5);
                padding: 25px;
                border-radius: 12px;
                text-align: center;
            }}
            .got-it-btn {{
                margin-top: 20px;
                font-size: 18px;
                padding: 12px 30px;
                border-radius: 10px;
                background-color: #FFD700;
                color: black;
                font-weight: bold;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

       
        st.markdown(
            """
            <div class="full-bg">
                <div class="overlay-box">
                    <h1>👋 Welcome to Diamond Bank</h1>
                    <p>Use the sidebar on the left to navigate through the app.</p>
                    <ul style="text-align:left;">
                        <li>🏠 Home — view balance & transfers</li>
                        <li>👤 Profile — manage account info</li>
                        <li>🚪 Logout — end your session securely</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        #Fallback if image not found
        st.markdown(
            "### 👋 Welcome to Diamond Bank\nUse the sidebar to navigate through the app."
        )

    # # ---------------- GOT IT BUTTON ----------------
    # btn_col = st.empty()
    # if btn_col.button("Got it! Take me to Home", key="got_it_home"):
    #     st.session_state.show_navigation = False
    #     st.session_state.page = "home"
    #     st.rerun()




def detect_network(phone: str):
    prefixes = {
        "MTN": ["0803", "0806", "0703", "0706", "0813", "0816", "0903", "0906"],
        "Airtel": ["0802", "0808", "0708", "0812", "0902", "0907"],
        "Glo": ["0805", "0807", "0705", "0811", "0815", "0905"],
        "9mobile": ["0809", "0817", "0818", "0909"]
    }

    for network, codes in prefixes.items():
        if phone[:4] in codes:
            return network
    return "Unknown"



#__________Utility pages_______________
def airtime_page(user):
    back_to_home()
    st.title("Buy Airtime")

    with st.form("airtime_form"):
        phone = st.text_input("Mobile Number", placeholder="080XXXXXXXX")
        amount = st.number_input("Amount (₦)", min_value=50.0, step=50.0)

        network = detect_network(phone) if phone else "—"
        st.info(f"Detected Network: **{network}**")

        submit = st.form_submit_button("Buy Airtime")

        if submit:
            if network == "Unknown":
                st.error("Unable to detect network provider")
            elif amount > user["account_balance"]:
                st.error("Insufficient balance")
            else:
                update_balance(user["account_num"], user["account_balance"] - amount)
                add_transaction(user["account_num"], "out", amount, f"Airtime to {phone}")
                st.success("Airtime purchase successful!")
                st.balloons()


def data_page(user):
    back_to_home()
    st.title("Buy Data")

    with st.form("data_form"):
        phone = st.text_input("Mobile Number")
        plan = st.selectbox("Data Plan", ["500MB", "1GB", "2GB", "5GB"])
        amount_map = {"500MB": 300, "1GB": 600, "2GB": 1200, "5GB": 2500}

        network = detect_network(phone) if phone else "—"
        st.info(f"Detected Network: **{network}**")

        submit = st.form_submit_button("Buy Data")

        if submit:
            cost = amount_map[plan]
            if cost > user["account_balance"]:
                st.error("Insufficient balance")
            else:
                update_balance(user["account_num"], user["account_balance"] - cost)
                add_transaction(user["account_num"], "out", cost, f"{plan} Data to {phone}")
                st.success("Data purchase successful!")


def betting_page(user):
    back_to_home()
    st.title("Fund Betting Wallet")

    with st.form("betting_form"):
        platform = st.selectbox("Betting Platform", ["SportyBet", "Bet9ja", "1xBet"])
        bet_id = st.text_input("Betting ID")
        amount = st.number_input("Amount", min_value=100.0)

        submit = st.form_submit_button("Fund Wallet")

        if submit:
            if amount > user["account_balance"]:
                st.error("Insufficient funds")
            else:
                update_balance(user["account_num"], user["account_balance"] - amount)
                add_transaction(user["account_num"], "out", amount, f"{platform} funding")
                st.success("Betting wallet funded successfully!")


def tv_page(user):
    back_to_home()
    st.title("TV Subscription")

    with st.form("tv_form"):
        provider = st.selectbox("TV Provider", ["DSTV", "GOTV", "Startimes"])
        smartcard = st.text_input("Smartcard Number")
        bouquet = st.selectbox("Bouquet", ["Basic", "Compact", "Premium"])
        amount = st.number_input("Amount", min_value=1000.0)

        submit = st.form_submit_button("Subscribe")

        if submit:
            update_balance(user["account_num"], user["account_balance"] - amount)
            add_transaction(user["account_num"], "out", amount, f"{provider} subscription")
            st.success("TV subscription successful!")


def safebox_page(user):
    back_to_home()
    st.title("Safebox Savings")

    amount = st.number_input("Amount to lock", min_value=500.0)
    duration = st.selectbox("Duration", ["30 days", "90 days", "180 days"])

    if st.button("Lock Funds"):
        update_balance(user["account_num"], user["account_balance"] - amount)
        add_transaction(user["account_num"], "out", amount, f"Safebox ({duration})")
        st.success("Funds locked successfully!")


def loan_page(user):
    back_to_home()
    st.title("Instant Loan")

    amount = st.number_input("Loan Amount", min_value=5000.0)
    tenure = st.selectbox("Tenure", ["30 days", "60 days", "90 days"])

    if st.button("Apply for Loan"):
        st.success("Loan request submitted for review")


def donation_page(user):
    back_to_home()
    st.title("Play4aChild Donation")

    amount = st.number_input("Donation Amount", min_value=100.0)
    message = st.text_area("Optional Message")

    if st.button("Donate"):
        update_balance(user["account_num"], user["account_balance"] - amount)
        add_transaction(user["account_num"], "out", amount, "Donation")
        st.success("Thank you for your generosity ❤️")


def more_page(user):
    back_to_home()
    st.title("More Services")
    st.info("Coming soon: Insurance, FOREX, Investments, Crypto, Travel")



#_______ HOME PAGE ____________
def home_page(user):
    st.markdown("# Home")
    fe.header_with_logo(user['account_name'], user['account_balance'], st.session_state.profile_img)
    st.markdown("---")

    #ACTION BUTTONS
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("logo_path/to_bank.png", width=50)
        if st.button("To OPay", key="btn_to_opay"):
            go_to("to_opay")

    with col2:
        st.image("logo_path/to_credit.png", width=50)
        if st.button("To Bank", key="btn_to_bank"):
            go_to("transfer")

    with col3:
        st.image("logo_path/to_withdrawal.png", width=50)
        if st.button("Withdraw", key="btn_withdraw"):
            go_to("withdraw")

    st.markdown("---")


    #ICON GRID
    icons = [
        ("Airtime", "airtime"),
        ("Data", "data"),
        ("Betting", "betting"),
        ("TV", "tv"),
        ("Safebox", "safebox"),
        ("Loan", "loan"),
        ("Play4aChild", "donation"),
        ("More", "more")
    ]

    cols = st.columns(4)

    for idx, (label, page_name) in enumerate(icons):
        with cols[idx % 4]:
            st.image(f"logo_path/{label}.png", width=45)
            if st.button(label, key=f"btn_{label}"):
                go_to(page_name)


    st.markdown("---")

    txns = get_transactions(user['account_num'], limit=8)
    fe.transactions_list(txns)


#PAGES
def to_opay(user):
    back_to_home()
    st.title("Send to OPay")
    with st.form("to_opay_form"):

        number = st.text_input("OPay Number")
        amount = st.number_input("Amount", min_value=0.0)
        send = st.form_submit_button("Send")

        if send:
            with st.spinner("Validating. Please wait..."):
                time.sleep(4)  #simulate network / DB delay
                st.success("Transfer to OPay Successful!")
                st.balloons()


import uuid
from datetime import datetime

def transfer_page(user):
    back_to_home()
    st.title("Transfer to Bank")

    #FORM
    with st.form("bank_transfer_form"):
        rcvr_acc = st.text_input("Account Number")
        amt = st.number_input("Amount", min_value=0.0)
        txt = st.text_input("Transfer description")
        done = st.form_submit_button("Transfer")

        if done:
            if amt > 0:
                #PERFORM TRANSFER
                transfer(user["account_num"], rcvr_acc, amt, txt)
                with st.spinner("Sending. Please wait..."):
                    time.sleep(4)  #simulate network / DB delay
                    #STORE RECEIPT DATA IN SESSION
                    st.session_state.transfer_receipt = {
                        "ref": f"DB-{uuid.uuid4().hex[:10].upper()}",
                        "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        "sender_name": user["account_name"],
                        "sender_acc": user["account_num"],
                        "receiver_acc": rcvr_acc,
                        "amount": amt,
                        "narration": txt or "Bank Transfer",
                    }

                    st.success("Transfer Successful!", icon="✅")
                    st.balloons()

            else:
                st.warning("⚠ Transfer Amount must be more than 0")

    #RECEIPT (OUTSIDE FORM)
    if "transfer_receipt" in st.session_state:
        r = st.session_state.transfer_receipt

        st.markdown("---")
        st.subheader("🧾 Transaction Receipt")

        receipt_text = f"""
DIAMOND BANK – TRANSFER RECEIPT
----------------------------------------
Transaction Reference: {r['ref']}
Date & Time: {r['time']}

Sender:
Name: {r['sender_name']}
Account Number: {r['sender_acc']}

Receiver:
Account Number: {r['receiver_acc']}

Transaction Details:
Amount: ₦{r['amount']:,.2f}
Narration: {r['narration']}

Status: Successful ✅
----------------------------------------
Thank you for banking with Diamond Bank
"""

        st.markdown(
            f"""
            <div style="
                background:#0a1a2f;
                padding:20px;
                border-radius:12px;
                border:1px solid #e0e6ef;
                font-family:monospace;
                white-space:pre-wrap;
            ">
{receipt_text}
            
            """,
            unsafe_allow_html=True
        )

        #DOWNLOAD BUTTON
        st.download_button(
            label="📄 Download Receipt",
            data=receipt_text,
            file_name=f"DiamondBank_Receipt_{r['ref']}.txt",
            mime="text/plain"
        )



def withdraw_page(user):
    back_to_home()
    st.title("Withdraw Cash")
    with st.form("withdraw_form"):
        amt = st.number_input("Amount", min_value=0.0)
        withdraw = st.form_submit_button("Withdraw")

        if withdraw:
            st.success("Withdrawal successful!")
            st.balloons()


def get_profile_image():
    if "profile_image" in st.session_state:
        return st.session_state.profile_img
    return fe.img_converter("blank_profile_img")


def profile(user):
    #Extract from user dict
    username = user.get("account_name")
    balance = user.get("account_balance", 0.0)
    tier = user.get("account_tier", "Basic")
    acc_limit = user.get("account_limit", "₦200,000")
        #INIT PROFILE IMAGE
    if "profile_img" not in st.session_state:
        img_from_db = user.get("profile_img")

        if isinstance(img_from_db, str) and img_from_db.startswith("data:image"):
            st.session_state.profile_img = img_from_db
        else:
            st.session_state.profile_img = fe.img_converter(blank_profile_img)
    
    
    st.markdown("""
    <style>
    .profile-card {
        background: linear-gradient(135deg, #f2faff, #01ffff);
        border-radius: 16px;
        padding: 3px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .profile-header {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .profile-img {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #0a5;
    }

    .stat-card {
        background: white;
        padding: 1px;
        border-radius: 14px;
        border: 1px solid #e6f1ff;
        text-align: center;
    }
                

    .stat-card h4 {
        margin: 0;
        color: #666;
        font-size: 20px;
    }

    .stat-card h2 {
        margin: 1px 10 10;
        color: #0a9;
    }

    .section-title {
        font-weight: 600;
        margin-bottom: 10px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # # ---------------- PROFILE IMAGE ----------------
    # if "profile_img" not in st.session_state:
    #     st.session_state.profile_img = fe.img_converter(blank_profile_img)

    st.markdown('<div class="profile-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([0.7, 4])

    with col1:
        st.markdown(
            f'<img src="{st.session_state.profile_img}" class="profile-img"/>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(f"### {username}")
        st.markdown("💎 Diamond Bank User")

    st.markdown("</div>", unsafe_allow_html=True)

    #IMAGE UPLOAD / CAPTURE
    st.markdown("### Update Profile Photo")

    tab1, tab2 = st.tabs(["📁 Upload", "📷 Camera"])
    with tab2:
        cam_img = st.camera_input("Capture image", width=500)
        if cam_img:
            img_b64 = fe.img_converter(cam_img)
            st.session_state.profile_img = img_b64
            update_profile_img(user["account_num"], img_b64)
            st.success("Profile photo updated!")
            # st.rerun()

    with tab1:
        file_img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        if file_img:
            img_b64 = fe.img_converter(file_img)
            st.session_state.profile_img = img_b64
            update_profile_img(user["account_num"], img_b64)
            st.success("Profile photo updated!")
            # st.rerun()
    st.write("---")

    #ACCOUNT STATS
    st.markdown("### Account Overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="stat-card">
                <h4>Balance</h4>
                <h2>₦{balance:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat-card">
                <h4>Account Tier</h4>
                <h2>{tier}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat-card">
                <h4>Limit</h4>
                <h2>{acc_limit}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("---")

    #ACTIONS
    st.markdown("### Account Actions")

    if st.button("📄 View Transaction History"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        # st.session_state.page = "home"
        st.success("Logged out successfully")




#APP FLOW
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if "show_navigation" not in st.session_state:
    st.session_state.show_navigation = False
if 'page' not in st.session_state:
    st.session_state.page = "login_navigation"  # start with login navigation after login



#PROFILE IMAGE SESSION INIT
# if "profile_img" not in st.session_state:
#     img_from_db = user.get("profile_img")

#     if isinstance(img_from_db, str) and img_from_db.startswith("data:image"):
#         st.session_state.profile_img = img_from_db
#     else:
#         st.session_state.profile_img = fe.img_converter(blank_profile_img)

st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to", ["Login", "Create", "Home", "Profile", "Logout"])

if nav == "Login":
    
    if not st.session_state.logged_in:
        login_form()
    if st.session_state.logged_in and st.session_state.user:
        user = get_user(st.session_state.user['account_num'])
        st.session_state.user = user

        page = st.session_state.get("page", "home")

        if page =="navigation":
            navigation()

elif nav == "Create":
    register_user_form()

elif nav == "Home":
    if st.session_state.logged_in and st.session_state.user:
        user = get_user(st.session_state.user['account_num'])
        st.session_state.user = user

        # ===================== ADDED =====================
        # Show navigation onboarding AFTER LOGIN (once)
        # if st.session_state.get("show_navigation", False):
        #     navigation()   # <-- onboarding guide
            # return
        # =================== END ADDED ===================


        #SYNC PROFILE IMAGE FROM db
        if user.get("profile_img"):
            st.session_state.profile_img = user["profile_img"]

            

        page = st.session_state.get("page", "home")

        if page =="navigation":
            home_page(user)
        elif page == "home":
            home_page(user)
        elif page == "to_opay":
            to_opay(user)
        elif page == "transfer":
            transfer_page(user)
        elif page == "withdraw":
            withdraw_page(user)
        elif page == "airtime":
            airtime_page(user)

        elif page == "data":
            data_page(user)

        elif page == "betting":
            betting_page(user)

        elif page == "tv":
            tv_page(user)

        elif page == "safebox":
            safebox_page(user)

        elif page == "loan":
            loan_page(user)

        elif page == "donation":
            donation_page(user)

        elif page == "more":
            more_page(user)

    else:
        st.warning("You must be logged in to view Home.")

elif nav == "Profile":
    if st.session_state.user:
        user = get_user(st.session_state.user['account_num'])
        st.session_state.user = user
        #KEEP PROFILE IMAGE IN SYNC
        if user.get("profile_img"):
            st.session_state.profile_img = user["profile_img"]

        profile(user)

elif nav == "Logout":
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "home"
    #RESET PROFILE IMAGE
    st.session_state.profile_img = fe.img_converter(blank_profile_img)
    
    st.info("Logged out.")
