# ---------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------
import streamlit as st
from PIL import Image
import os
import base64
import graphviz
import time
import tempfile
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------
# API UTILS 
# ---------------------------------------------------------------
API_BASE_URL = os.getenv("API_PROD_URL", "http://127.0.0.1:8000")
def submit_file_to_api(file_path, output_format):
    with open(file_path, "rb") as f:
        files = {"file": f}
        params = {"output_format": output_format.replace(' File', '')}
        response = requests.post(f"{API_BASE_URL}/tis/get-annotation", files=files, params=params)

    if response.status_code == 200:
        return response.json().get("uuid")
    return None

def check_progress(uuid):
    response = requests.get(f"{API_BASE_URL}/tis/get-progress/{uuid}")
    if response.status_code == 200:
        return response.json()
    return None

def get_result_file(uuid):
    response = requests.get(f"{API_BASE_URL}/tis/get-result/{uuid}")
    if response.status_code == 200:
        try:
            result_data = response.json()
            result_url = result_data.get("result_url")
            seq_id = result_data.get("seq_id")

            file_response = requests.get(result_url)
            if file_response.status_code == 200:
                file_extension = ".csv" if result_url.endswith(".csv") else ".gff"
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                temp_file.write(file_response.content)
                temp_file.close()
                return (temp_file.name, seq_id)
            else:
                return (None, None)
        except Exception as e:
            st.error(f"❌ Error processing result response: {str(e)}")
            return (None, None)
    st.error(f"❌ Failed to fetch result. Status code: {response.status_code}")
    return (None, None)

