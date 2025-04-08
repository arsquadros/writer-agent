import streamlit as st
from dotenv import load_dotenv
import openai
import base64
from uuid import uuid4
import os

from src.utils import utils
from src.personas import personas as module_personas

from langchain_community.document_loaders import PyPDFium2Loader

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Escreva conteúdo autêntico com pouco.")

tones = ["Neutro", "Explicativo", "Instrutivo", "Analítico", "Inspirador", "Empático", "Conversacional", "Crítico", "Provocativo", "Persuasivo", "Técnico"]
personas = ["Mônica Hauck", "Alessandro Vieira", "Persona Neutra"]
targets = ["Empreendedores iniciantes", "Empreendedores experientes", "Profissionais de RH", "Investidores", "Estudantes", "Outros"]

option = st.radio(
    "O que você gostaria de gerar?",
    ("Post de LinkedIn", "Seção de Livro"),
    index=0
)

# Seção obrigatória

with st.expander("Informações Essenciais (Obrigatório)"):
    if option == "Seção de Livro":
        theme = st.text_input("Sobre o que é o livro?", placeholder="Exemplo: Empreendedorismo no Brasil")
        title = st.text_input("Qual deve ser o título da seção?", placeholder="Exemplo: Dificuldades históricas e atuais do empreendedorismo no Brasil")
        objective = st.text_area("O que precisa ser passado na seção?", placeholder="Exemplo: Contextualizar os principais obstáculos enfrentados por empreendedores no Brasil ao longo do tempo, destacando fatores históricos, culturais, burocráticos e econômicos.", height=100)
    elif option == "Post de LinkedIn":
        theme = st.text_input("Sobre o que é o post?", placeholder="Exemplo: empreendedorismo no Brasil")
        title = st.text_input("Qual deve ser o título do post?", placeholder="Exemplo: Por que empreender no Brasil é um ato de coragem?")
        objective = st.text_area("O que precisa ser passado no post?", placeholder="Exemplo: Provocar reflexão sobre os desafios enfrentados por empreendedores no Brasil, destacando fatores culturais, burocráticos e estruturais.", height=100)

# Seção opcional recomendada

with st.expander("Detalhes do Conteúdo (Opcional)"):
    keywords = st.text_input("Quais palavras-chave podem guiar a escrita do tema?", placeholder="Exemplo: Empreendedorismo, Brasil, Obstáculos, Burocracia, História")
    target = st.multiselect(
        "Para quem você está escrevendo?",
        options=targets,
        default=[]
    )
    style = st.selectbox(
        "Qual a persona que está escrevendo?",
        options=personas,
        index=0
    )
    tone = st.radio(
        "Qual tom deve ser abordado na escrita?",
        options=tones,
        index=6 if option == "Post de LinkedIn" else 1  # "conversacional" para LinkedIn, "explicativo" para Livro
    )
    if option == "Seção de Livro":
        length = st.slider("Quantas palavras aproximadamente o conteúdo deve possuir?", 500, 10000, step=250, value=2000)
    elif option == "Post de LinkedIn":
        length = st.slider("Quantas palavras aproximadamente o conteúdo deve possuir?", 25, 500, step=25, value=100)

# Seção opcional extra

with st.expander("Informações Adicionais (Opcional)"):
    text_area = st.text_area("Alguma ideia ou anotação adicional?", placeholder="Inclua qualquer coisa que possa ajudar na escrita mas não foi coberto.")

    # Upload de documentos/imagens
    appended_documents = st.file_uploader(
        "Deseja anexar arquivos complementares? (PDF ou imagem)",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True
    )

submit_button = st.button("Gerar conteúdo")

if submit_button and title and objective and theme:
    # Processar documentos
    doc_content = ""
    images = []
    for appended_document in appended_documents:
        if appended_document:
            if appended_document.name.split(".")[-1] == "pdf":
                copy = f"{uuid4()}.pdf"
                with open(copy, "wb") as f:
                    f.write(appended_document.read())
                doc_content += "\n".join([page.page_content for page in PyPDFium2Loader(copy).lazy_load()])
                os.remove(copy)
            else:
                images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(appended_document.read()).decode('utf-8')}",
                    },
                })

    system_prompt = open(os.getenv("BOOK_SYSTEM_PROMPT_PATH", ""), "r").read() if option == "Seção de Livro" else open(os.getenv("LINKEDIN_SYSTEM_PROMPT_PATH", ""), "r").read()
    user_prompt = open(os.getenv("BOOK_USER_PROMPT_TEMPLATE_PATH", ""), "r").read() if option == "Seção de Livro" else open(os.getenv("LINKEDIN_USER_PROMPT_TEMPLATE_PATH", ""), "r").read()

    user_prompt = user_prompt.format(
        theme=theme if theme else "Não especificado",
        title=title if title else "Não especificado",
        objective=objective if objective else "Não especificado",
        keywords=keywords if keywords else "Não especificado",
        length=length if length else "Não especificado",
        tone=tone if tone else "Não especificado",
        target=target if target else "Não especificado",
        style=module_personas.persona_instances[style] if style else "Não especificado",
        text_area=text_area if text_area else "Não especificado",
        doc_content=doc_content if doc_content else "Não especificado"
    )

    messages = [{
        "role": "system",
        "content": [{"type": "text", "text": system_prompt}]
    }, {
        "role": "user",
        "content": [{"type": "text", "text": user_prompt}] + images
    }]

    result = utils.get_text_response("OPENAI_API_KEY", messages)

    st.subheader("Conteúdo gerado:")
    st.write(result)
