"""
IT Helpdesk Chatbot
===================
A simple chatbot built with Python and Streamlit that helps users
solve common IT problems like Wi-Fi issues, forgotten passwords,
slow computers, printer problems, and software installation.

The chatbot uses keyword matching against a predefined knowledge base.
No AI models or external APIs are required.
"""

import streamlit as st
import re
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# Each entry has:
#   - "keywords" : words/phrases the user might type
#   - "answer"   : the helpful response
#   - "title"    : short label shown in the sidebar's common-problems list
# ──────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = [
    {
        "keywords": ["wifi", "wi-fi", "internet", "network", "connected", "no internet",
                      "can't connect", "connection", "wireless", "disconnected", "online"],
        "title": "🌐 Wi-Fi / Internet Issues",
        "answer": (
            "Here are some steps to fix **Wi-Fi / Internet issues**:\n\n"
            "1. **Toggle Wi-Fi** — Turn Wi-Fi off, wait 10 seconds, then turn it back on.\n"
            "2. **Restart your router** — Unplug it for 30 seconds, then plug it back in.\n"
            "3. **Forget & reconnect** — Go to Wi-Fi settings, forget the network, and reconnect with your password.\n"
            "4. **Check Airplane Mode** — Make sure Airplane Mode is turned off.\n"
            "5. **Run the Network Troubleshooter** (Windows) — "
            "Go to *Settings → Network & Internet → Network Troubleshooter*.\n"
            "6. **Flush DNS** — Open Command Prompt and type `ipconfig /flushdns`.\n\n"
            "If the problem continues, please contact the **IT Support Team**."
        ),
    },
    {
        "keywords": ["password", "forgot password", "reset password", "locked out",
                      "can't login", "can't log in", "login", "log in", "sign in",
                      "account locked", "unlock", "credentials"],
        "title": "🔑 Password / Login Problems",
        "answer": (
            "Here's how to handle **password and login problems**:\n\n"
            "1. **Use the 'Forgot Password' link** on the login page to reset your password.\n"
            "2. **Check Caps Lock** — Passwords are case-sensitive.\n"
            "3. **Clear browser cache** — Old saved passwords can cause conflicts.\n"
            "4. **Try a different browser** — Sometimes browser extensions interfere.\n"
            "5. **Wait 15 minutes** — If your account is locked, it may auto-unlock after a cooldown period.\n\n"
            "If you still can't log in, contact the **IT Support Team** to manually reset your account."
        ),
    },
    {
        "keywords": ["slow", "lagging", "freezing", "hanging", "performance", "speed",
                      "takes long", "not responding", "unresponsive", "sluggish", "lag"],
        "title": "🐢 Slow Computer",
        "answer": (
            "Try these steps to **speed up your computer**:\n\n"
            "1. **Restart your computer** — This clears temporary files and refreshes memory.\n"
            "2. **Close unused programs** — Check the Task Manager (Ctrl+Shift+Esc) for high-usage apps.\n"
            "3. **Free up disk space** — Delete old files or use *Disk Cleanup* (Windows).\n"
            "4. **Disable startup programs** — Open Task Manager → Startup tab → disable unnecessary items.\n"
            "5. **Check for malware** — Run a full scan with your antivirus software.\n"
            "6. **Update your OS** — Install the latest operating system updates.\n\n"
            "If your computer is still slow, it may need a hardware upgrade — contact the **IT Support Team**."
        ),
    },
    {
        "keywords": ["printer", "print", "printing", "paper jam", "not printing",
                      "offline printer", "scanner", "scan", "toner", "ink",
                      "print queue", "spooler"],
        "title": "🖨️ Printer Problems",
        "answer": (
            "Here are solutions for common **printer problems**:\n\n"
            "1. **Check the connection** — Make sure the printer is turned on and connected (USB or Wi-Fi).\n"
            "2. **Set as default printer** — Go to *Settings → Devices → Printers & Scanners* "
            "and set the correct printer as default.\n"
            "3. **Clear the print queue** — Open the printer queue and cancel all pending documents.\n"
            "4. **Restart the Print Spooler** — Open *Services* (services.msc), find *Print Spooler*, "
            "and click *Restart*.\n"
            "5. **Check paper & ink/toner** — Refill paper or replace cartridges if needed.\n"
            "6. **Reinstall the printer driver** — Remove the printer and add it again.\n\n"
            "For persistent issues, please contact the **IT Support Team**."
        ),
    },
    {
        "keywords": ["install", "software", "application", "app", "program", "setup",
                      "download", "update", "upgrade", "uninstall", "remove",
                      "installation", "not installing"],
        "title": "💿 Software Installation",
        "answer": (
            "Steps for **software installation issues**:\n\n"
            "1. **Run as Administrator** — Right-click the installer and select *Run as Administrator*.\n"
            "2. **Check system requirements** — Make sure your computer meets the software's minimum requirements.\n"
            "3. **Disable antivirus temporarily** — Some antivirus programs block installations.\n"
            "4. **Free up disk space** — Ensure you have enough storage for the software.\n"
            "5. **Download from the official website** — Avoid third-party download sites.\n"
            "6. **Restart and retry** — A fresh restart often resolves installation glitches.\n\n"
            "If you need a specific piece of software installed, please submit a request to the "
            "**IT Support Team**."
        ),
    },
    {
        "keywords": ["email", "outlook", "mail", "inbox", "send", "receive",
                      "attachment", "spam", "junk", "phishing"],
        "title": "📧 Email Issues",
        "answer": (
            "Here's how to troubleshoot **email issues**:\n\n"
            "1. **Check your internet connection** — Email requires a stable connection.\n"
            "2. **Check the Junk/Spam folder** — Your email may have been filtered there.\n"
            "3. **Clear the Outlook cache** — Close Outlook, delete the OST file, and reopen.\n"
            "4. **Check attachment size** — Most email servers limit attachments to 25 MB.\n"
            "5. **Update Outlook** — Go to *File → Office Account → Update Options → Update Now*.\n"
            "6. **Remove and re-add your account** — Sometimes re-authenticating fixes sync problems.\n\n"
            "If email is still not working, contact the **IT Support Team**."
        ),
    },
    {
        "keywords": ["vpn", "remote", "work from home", "connect remotely",
                      "remote desktop", "rdp", "virtual private network"],
        "title": "🔒 VPN / Remote Access",
        "answer": (
            "Solutions for **VPN and remote access issues**:\n\n"
            "1. **Check your internet connection** — VPN needs a stable connection first.\n"
            "2. **Restart the VPN client** — Close it completely and reopen.\n"
            "3. **Use the correct server** — Make sure you're connecting to the right VPN server address.\n"
            "4. **Update the VPN software** — Outdated clients can cause connection failures.\n"
            "5. **Disable firewall temporarily** — Some firewalls block VPN traffic.\n"
            "6. **Try a different network** — Some public Wi-Fi networks block VPN connections.\n\n"
            "If you still can't connect, contact the **IT Support Team** for remote assistance."
        ),
    },
    {
        "keywords": ["blue screen", "bsod", "crash", "error", "bug", "broken",
                      "not working", "shutdown", "restart loop", "black screen"],
        "title": "💥 System Errors / Crashes",
        "answer": (
            "Steps to handle **system errors and crashes**:\n\n"
            "1. **Restart your computer** — This fixes many temporary glitches.\n"
            "2. **Note the error code** — If you see a blue screen, write down the error code.\n"
            "3. **Boot into Safe Mode** — Press F8 or Shift+Restart to access Safe Mode.\n"
            "4. **Run System File Checker** — Open Command Prompt as Admin and type `sfc /scannow`.\n"
            "5. **Check for updates** — Install the latest Windows/macOS updates.\n"
            "6. **Check disk health** — Run `chkdsk /f` in Command Prompt.\n\n"
            "If crashes persist, please contact the **IT Support Team** immediately."
        ),
    },
    {
        "keywords": ["monitor", "display", "screen", "resolution", "dual monitor",
                      "second screen", "external display", "hdmi", "no display",
                      "blank screen", "flickering"],
        "title": "🖥️ Display / Monitor Issues",
        "answer": (
            "Troubleshooting **display and monitor issues**:\n\n"
            "1. **Check the cable** — Make sure the HDMI/DisplayPort/VGA cable is firmly connected.\n"
            "2. **Try a different port** — Switch to another video output port on your computer.\n"
            "3. **Adjust resolution** — Right-click the desktop → *Display Settings* → adjust resolution.\n"
            "4. **Update display drivers** — Go to *Device Manager → Display Adapters → Update Driver*.\n"
            "5. **Detect displays** — Go to *Display Settings* and click *Detect* for external monitors.\n"
            "6. **Restart your computer** — A reboot often resolves display glitches.\n\n"
            "If the issue continues, contact the **IT Support Team**."
        ),
    },
    {
        "keywords": ["audio", "sound", "speaker", "headphone", "microphone", "mic",
                      "no sound", "volume", "mute", "earphone"],
        "title": "🔊 Audio / Sound Problems",
        "answer": (
            "Fixing **audio and sound problems**:\n\n"
            "1. **Check the volume** — Make sure it isn't muted or set to zero.\n"
            "2. **Check the output device** — Right-click the speaker icon → *Sound Settings* "
            "→ select the correct output.\n"
            "3. **Reconnect headphones/speakers** — Unplug and replug your audio device.\n"
            "4. **Update audio drivers** — Go to *Device Manager → Sound Controllers → Update Driver*.\n"
            "5. **Run the audio troubleshooter** — *Settings → System → Sound → Troubleshoot*.\n"
            "6. **Restart the Windows Audio service** — Open *services.msc* and restart *Windows Audio*.\n\n"
            "Still no luck? Contact the **IT Support Team**."
        ),
    },
]

