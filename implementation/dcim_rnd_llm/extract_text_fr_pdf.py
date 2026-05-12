from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("/home/infra/rnd_llm/pdf/compro_falah.pdf")
docs = loader.load()