# ---------------------------------------------------------------
# FUNCTION 
# ---------------------------------------------------------------
st.set_page_config(
    page_title='TIS',
    page_icon='🧊',
    initial_sidebar_state='collapsed',
    # layout='wide',
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def load_custom_header():
    """Creates a fixed custom header with a full-width hero section below it."""
    header_html = f"""
    <style>
        /* Hide default Streamlit header */
        header {{
            visibility: hidden;
        }}

        /* Reset default margin/padding */
        body {{
            margin: 0;
            padding: 0;
        }}

        /* Custom Fixed Header */
        .custom-header {{
            background-color: rgb(44, 62, 80);
            height: 80px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 50px;
            color: white;
            font-size: 20px;
            font-weight: bold;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }}

        /* Navigation Menu */
        .custom-header nav {{
            display: flex;
            gap: 20px;
        }}

        .custom-header a {{
            color: white;
            text-decoration: none;
            font-size: 18px;
            padding: 5px 10px;
            transition: 0.3s;
        }}

        .custom-header a:hover {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
        }}

        /* Hero Section - Directly Below Header */
        .hero {{
            text-align: center;
            color: white;
            padding: 60px 20px;
            background: rgb(52, 152, 219);
            width: 100%;
            margin: 0;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            margin-top: 80px; /* Pushes hero below the fixed header */
        }}

        .hero h1 {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .hero p {{
            font-size: 1.2rem;
            margin-bottom: 20px;
        }}

        .hero .btn {{
            display: inline-block;
            padding: 7px 13px;
            font-size: 1.2rem;
            font-weight: bold;
            color: white;
            background: #e74c3c;
            border-radius: 5px;
            text-decoration: none;
            transition: background 0.3s ease-in-out;
            cursor: pointer;
        }}

        .hero .btn:hover {{
            background: #c0392b;
        }}

        /* Space below hero to prevent overlap with tabs */
        .content-wrapper {{
            padding-top: 30px;
        }}
        
        .st-emotion-cache-mtjnbi{{
            width: 100%;
            padding: 0 !important;
            max-width: 100% !important;
        }}
        
        .stTabs{{
            width: 90% !important;
            padding: 1rem 2.5rem 10rem;
            margin: 0 auto !important;
        }}

        .st-emotion-cache-89jlt8 {{
            font-size: 18px !important;
        }}

        .st-emotion-cache-1104ytp {{
            font-size: 1.1rem !important;
        }}

        .stButton{{
            text-align: center;
        }}

        .stTabs {{
            padding: 1rem 2.5rem 2.5rem !important;
        }}

        .result-box {{
            width: 100%;
            padding: 20px;
            text-align: center;
            border: 2px solid #efeff1;
            border-radius: 1px;
            background-color: #f8f8f9;
            font-size: 18px;
            font-weight: bold;
            color: gray;
            height: 25em;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .overlay {{
            top: 0;
            left: 0;
            width: 100%;
            height: 35em;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            z-index: 1000;
            text-align: center;
            flex-direction: column;
        }}
        
        .overlay div a {{
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            font-size: 18px;
            margin-top: 10px;
            display: block;
            text-decoration: none;
        }}
        .overlay div a:hover {{
            background-color: #45a049;
        }}
    </style>

    <div class="custom-header">
        <div>TIS Predictor</div>
        <nav>
            <!--<a href="#home">Home</a>
            <a href="#data">Data</a>
            <a href="#tools">Tools</a>
            <a href="#api">API</a>-->
        </nav>
    </div>
    <div class="hero">
        <h1>TIS  - AI powered Gene Annotation</h1>
        <p>Effortlessly analyze genomes using our AI-driven annotation tool.</p>
        <a href="?tab=tool" class="btn" target="_self">Try the Tool</a>
    </div>
    <div class="content-wrapper"></div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def set_ui_navigation():
    list_of_tabs = ["🏠 Home", "🔬 Try the Tool", "📖 API Docs", "⚠️ Disclaimer"]
    tabs = st.tabs(list_of_tabs)

    query_params = st.query_params
    if "tab" in query_params:
        tab_index = None
        if query_params["tab"] == "tool":
            tab_index = 1
        elif query_params["tab"] == "api":
            tab_index = 2
        
        if tab_index is not None:
            js_script = f"""
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    setTimeout(function() {{
                        var tabs = window.parent.document.querySelectorAll('[data-testid="stTab"]');
                        if (tabs.length > {tab_index}) {{
                            tabs[{tab_index}].click();
                        }}
                    }}, 10);
                }});
            </script>
            """
            st.components.v1.html(js_script, height=0)

    with tabs[0]:
        home()
    with tabs[1]:
        try_the_tool()
    with tabs[2]:
        api_documentation()
    with tabs[3]:
        disclaimer()

def create_flowchart():
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("#### Pipeline:")
    with col2:
        flowchart = graphviz.Digraph(format="png")
        flowchart.attr(rankdir="LR", bgcolor="white")

        steps = {
            "Start": "🔵 Start",
            "ORF": "🧬 ORFs Extraction",
            "Tokenization": "🔠 Tokenization (K-mer)",
            "CDS_Classification": "📜 CDS Classification",
            "TIS_Refinement": "🔍 TIS Refinement",
            "Postprocessing": "⚙️ Post-Processing",
            "Output": "🟢 Final Annotation"
        }

        # add nodes
        for key, label in steps.items():
            flowchart.node(key, label, shape="box", style="filled,solid", fillcolor="#f8f8f9", color="lightgray")

        # edges
        flowchart.edge("Start", "ORF")
        flowchart.edge("ORF", "Tokenization")
        flowchart.edge("Tokenization", "CDS_Classification")
        flowchart.edge("CDS_Classification", "TIS_Refinement")
        flowchart.edge("TIS_Refinement", "Postprocessing")
        flowchart.edge("Postprocessing", "Output")

        # display flowchart
        flowchart_placeholder = st.graphviz_chart(flowchart)

    return flowchart, flowchart_placeholder

def annotation_process(uploaded_file, output_format, flowchart, flowchart_placeholder):
    if isinstance(uploaded_file, str):  
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta", mode="w") as temp_file:
            temp_file.write(uploaded_file)
            temp_file_path = temp_file.name
    else:  
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

    uuid = submit_file_to_api(temp_file_path, output_format)
    os.remove(temp_file_path)

    if not uuid:
        st.error("Failed to submit the annotation request.")
        return
    st.success(f"Submitted for annotation (UUID: {uuid})")

    # Track progress
    step_colors = {
        "Start": "lightgreen",
        "ORF": "lightgray",
        "Tokenization": "lightgray",
        "CDS_Classification": "lightgray",
        "TIS_Refinement": "lightgray",
        "Postprocessing": "lightgray",
        "Output": "lightgray"
    }
    progress_steps = [
        ("Start", "Start"),
        ("ORF", "ORF Extracted"),
        ("Tokenization", "Tokenization Completed"),
        ("CDS_Classification", "CDS Classification Completed"),
        ("TIS_Refinement", "TIS Refinement Completed"),
        ("Postprocessing", "Post-Processing Completed"),
        ("Output", "✅ Final Annotation Ready!"),
    ]
    result_file = None
    while True:
        progress = check_progress(uuid)
        if not progress:
            st.warning("Unable to fetch progress. Retrying...")
            time.sleep(5)
            continue

        progress_value = progress.get("progress", 0)
        status = progress.get("status", "Unknown")
        message = progress.get("message", "Error")
        exec_state = progress.get("exec_state", {})
        st.session_state["status"] = status
        
        if status == "Canceled":
            st.error(f"The annotation task was canceled: {message}.")
            break

        if message != "" and message != None:
            st.info(f"`{message}`")

        # <<<old style>>>
        # progress_index = int((progress_value / 100) * len(progress_steps))  
        # for i in range(progress_index):
        #     step, label = progress_steps[i]
        #     step_colors[step] = "lightblue" if step != "Output" else "lightgreen"
        #     flowchart.node(step, label, shape="box", style="filled,solid", fillcolor=step_colors[step], color="gray")
        #     flowchart_placeholder.graphviz_chart(flowchart)
        # <<<new style>>>
        for step, label in progress_steps:
            completion = exec_state.get(step, 0) 
            if completion == 100:
                step_colors[step] = "lightblue" if step != "Output" else "lightgreen"
                label = f"{label} ✅" if step != "Output" else label
            elif completion > 0:
                step_colors[step] = "#eee590"
                label = f"{label} (Processing...)"
            else:
                step_colors[step] = "lightgray"

            flowchart.node(step, label, shape="box", style="filled,solid", fillcolor=step_colors[step], color="lightgray")

        # update the flowchart visualization
        flowchart_placeholder.graphviz_chart(flowchart)
        
        if status == "Completed":
            result_file, seq_id = get_result_file(uuid)
            break

        time.sleep(5)

    # display results
    st.session_state["annotation_result"] = result_file
    st.session_state["seq_id"] = seq_id
    st.session_state["annotation_output_format"] = output_format
    st.session_state["annotation_done"] = True

# ---------------------------------------------------------------
# PAGE 
# ---------------------------------------------------------------
def home():
    st.subheader("Translation Initiation Site Predictor in Bacteria")
    st.markdown("""
    **Project Overview:**
    This tool predicts translation initiation sites in bacterial genomes.

    **GitHub Repository:** [GitHub](https://github.com/your-repo)

    **Reference Paper:** [Link to paper]

    **How to Cite:**
    *Author(s), Year. Title. Journal/Conference. DOI/Link*
    """)

def try_the_tool():
    st.subheader("🔬 Gene Annotation Tool")
    st.info(
        "**Version:** 1.0.0  \n"
        "**Features:** CDS Extraction & TIS Refinement  \n"
        "⚠️ This tool predicts coding sequences (CDS) and refines Translation Initiation Sites (TIS) for bacterial genomes using two stages genomic language model pipeline."
    )
    
    annotation_completed = st.session_state.get("annotation_done", False)
    status_placeholder = st.empty()
    
    if not annotation_completed:
        ### ---- INPUT SECTION ---- ###
        st.markdown("#### Input:")
        dna_sequence = st.text_area(
            "Paste your genome sequence here :",
            placeholder=">CP011509.1 Archangium gephyra strain DSM 2261, complete genome\nGCGTCTCCACCGCCGGAATGCCATACGCCGCCAGCAGCCCGCTTGGACTCGTACTCCGTCAGCAGCGTGCGGCCCGCCTC...",
            height=200,
        )
        uploaded_files = st.file_uploader(
            "Choose FASTA file(s)",
            type=["fasta", "fna"],
            accept_multiple_files=False,
        )
        st.markdown(
            """
            **Need a sample input?**  
            [Download Sample FASTA File](./static/sequence_tiny.fasta)
            """,
            unsafe_allow_html=True,
        )

        if dna_sequence.strip():
            input_source = dna_sequence
        elif uploaded_files: 
            st.success(f"✅ File uploaded successfully.")
            input_source = uploaded_files
        else:
            input_source = None
            # st.error("❌ Please **paste a genome sequence** OR **upload a FASTA file** before proceeding.")

        ### ---- OUTPUT SETTINGS ---- ###
        st.markdown("#### Options:")
        col1, col2 = st.columns(2)
        with col1:
            output_format = st.radio(
                "Select Output Format",
                ["GFF File", "CSV File"],
                horizontal=True,
            )
        # with col2:
        #     post_processing_method = st.selectbox(
        #         "Post-Processing Method",
        #         ["Max Likelihood per ORFs (recommended)", "Probability Threshold"],
        #     )
        #     if post_processing_method == "Probability Threshold":
        #         st.warning("⚠️ This option is currently unavailable. Please use the recommended method.")
        # if post_processing_method == "Probability Threshold":
        #     threshold = st.slider(
        #         "Set Custom Probability Threshold",
        #         min_value=0.0,
        #         max_value=1.0,
        #         value=0.9,
        #         step=0.05,
        #     )
            
        ### ---- PROCESSING SECTION ---- ###
        st.divider()
        flowchart, flowchart_placeholder = create_flowchart()
        st.subheader("")
        
        if "processing" not in st.session_state:
            st.session_state["processing"] = False  
        is_processing = st.session_state["processing"]

            
        if st.button("Start Annotation", type="primary", disabled=is_processing):
            if not input_source:
                st.error("❌ No valid input provided. Please **paste a genome sequence** or **upload a FASTA file**.")
            else:
                st.session_state["processing"] = True
                st.rerun()
        
        if st.session_state["processing"]:
            with st.spinner(f"Processing... Please wait"):
                annotation_process(input_source, output_format, flowchart, flowchart_placeholder)
                st.session_state["processing"] = False
                st.session_state["annotation_done"] = True   
                st.rerun()         
    else:
        with status_placeholder:
            st.markdown("""
                <div class="overlay">
                    <p>Annotation completed! Download your output first, then click below to continue.</p>
                    <div>
                        <a href"/?tab=tool" target="_self">Annotate Again</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
    # Always resuls
    st.markdown("#### Results:")
    result_file = st.session_state.get("annotation_result", None)
    output_format = st.session_state.get("annotation_output_format", "GFF")
    if output_format == "CSV":
        seq_id = str(st.session_state.get("seq_id", "annotation_output")).replace(' ', '_') + "_Annotation.csv"
    else:
        seq_id = str(st.session_state.get("seq_id", "annotation_output")).replace(' ', '_') + "_Annotation.gff"
        
    if result_file:
        st.success("✅ Annotation complete! Download your results below.")
        if result_file.endswith(".csv"):
            df = pd.read_csv(result_file)
            st.dataframe(
                df, 
                use_container_width=True, 
                height=700, 
                column_order=("seq_id", "annotation", "start", "end", "strand", "orf_group", "logit_cls0", "logit_cls1", "prob_cls0", "prob_cls1", "prediction_max_likelihood")
            )
        else:
            with open(result_file, "r") as f:
                gff_content = f.read()
            st.code(gff_content, language="bash", height=500) 
        with open(result_file, "rb") as f:
            st.download_button(label="Download Result", data=f, file_name=seq_id, mime="text/csv" if output_format == "CSV" else "text/plain")
    else:
        st.markdown(
            """
            <div class="result-box">Nothing yet</div>
            """,
            unsafe_allow_html=True,
        )

def api_documentation():
    api_base_url = "http://localhost:8000"
    st.subheader("📖 API Documentation")
    st.info("""
    Welcome to the **Gene Annotation API**.  
    This API allows you to submit genome files for annotation, track progress, and retrieve results.
    
    ---

    ##### **🛠 Available API Routes** ([View Full API Documentation](http://localhost:8000/docs))
    """)

    # 01
    st.markdown("1. Submit Genome for Annotation")
    with st.expander("🔴 **Submit Genome for Annotation** (`POST /tis/get-annotation`)", expanded=True):
        st.markdown("""
        This endpoint allows you to submit a **FASTA file** for annotation.

        **Request Parameters:**
        - `file`: The genome file (`.fasta`, `.fna`).
        - `output_format`: Desired output format (`CSV`, `GFF`).

        **Response:**
        - Returns a **UUID** representing the submitted task.
        """)
        
        option = st.selectbox("Select Code Example", ["Python", "cURL"], key="annotation")
        if option == "Python":
            st.code("""
                import requests

                url = "http://localhost:8000/tis/get-annotation"
                files = {"file": open("genome.fasta", "rb")}
                params = {"output_format": "CSV"}
                response = requests.post(url, files=files, params=params)
                uuid = response.json().get("uuid")
                print(f"Task submitted! UUID: {uuid}")
                """, 
            language="python")
        elif option == "cURL":
            st.code("""
                curl -X POST "http://localhost:8000/tis/get-annotation" -F "file=@genome.fasta" -F "output_format=CSV"
                """, 
            language="bash")

    # 02
    st.markdown("2. Check Task Progress")
    with st.expander("🟢 **Check Task Progress** (`GET /tis/get-progress/{uuid}`)"):
        st.markdown("""
        This endpoint allows you to check the status of an annotation task.

        **Request Parameters:**
        - `uuid`: The **UUID** of the task.

        **Response:**
        - Returns a **JSON object** containing the task progress percentage.
        """)

        option = st.selectbox("Select Code Example", ["Python", "cURL"], key="progress")
        if option == "Python":
            st.code("""
                import requests

                uuid = "0effda03-ba36-4ca8-870d-3e6f63e852ce"
                url = f"http://localhost:8000/tis/get-progress/{uuid}"
                response = requests.get(url)
                progress = response.json()
                print(f"Task Progress: {progress}")
                """, 
            language="python")
        elif option == "cURL":
            st.code("""
                curl -X GET "http://localhost:8000/tis/get-progress/{uuid}"
                """, 
            language="bash")

    # 03
    st.markdown("3. Retrieve Annotation Results")
    with st.expander("🟢 **Retrieve Annotation Results** (`GET /tis/get-result/{uuid}`)"):
        st.markdown("""
        This endpoint allows you to download the final annotated genome file.

        **Request Parameters:**
        - `uuid`: The **UUID** of the completed task.

        **Response:**
        - Returns the **annotated file** in the requested format (`CSV` or `GFF`).
        """)

        option = st.selectbox("Select Code Example", ["Python", "cURL"], key="results")
        if option == "Python":
            st.code("""
                import requests

                uuid = "0effda03-ba36-4ca8-870d-3e6f63e852ce"
                url = f"http://localhost:8000/tis/get-result/{uuid}"
                result = requests.get(url)

                with open("annotated_output.csv", "wb") as f:
                    f.write(result.content)

                print("Annotation Complete! File saved.")
                """, 
            language="python")
        elif option == "cURL":
            st.code("""
                curl -X GET "http://localhost:8000/tis/get-result/{uuid}" -o annotated_output.csv
                """, 
            language="bash")

    # 04
    st.markdown("4. Cancel Annotation Task")
    with st.expander("🟠 **Cancel Annotation Task** (`DELETE /tis/cancel-task/{uuid}`)",):
        st.markdown("""
        This endpoint allows you to **cancel a previously submitted annotation task** using its **UUID**.

        **Request Parameters:**
        - `uuid` (path parameter): The **UUID** of the task you want to cancel.

        **Response:**
        - A **confirmation message** indicating whether the cancellation was successful.
        """)

        option = st.selectbox("Select Code Example", ["Python", "cURL"], key="cancel_task")
        if option == "Python":
            st.code("""
                import requests

                uuid = "0effda03-ba36-4ca8-870d-3e6f63e852ce"
                url = f"http://localhost:8000/tis/cancel-task/{uuid}"
                response = requests.delete(url)

                if response.status_code == 200:
                    print("Task successfully canceled!")
                else:
                    print(f"Failed to cancel task: {response.json()}")
                """, 
            language="python")

        elif option == "cURL":
            st.code("""
                uuid="0effda03-ba36-4ca8-870d-3e6f63e852ce"  # Replace with actual UUID
                curl -X DELETE "http://localhost:8000/tis/cancel-task/$uuid"
                """, 
            language="bash")
        
    # 05
    st.markdown("")
    st.markdown("5. Running Inference Locally")
    with st.expander("🔌 **Running Inference Locally**"):
        st.markdown("""
            You can run the **CDS and TIS classification models** locally using **Hugging Face transformers**.

            ---
            
            ### **Required Installations**
            Install the necessary dependencies using:
            ```bash
            pip install torch transformers
            ```

            ---

            ### **Download and Load the CDS Classifier**
            ```python
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            # Load CDS classifier
            model_name = "Genereux-akotenou/BacteriaCDS-DNABERT-K6-89M"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Example inference
            sequence = "ATGCGTACGTAGCTAGCTG..."
            inputs = tokenizer(sequence, return_tensors="pt")
            outputs = model(**inputs)
            print(outputs)
            ```

            ---

            ### **Download and Load the TIS Classifier**
            ```python
            # Load TIS classifier
            model_name = "Genereux-akotenou/BacteriaTIS-DNABERT-K6-89M"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            ```

            ---

            ### **Steps to Run Locally**
            1. **Load the appropriate model**:
                - Use `BacteriaCDS-DNABERT-K6-89M` for CDS classification.
                - Use `BacteriaTIS-DNABERT-K6-89M` for TIS classification.
            2. **Prepare the genome sequence** in 6-mer format (if needed).
            3. **Run inference** on your sequence.
            4. **Interpret outputs** (classification labels and confidence scores).

            **Now you can run bacterial gene annotation locally!**
        """)


def disclaimer():
    st.subheader("Disclaimer & Contact")
    st.markdown("""
    **Disclaimer:**
    This tool is based on machine learning predictions and should be verified manually.
    
    **Contact:**
    - Email: your_email@example.com
    - Support: [GitHub Issues](https://github.com/your-repo/issues)
    """)

    
# ---------------------------------------------------------------
# main 
# ---------------------------------------------------------------
def main():
    load_custom_header()
    set_ui_navigation()
    
# ---------------------------------------------------------------
# main 
# ---------------------------------------------------------------
if __name__ == "__main__":
    main()