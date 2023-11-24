import streamlit as st
import ifcopenshell
import os
import re  # Import regex module

def list_files_in_directory(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def load_ifc_file(file_path):
    with open(file_path, 'r') as file:
        ifc_data = file.read()
    with open(file_path, 'rb') as file:
        session['array_buffer'] = file.read()
    return ifcopenshell.file.from_string(ifc_data)

def callback_upload(uploaded_file):
    session["file_name"] = uploaded_file.name
    session["array_buffer"] = uploaded_file.getvalue()
    session["ifc_file"] = ifcopenshell.file.from_string(session["array_buffer"].decode("utf-8"))
    session["is_file_loaded"] = True

def get_project_name():
    if "ifc_file" in session:
        return session.ifc_file.by_type("IfcProject")[0].Name
    return ""

def change_project_name():
    if "project_name_input" in session and session.project_name_input:
        session.ifc_file.by_type("IfcProject")[0].Name = session.project_name_input

def get_postfix(filename):
    """Extracts the numeric postfix from a filename."""
    match = re.search(r"_(\d+)\.ifc$", filename)
    return int(match.group(1)) if match else 0

def main():
    # Streamlit style and configuration
    streamlit_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');
            html, body, [class*="css"]  {
            font-family: DejaVu Sans Mono, monospace;
            }
            </style>
            """
    st.set_page_config(layout="wide", page_title="Insight-AWP IFC Viewer", page_icon="🟩")
    st.title("IFC Model Analysis")
    st.markdown(streamlit_style, unsafe_allow_html=True)

    # Load models from directory
    model_folder = 'models'
    model_files = list_files_in_directory(model_folder)

    # Sort model files based on numeric postfix
    model_files_sorted = sorted(model_files, key=get_postfix)

    # Automatically load the first model ending with _1.ifc
    if 'is_file_loaded' not in session:
        first_model = next((f for f in model_files if f.endswith('_1.ifc')), None)
        if first_model:
            file_path = os.path.join(model_folder, first_model)
            session['ifc_file'] = load_ifc_file(file_path)
            session['is_file_loaded'] = True
            session['selected_file'] = first_model

    # Create buttons for selecting a model file within a column layout
    col = st.sidebar.columns(1)  # Adjust the number of columns if needed
    for file_name in model_files_sorted:
        if col[0].button(file_name, key=file_name):  # All buttons are in the first column
            file_path = os.path.join(model_folder, file_name)
            session['ifc_file'] = load_ifc_file(file_path)
            session['is_file_loaded'] = True
            session['selected_file'] = file_name
            st.experimental_rerun()

    # Upload a new file
    uploaded_file = st.sidebar.file_uploader('Or upload a model', type=['ifc'], key="uploaded_file")
    if uploaded_file is not None:
        callback_upload(uploaded_file)
        st.experimental_rerun()

    # Display file information
    if "is_file_loaded" in session and session["is_file_loaded"]:
        st.sidebar.success(f'Model successfully loaded')
        
        col1, col2 = st.columns([2,1])
        col1.subheader(f'Loaded model "{get_project_name()}"')
        col2.text_input("Change Project Name ✏️", key="project_name_input")
        col2.button("Apply ✔️", key="change_project_name_button", on_click=change_project_name)

if __name__ == "__main__":
    session = st.session_state
    main()