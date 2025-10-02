"""
Main Application Launcher for AISB Student Management System
"""
import streamlit as st
from streamlit_option_menu import option_menu

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
    
    # Terminal selection
    selected = option_menu(
        menu_title=None,
        options=["Student Portal", "Admin Terminal"],
        icons=["person-circle", "gear-fill"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )
    
    # Route to appropriate terminal
    if selected == "Student Portal":
        student_terminal = StudentTerminal()
        student_terminal.run()
    elif selected == "Admin Terminal":
        admin_terminal = AdminTerminal()
        admin_terminal.run()

if __name__ == "__main__":
    main()
