import pandas as pd
import docx2txt
import fitz  # PyMuPDF
import io
import csv

def extract_feedbacks_from_file(file) -> list:
    contents = []

    if file.filename.endswith(".txt"):
        text = file.file.read().decode("utf-8")
        contents = text.strip().split("\n")

    elif file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
        contents = df.iloc[:, 0].dropna().tolist()

    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
        contents = df.iloc[:, 0].dropna().tolist()

    elif file.filename.endswith(".docx"):
        text = docx2txt.process(file.file)
        contents = text.strip().split("\n")

    elif file.filename.endswith(".pdf"):
        contents = []
        pdf = fitz.open(stream=file.file.read(), filetype="pdf")
        for page in pdf:
            contents += page.get_text().strip().split("\n")

    return [c.strip() for c in contents if c.strip()]


def save_results_to_excel(results: list, filepath: str):
    df = pd.DataFrame(results)
    df.to_excel(filepath, index=False)
