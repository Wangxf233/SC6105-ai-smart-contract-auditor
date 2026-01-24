import streamlit as st
from src.logic import initialize_qa_chain, run_heuristic_checks, analyze_code_with_ai
from src.logger_config import logger

# --- User Interface ---
st.set_page_config(
    page_title="Auditor AI - Smart Contract Security",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
with st.sidebar:
    # Logo/Title
    st.title("🤖 Auditor AI")

    # User Login Status (TODO: 集成认证模块)
    st.markdown("---")
    if 'user_id' in st.session_state:
        st.success(f"👤 Logged in as: **{st.session_state['user_id']}**")
        if st.button("🚪 Logout", use_container_width=True):
            # TODO: 清除session并重定向到登录页
            st.session_state.clear()
            st.rerun()
    else:
        st.info("👤 Guest Mode")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", use_container_width=True):
                # TODO: 跳转到登录页
                st.info("Login page coming soon!")
        with col2:
            if st.button("📝 Register", use_container_width=True):
                # TODO: 跳转到注册页
                st.info("Register page coming soon!")

    st.markdown("---")

    # Navigation
    st.subheader("📋 Navigation")

    # 使用session_state跟踪当前页面
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'audit'

    nav_buttons = {
        "🔍 Smart Audit": "audit",
        "📊 Dashboard": "dashboard",
        "📈 Statistics": "statistics"
    }

    for label, page in nav_buttons.items():
        if st.button(label, use_container_width=True, type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
            st.rerun()

    st.markdown("---")

    # About section
    st.subheader("ℹ️ About")
    st.markdown("""
    **Auditor AI** leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to analyze Solidity smart contracts for security vulnerabilities.
    
    **Features:**
    - 🔍 Heuristic analysis
    - 🤖 AI-powered deep analysis
    - 📊 Visual reports
    - 💾 Export to PDF/JSON
    
    **Disclaimer:** Educational tool only. Not a replacement for professional audits.
    """)

    st.markdown("---")
    st.subheader("💡 Example Queries")

    example_1 = st.button("Analyze for Reentrancy risks")
    example_2 = st.button("Check `tx.origin` usage")
    example_3 = st.button("Explain risks of outdated Solidity pragma")

# --- Main Page ---
st.title("🤖 Auditor: AI Smart Contract Security Assistant")
st.markdown("Enter your Solidity smart contract code or ask a security-related question below.")

# Quick actions bar
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("### 📝 Quick Actions")
with col2:
    if st.button("📜 View History", use_container_width=True):
        st.info("Navigate to Dashboard to view audit history")
with col3:
    if st.button("📊 View Stats", use_container_width=True):
        st.info("Navigate to Statistics page for detailed analytics")

st.markdown("---")

qa_chain = initialize_qa_chain()

if qa_chain:
    with st.form("audit_form"):
        if example_1:
            initial_input = "What is a reentrancy attack and how can I prevent it in my code?"
        elif example_2:
            initial_input = "function withdraw(uint amount) public { require(balances[msg.sender] >= amount); (bool success, ) = msg.sender.call{value: amount}(\"\"); require(success, \"Failed to send Ether\"); balances[msg.sender] -= amount; }"
        elif example_3:
            initial_input = "pragma solidity ^0.5.0;"
        else:
            initial_input = ""

        # Contract name and analysis mode
        col1, col2 = st.columns([3, 1])
        with col1:
            contract_name = st.text_input(
                "Contract Name (Optional):",
                placeholder="e.g., MyToken, DEXRouter",
                help="Give your contract a name for easier tracking"
            )
        with col2:
            analysis_mode = st.selectbox(
                "Analysis Mode:",
                ["Standard", "Deep", "Quick"],
                help="Choose analysis depth"
            )

        user_input = st.text_area(
            "Your Solidity Code or Security Question:",
            value=initial_input,
            height=300,
            placeholder="function transfer(address to, uint256 amount) public { ... }",
            help="Paste your Solidity code or ask a security question"
        )

        # Form submit buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            submitted = st.form_submit_button("🚀 Analyze Now", use_container_width=True, type="primary")
        with col2:
            clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)
        with col3:
            st.form_submit_button("💾 Save Draft", use_container_width=True, disabled=True)

    if submitted and user_input:
        logger.info(f"New submission received. Input length: {len(user_input)}. Contract: {contract_name}")

        # Create results container with tabs
        with st.container():
            tab1, tab2, tab3 = st.tabs(["🔍 Analysis Results", "📊 Summary", "💾 Export"])

            with tab1:
                st.subheader("Heuristic Analysis")
                with st.spinner("Running heuristic checks..."):
                    heuristic_alerts = run_heuristic_checks(user_input)

                    if heuristic_alerts:
                        for alert in heuristic_alerts:
                            st.markdown(alert)
                    else:
                        st.success("✅ No immediate issues detected by heuristic analysis.")

                st.markdown("---")

                st.subheader("Deep AI-Powered Analysis")
                with st.spinner(f"Auditor is performing {analysis_mode.lower()} analysis... This may take a moment."):
                    try:
                        analysis_result = analyze_code_with_ai(qa_chain, user_input)
                        st.markdown(analysis_result)

                        # Store result in session state for export
                        from datetime import datetime
                        st.session_state['last_analysis'] = {
                            'contract_name': contract_name or 'Unnamed Contract',
                            'raw_input': user_input,
                            'heuristic_alerts': heuristic_alerts,
                            'full_markdown_report': analysis_result,
                            'created_at': datetime.now().isoformat()
                        }

                    except Exception as e:
                        logger.critical(f"An unhandled exception occurred in the main analysis block: {e}", exc_info=True)
                        st.error("❌ A critical error occurred. The incident has been logged. Please check `auditor.log` for more details.")

            with tab2:
                st.subheader("📊 Analysis Summary")
                if 'last_analysis' in st.session_state:
                    summary_col1, summary_col2 = st.columns(2)

                    with summary_col1:
                        st.metric("Contract Name", st.session_state['last_analysis'].get('contract_name', 'N/A'))
                        st.metric("Heuristic Alerts", len(st.session_state['last_analysis'].get('heuristic_alerts', [])))

                    with summary_col2:
                        st.metric("Analysis Mode", analysis_mode)
                        st.metric("Input Size", f"{len(user_input)} chars")

                    st.info("💡 Navigate to Dashboard to view this report in your history.")
                else:
                    st.info("Run an analysis to see the summary.")

            with tab3:
                st.subheader("💾 Export Report")

                if 'last_analysis' in st.session_state:
                    export_col1, export_col2, export_col3 = st.columns(3)

                    with export_col1:
                        if st.button("📄 Export as Markdown", use_container_width=True):
                            from src.export_service import ExportService
                            md_content = ExportService.export_to_markdown(st.session_state['last_analysis'])
                            st.download_button(
                                label="📥 Download Markdown",
                                data=md_content,
                                file_name=f"audit_{contract_name or 'report'}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )

                    with export_col2:
                        if st.button("📋 Export as JSON", use_container_width=True):
                            from src.export_service import ExportService
                            json_content = ExportService.export_to_json(st.session_state['last_analysis'])
                            st.download_button(
                                label="📥 Download JSON",
                                data=json_content,
                                file_name=f"audit_{contract_name or 'report'}.json",
                                mime="application/json",
                                use_container_width=True
                            )

                    with export_col3:
                        if st.button("📕 Export as PDF", use_container_width=True):
                            try:
                                from src.export_service import ExportService
                                pdf_bytes = ExportService.export_to_pdf(st.session_state['last_analysis'])
                                st.download_button(
                                    label="📥 Download PDF",
                                    data=pdf_bytes,
                                    file_name=f"audit_{contract_name or 'report'}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"PDF export error: {str(e)}")

                    st.markdown("---")
                    st.success("✅ Export options available. Choose your preferred format above.")
                else:
                    st.info("Run an analysis first to enable export options.")

    elif clear_btn:
        st.info("Form cleared. Enter new code to analyze.")

else:
    st.warning("⚠️ The Auditor engine could not be initialized. Please check the console for errors and see `auditor.log`.")
    st.error("Please ensure:")
    st.markdown("""
    - ✅ FAISS index exists in `faiss_index/` directory
    - ✅ Google API key is set in `.env` file
    - ✅ All dependencies are installed
    """)

