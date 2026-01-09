"""
Streamlit UI for easy document uploads.

Usage:
    streamlit run ingestion/streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pipeline import IngestionPipeline
from ingestion.loaders import DocumentLoaderFactory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="UoV AI Assistant - Document Upload",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'stats' not in st.session_state:
    st.session_state.stats = None


def initialize_pipeline():
    """Initialize ingestion pipeline."""
    if st.session_state.pipeline is None:
        with st.spinner("Initializing pipeline..."):
            st.session_state.pipeline = IngestionPipeline()
            st.session_state.stats = st.session_state.pipeline.get_stats()
        st.success("✅ Pipeline initialized!")


def process_uploaded_file(uploaded_file, clean_text):
    """Process an uploaded file."""
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Process file
        with st.spinner(f"Processing {uploaded_file.name}..."):
            st.session_state.pipeline.process_file(
                file_path=tmp_path,
                clean_text=clean_text
            )
        
        # Update stats
        st.session_state.stats = st.session_state.pipeline.get_stats()
        
        # Clean up temp file
        Path(tmp_path).unlink()
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return False, str(e)


# Main UI
st.title("📚 UoV AI Assistant - Document Upload")
st.markdown("Upload documents to add them to the knowledge base")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Initialize button
    if st.button("🔄 Initialize Pipeline", use_container_width=True):
        initialize_pipeline()
    
    # Clean text option
    clean_text = st.checkbox("Clean text before processing", value=True)
    
    st.divider()
    
    # Stats
    st.header("📊 Statistics")
    if st.session_state.stats:
        st.metric("Collection", st.session_state.stats['collection_name'])
        st.metric("Total Chunks", st.session_state.stats['total_chunks'])
        st.metric("Embedding Dim", st.session_state.stats['embedding_dimension'])
    else:
        st.info("Initialize pipeline to see stats")
    
    st.divider()
    
    # Help
    st.header("ℹ️ Help")
    st.markdown("""
    **Supported formats:**
    - PDF (.pdf)
    - Word (.docx, .doc)
    - HTML (.html, .htm)
    - Text (.txt)
    
    **Tips:**
    - Initialize pipeline first
    - Upload one file at a time
    - Check stats after upload
    """)

# Main content
if st.session_state.pipeline is None:
    st.warning("⚠️ Please initialize the pipeline first (see sidebar)")
else:
    # Create tabs for different file types
    tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF", "📝 Word", "🌐 HTML", "📃 Text"])
    
    # PDF Tab
    with tab1:
        st.subheader("Upload PDF Document")
        pdf_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            key='pdf_uploader',
            help="Upload a PDF document to add to the knowledge base"
        )
        
        if pdf_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📄 **{pdf_file.name}** ({pdf_file.size / 1024:.1f} KB)")
            with col2:
                if st.button("Process PDF", key='process_pdf', use_container_width=True):
                    success, error = process_uploaded_file(pdf_file, clean_text)
                    if success:
                        st.success(f"✅ Successfully processed {pdf_file.name}!")
                        st.balloons()
                    else:
                        st.error(f"❌ Error: {error}")
    
    # Word Tab
    with tab2:
        st.subheader("Upload Word Document")
        docx_file = st.file_uploader(
            "Choose a Word file",
            type=['docx', 'doc'],
            key='docx_uploader',
            help="Upload a Word document to add to the knowledge base"
        )
        
        if docx_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📝 **{docx_file.name}** ({docx_file.size / 1024:.1f} KB)")
            with col2:
                if st.button("Process Word", key='process_docx', use_container_width=True):
                    success, error = process_uploaded_file(docx_file, clean_text)
                    if success:
                        st.success(f"✅ Successfully processed {docx_file.name}!")
                        st.balloons()
                    else:
                        st.error(f"❌ Error: {error}")
    
    # HTML Tab
    with tab3:
        st.subheader("Upload HTML File")
        html_file = st.file_uploader(
            "Choose an HTML file",
            type=['html', 'htm'],
            key='html_uploader',
            help="Upload an HTML file to add to the knowledge base"
        )
        
        if html_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"🌐 **{html_file.name}** ({html_file.size / 1024:.1f} KB)")
            with col2:
                if st.button("Process HTML", key='process_html', use_container_width=True):
                    success, error = process_uploaded_file(html_file, clean_text)
                    if success:
                        st.success(f"✅ Successfully processed {html_file.name}!")
                        st.balloons()
                    else:
                        st.error(f"❌ Error: {error}")
    
    # Text Tab
    with tab4:
        st.subheader("Upload Text File")
        txt_file = st.file_uploader(
            "Choose a text file",
            type=['txt'],
            key='txt_uploader',
            help="Upload a text file to add to the knowledge base"
        )
        
        if txt_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📃 **{txt_file.name}** ({txt_file.size / 1024:.1f} KB)")
            with col2:
                if st.button("Process Text", key='process_txt', use_container_width=True):
                    success, error = process_uploaded_file(txt_file, clean_text)
                    if success:
                        st.success(f"✅ Successfully processed {txt_file.name}!")
                        st.balloons()
                    else:
                        st.error(f"❌ Error: {error}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>UoV AI Assistant - Document Ingestion | University of Vavuniya</small>
</div>
""", unsafe_allow_html=True)
