"""
Simple Main Application Launcher for AISB Student Management System
(Without streamlit_option_menu dependency)
"""
import streamlit as st

# Import terminals
from terminals.admin_terminal import AdminTerminal
from terminals.student_terminal import StudentTerminal

def main():
    """Main application launcher"""
    st.set_page_config(
        page_title="AISB Student Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main header
    st.title("🎓 AISB Student Management System")
    st.markdown("### Artificial Intelligence Student Body - Powered by CrewAI")
    st.markdown("---")
    
    # Simple terminal selection using radio buttons
    st.subheader("Select Terminal")
    selected = st.radio(
        "Choose your interface:",
        ["Student Portal", "Admin Terminal"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Route to appropriate terminal
    if selected == "Student Portal":
        student_terminal = StudentTerminal()
        student_terminal.run()
    elif selected == "Admin Terminal":
        admin_terminal = AdminTerminal()
        admin_terminal.run()

if __name__ == "__main__":
    main()
