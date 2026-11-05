import streamlit as st
from dotenv import load_dotenv
from granite_client import generate_learning_content

load_dotenv()
st.set_page_config(page_title="LearnEase AI", page_icon="🎓", layout="wide")
st.title("🎓 LearnEase AI")
st.subheader("AI-powered Course Content Simplification Agent")
st.write("Turn difficult academic topics into simple explanations and exam-ready study materials, powered by IBM watsonx.ai.")

with st.sidebar:
    st.header("Learning preferences")
    level=st.selectbox("Explanation level", ["Beginner","Intermediate","Exam-focused"])
    output_type=st.selectbox("Generate", ["Complete study pack","Simple explanation","Structured notes","Examples","Practice questions and answers","Quick summary"])

topic=st.text_input("Enter an academic topic", placeholder="Example: Machine Learning")
material=st.text_area("Or paste study material (optional)", height=180)

st.markdown("**Or upload a PDF or DOCX file (optional)**")
uploaded_file=st.file_uploader("Upload a course document", type=["pdf","docx"], label_visibility="collapsed")

def extract_text_from_upload(uploaded):
    """Extract plain text from an uploaded PDF or DOCX file.
    Returns (text, error_message). One of the two will be None."""
    name=uploaded.name.lower()
    try:
        if name.endswith(".pdf"):
            import fitz  # PyMuPDF
            data=uploaded.read()
            doc=fitz.open(stream=data, filetype="pdf")
            pages=[page.get_text() for page in doc]
            doc.close()
            text="\n".join(pages).strip()
            if not text:
                return None, "The PDF appears to contain no extractable text (it may be scanned/image-only)."
            return text, None
        elif name.endswith(".docx"):
            import docx as _docx  # python-docx
            import io
            document=_docx.Document(io.BytesIO(uploaded.read()))
            paragraphs=[p.text for p in document.paragraphs if p.text.strip()]
            text="\n".join(paragraphs).strip()
            if not text:
                return None, "The DOCX file appears to contain no readable text."
            return text, None
        else:
            return None, f"Unsupported file type: {uploaded.name}"
    except Exception as exc:
        return None, f"Could not extract text from '{uploaded.name}': {exc}"

if st.button("✨ Generate Learning Content", type="primary", use_container_width=True):
    # Determine source: uploaded file → pasted text → topic
    doc_text=None
    if uploaded_file is not None:
        doc_text, err=extract_text_from_upload(uploaded_file)
        if err:
            st.error(err)
            st.stop()

    source=doc_text or material.strip() or topic.strip()
    if not source:
        st.warning("Enter a topic, paste study material, or upload a PDF/DOCX file.")
    else:
        with st.spinner("IBM Granite is preparing your learning material..."):
            try:
                st.session_state["learn_output"]=generate_learning_content(source, level, output_type)
                st.session_state["learn_topic"]=topic or (uploaded_file.name if uploaded_file else "Provided study material")
            except Exception as e:
                st.error(f"Generation failed: {e}")
                st.info("Check your IBM API key, Project ID, service URL, and model access in .env.")

if "learn_output" in st.session_state:
    st.divider()
    st.subheader(f"📘 Learning material: {st.session_state.get('learn_topic','')}")
    st.markdown(st.session_state["learn_output"])
    st.download_button("⬇️ Download study material", st.session_state["learn_output"], "LearnEase_AI_Study_Material.txt", "text/plain", use_container_width=True)

st.divider()
st.caption("Responsible AI: Verify important facts with textbooks and faculty notes. AI-generated responses may contain errors.")