# Quick replies the user can send with one click
GREETING_KEYWORDS = ["hello", "hi", "hey", "good morning", "good afternoon",
                     "good evening", "howdy", "greetings"]

THANK_KEYWORDS = ["thank", "thanks", "thank you", "thx", "appreciate"]

HELP_KEYWORDS = ["help", "support", "assist", "what can you do", "options",
                 "menu", "topics"]


# ──────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def find_best_answer(user_message: str) -> str:
    """
    Match the user's message against the knowledge base using keyword counting.
    Returns the best-matching answer, or a fallback message.
    """
    # Normalise: lowercase, keep only letters, digits, and spaces
    cleaned = re.sub(r"[^a-z0-9\s]", "", user_message.lower())

    # --- Check for greetings ---
    if any(word in cleaned.split() for word in GREETING_KEYWORDS):
        return (
            "Hello! 👋 I'm your **IT Helpdesk Assistant**.\n\n"
            "Tell me about your IT problem and I'll do my best to help!\n\n"
            "For example, you can ask about:\n"
            "- Wi-Fi not working\n"
            "- Forgotten passwords\n"
            "- Slow computer\n"
            "- Printer problems\n"
            "- Software installation\n"
        )

    # --- Check for thank-you ---
    if any(word in cleaned for word in THANK_KEYWORDS):
        return (
            "You're welcome! 😊 Happy I could help.\n\n"
            "If you run into anything else, just ask!"
        )

    # --- Check for generic help ---
    if any(word in cleaned.split() for word in HELP_KEYWORDS):
        topics = "\n".join(f"- {entry['title']}" for entry in KNOWLEDGE_BASE)
        return (
            "I can help you with the following topics:\n\n"
            f"{topics}\n\n"
            "Just describe your problem in your own words!"
        )

    # --- Keyword matching against the knowledge base ---
    best_score = 0
    best_answer = ""

    for entry in KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in cleaned)
        if score > best_score:
            best_score = score
            best_answer = entry["answer"]

    if best_score > 0:
        return best_answer

    # --- Fallback ---
    return (
        "I'm sorry, I couldn't find a solution for your issue. 😔\n\n"
        "Please contact the **IT Support Team** for further assistance:\n\n"
        "- 📧 Email: **itsupport@company.com**\n"
        "- 📞 Phone: **+1 (555) 123-4567**\n"
        "- 🕐 Hours: Mon – Fri, 8:00 AM – 6:00 PM\n\n"
        "You can also try describing your problem differently and I'll try again!"
    )


