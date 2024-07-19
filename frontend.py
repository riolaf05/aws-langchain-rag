import streamlit as st
import tempfile

f = st.file_uploader("Upload file")
tfile = tempfile.NamedTemporaryFile(delete=False)
tfile.write(f.read())

