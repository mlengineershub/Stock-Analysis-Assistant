import streamlit as st
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend import process_query

# Set page config
st.set_page_config(
    page_title="Stock Analysis Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
    }
    .output-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("📈 Stock Analysis Assistant")
st.markdown("""
    Welcome to the Stock Analysis Assistant! I can help you analyze stocks by:
    - Providing insights from company reports
    - Analyzing recent financial news
    - Making investment recommendations
    
    Just ask me anything about a company or stock!
""")

# Example questions
st.markdown("### Example Questions")
examples = [
    "What are the latest developments for AAPL?",
    "Should I invest in NVDA based on recent news?",
    "What were Microsoft's key achievements in Q3 2023?",
]
for example in examples:
    st.markdown(f"- *{example}*")

# User input
user_question = st.text_input(
    "Ask your question:",
    placeholder="E.g., What are the latest developments for AAPL?",
    key="user_input"
)

# Process button
if st.button("Get Analysis", type="primary"):
    if user_question:
        try:
            with st.spinner("Analyzing... This might take a few moments."):
                response = process_query(user_question).content
                
                # Display response in a nice container
                st.markdown("<div class='output-container'>", unsafe_allow_html=True)
                st.markdown("### Analysis Result")
                st.write(response)
                st.markdown("</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"""
                😕 I encountered an error while processing your request.
                This might be due to:
                - Invalid company ticker
                - Connection issues
                - Service unavailability
                
                Please try again or rephrase your question.
            """)
    else:
        st.warning("Please enter a question first! 🤔")

# Footer
st.markdown("---")
st.markdown("""
    💡 **Tips:**
    - Use company ticker symbols (e.g., AAPL, MSFT, NVDA)
    - Be specific about what information you're looking for
    - Questions about recent developments work best
""")