# ──────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IT Helpdesk Chatbot",
    page_icon="🛠️",
    layout="centered",
)

# ──────────────────────────────────────────────────────────────────────
# CUSTOM STYLING
# ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ---------- Global ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1);
    }

    /* ---------- Chat messages ---------- */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 4px;
        padding: 6px 10px;
    }

    /* ---------- Chat input ---------- */
    .stChatInput > div {
        border-radius: 12px !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* ---------- Quick-reply pills ---------- */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        border-radius: 20px;
        padding: 4px 16px;
        font-size: 0.85rem;
    }

    /* ---------- Hide the default Streamlit footer ---------- */
    footer {visibility: hidden;}

    /* ---------- Sidebar topic cards ---------- */
    .topic-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 6px;
        font-size: 0.9rem;
        transition: background 0.2s;
    }
    .topic-card:hover {
        background: rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────
# SESSION STATE — keeps chat history between reruns
# ──────────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    # Start with a welcome message from the assistant
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 **Welcome to the IT Helpdesk!**\n\n"
                "I'm here to help you with common IT issues. "
                "Just type your problem below and I'll guide you through the solution.\n\n"
                "You can ask about things like:\n"
                "- *\"My Wi-Fi isn't working\"*\n"
                "- *\"I forgot my password\"*\n"
                "- *\"My computer is very slow\"*\n"
                "- *\"The printer won't print\"*\n"
                "- *\"I can't install software\"*\n\n"
                "How can I help you today? 😊"
            ),
        }
    ]


