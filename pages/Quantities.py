import streamlit as st
from tools import ifchelper
from tools import pandashelper
from tools import graph_maker

session = st.session_state

def initialize_session_state():
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

def load_data():
    if "ifc_file" in session:
        session["DataFrame"] = get_ifc_pandas()
        session.Classes = session.DataFrame["Class"].value_counts().keys().tolist()
        session["IsDataFrameLoaded"] = True

def download_csv():
    pandashelper.download_csv(session.file_name,session.DataFrame)

def download_excel():
    pandashelper.download_excel(session.file_name,session.DataFrame)

def get_ifc_pandas():
    data, pset_attributes = ifchelper.get_objects_data_by_class(
        session.ifc_file, 
        "IfcBuildingElement"
    )
    frame = ifchelper.create_pandas_dataframe(data, pset_attributes)
    return frame

def execute():
    st.title("Model Quantites")
    if not "IsDataFrameLoaded" in session:
        initialize_session_state()
    if not session.IsDataFrameLoaded:
        load_data()
    tab1, tab2 = st.tabs(["Dataframe utilities","Quantities Review"])

    with tab1:
        st.header("DataFrame Rev")
        session['DataFrame'] = get_ifc_pandas()
        st.write(session['DataFrame'])
        st.button("Download CSV", key="download_csv", on_click=download_csv)
        st.button("Download Excel", key="download_excel", on_click=download_excel)
    with tab2:
        row2col1, row2col2 = st.columns(2)
        with row2col1:
            st.write("Options")
            if session.IsDataFrameLoaded:
                classes = session.DataFrame["Class"].value_counts().keys().to_list()
                class_selector = st.selectbox("Select Class", options=classes, key="class_selector")
                session["filtered_frame"] = pandashelper.filter_dataframe_per_class(session.DataFrame, session.class_selector)
                session["qtos"] = pandashelper.get_qsets_columns(session["filtered_frame"])
                if session["qtos"] is not None:
                    qto_selector = st.selectbox("Select Quantity Set", session.qtos, key='qto_selector')
                    quantities = pandashelper.get_quantities(session.filtered_frame, session.qto_selector)
                    # Check if 'quantity_selector' exists in the session state
                    if 'quantity_selector' not in session:
                        session['quantity_selector'] = quantities[0] if quantities else None
                    st.selectbox("Select Quantity", quantities, key="quantity_selector")
                    st.radio('Split per', ['Level', 'Type'], key="split_options")
                else:
                    st.warning("No Quantities to Look at !")

            # DRAW FRAME
            with row2col2:
                st.write("Graph")
                # Check if 'quantity_selector' is initialized before using it
                if 'quantity_selector' in session and session.quantity_selector:
                    st.subheader(f"{session.class_selector} {session.quantity_selector}")
                    graph = graph_maker.load_graph(
                        session.filtered_frame,
                        session.qto_selector,
                        session.quantity_selector,
                        session.split_options,                                
                    )
                    st.plotly_chart(graph)
                else:
                    st.warning("Select a quantity to display the graph.")

execute()
