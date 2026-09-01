"""
Serviço responsável por extrair texto de arquivos enviados pelo usuário.
Suporta: PDF (via pdfplumber) e texto puro.
"""
import io
import logging

logger = logging.getLogger(__name__)


def extrair_texto_pdf(arquivo_bytes: bytes) -> str:
    """
    Extrai o texto de um arquivo PDF a partir dos seus bytes brutos.

    Args:
        arquivo_bytes: Conteúdo binário do arquivo PDF.

    Returns:
        Texto extraído como string. Retorna string vazia se falhar.
    """
    try:
        import pdfplumber
    except ImportError:
        logger.error("pdfplumber não está instalado. Execute: pip install pdfplumber")
        raise ImportError("pdfplumber não instalado. Execute: pip install pdfplumber")

    texto_total = []

    with pdfplumber.open(io.BytesIO(arquivo_bytes)) as pdf:
        total_paginas = len(pdf.pages)
        logger.info(f"Extraindo texto de PDF com {total_paginas} página(s)...")

        for i, pagina in enumerate(pdf.pages):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_total.append(texto_pagina.strip())

    texto_final = "\n\n".join(texto_total)
    logger.info(f"Extração concluída. {len(texto_final)} caracteres extraídos.")
    return texto_final


def extrair_texto_arquivo(uploaded_file) -> str:
    """
    Extrai texto de um arquivo enviado pelo Streamlit (st.file_uploader).
    Detecta automaticamente o tipo do arquivo.

    Args:
        uploaded_file: Objeto de arquivo do Streamlit (UploadedFile)

    Returns:
        Texto extraído como string.

    Raises:
        ValueError: Se o tipo de arquivo não for suportado.
    """
    nome = uploaded_file.name.lower()
    conteudo = uploaded_file.read()

    if nome.endswith(".pdf"):
        return extrair_texto_pdf(conteudo)
    elif nome.endswith(".txt"):
        return conteudo.decode("utf-8", errors="replace")
    else:
        raise ValueError(
            f"Tipo de arquivo '{nome}' não suportado. "
            "Use arquivos .pdf ou .txt"
        )