# ──────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────

with st.sidebar:
    # Chatbot branding
    st.markdown("## 🛠️ IT Helpdesk Bot")
    st.caption("Your friendly IT assistant — available 24/7")
    st.divider()

    # Instructions
    st.markdown("### 📖 How to Use")
    st.markdown(
        "1. Type your IT problem in the chat box.\n"
        "2. Read the suggested solution.\n"
        "3. If unsolved, contact the IT team."
    )
    st.divider()

    # Common topics list (rendered as styled cards)
    st.markdown("### 📋 Common Topics")
    for entry in KNOWLEDGE_BASE:
        st.markdown(
            f'<div class="topic-card">{entry["title"]}</div>',
            unsafe_allow_html=True,
        )
    st.divider()

    # Clear chat button
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Chat cleared! 🧹\n\n"
                    "How can I help you today?"
                ),
            }
        ]
        st.rerun()

    # Footer
    st.divider()
    st.caption(f"© {datetime.now().year} IT Helpdesk Bot • v1.0")


# ──────────────────────────────────────────────────────────────────────
# MAIN CHAT AREA
# ──────────────────────────────────────────────────────────────────────

st.markdown("## 💬 IT Helpdesk Chat")

# Render all messages in the chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Quick-reply suggestion buttons (shown below the chat)
st.markdown("")  # small spacer
quick_cols = st.columns(5)
quick_prompts = ["Wi-Fi issue", "Forgot password", "Slow PC", "Printer help", "Install software"]
quick_clicked = None

for idx, col in enumerate(quick_cols):
    with col:
        if st.button(quick_prompts[idx], key=f"quick_{idx}"):
            quick_clicked = quick_prompts[idx]

# ──────────────────────────────────────────────────────────────────────
# HANDLE USER INPUT
# ──────────────────────────────────────────────────────────────────────

# Either the user types in the chat input or clicks a quick-reply button
user_input = st.chat_input("Describe your IT problem here…")

# If a quick-reply was clicked, treat it as the user's message
if quick_clicked:
    user_input = quick_clicked

if user_input:
    # 1. Show and store the user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Generate the bot's reply
    bot_reply = find_best_answer(user_input)

    # 3. Show and store the bot's reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    # 4. Rerun to update quick-reply buttons' state
    st.rerun()
