## 1. Web tools

To streamline gene annotation after model training, we developed a post-processing pipeline that integrates an interactive web interface and an API-based system.

Our web-based annotation tool allows users to submit genome sequences for automatic annotation. It supports two input modes: 
1. **Direct input** – Users can paste a genome sequence into the provided text area.
2. **File upload** – Users can upload a FASTA file for processing.

After providing input, users can specify the desired output format (GFF or CSV). Once submitted, the system processes the annotation and generates structured output files.

### 1.1 Setting Up the Environment
#### Step 1: Create a Python Environment
```sh
git clone https://github.com/Bioinformatics-UM6P/GeneLM
cd webtool
python -m venv venv
```

#### Step 2: Activate the Environment
```sh
source ./venv/bin/activate
```

#### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```

### 1.2 Launch the Web Tool UI
```sh
streamlit run ui/app.py
```

### 1.3 Start the API Server
```sh
uvicorn --app-dir api api:app --host 127.0.0.1 --port 8000 --reload
```

### 1.4. Perform Annotation
Navigate to the web tool and submit a FASTA/FNA file containing your full genome sequence.