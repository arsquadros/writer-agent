import streamlit as st

from dotenv import load_dotenv

import openai

import base64
from uuid import uuid4
import os

from langchain_community.document_loaders import PyPDFium2Loader

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Agente \"Ghostwriter\"")

st.write("Segue exemplos de posts de LinkedIn da Mônica Hauck.")

with open("Monica/tests.pdf", "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

    st.download_button(label="Baixar Exemplos",
                    data=pdf_bytes,
                    file_name="exemplos.pdf",
                    mime='application/pdf')
    
text_area = st.text_area("Coloque as informações aqui", placeholder="Não sabe por onde começar? Siga os exemplos no documento acima.")
appended_documents = st.file_uploader("Possui imagens ou PDFs em anexo para ajudar o modelo a gerar o texto? Evite envio de documentos muito grandes. Você pode passar múltiplos arquivos", type=["jgp", "jpeg", "png", "pdf"], accept_multiple_files=True)
submit_button = st.button("Enviar e gerar o post")

if submit_button and text_area != "":
    doc_content = "''"
    images = []
    for appended_document in appended_documents:
        if appended_document:
            if appended_document.name.split(".")[-1] == "pdf":
                copy = f"{uuid4()}.pdf"

                with open(copy, "wb") as f:
                    f.write(appended_document.read())

                doc_content = "\n".join([page.page_content for page in PyPDFium2Loader(copy).lazy_load()])
                
                os.remove(copy)
            else:
                images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(appended_document.read()).decode('utf-8')}",
                    },
                })


    result = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": open("Monica/prompt.yaml", "r").read()
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{text_area}\nSource Document: '{doc_content}'."
                    },
                ] + images
            },
        ],
        temperature=0.5,
        n=1
    )

    st.write(result.choices[0].message.content)