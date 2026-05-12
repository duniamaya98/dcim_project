from langchain_huggingface import HuggingFaceEmbeddings

# pilih model embedding (ringan & bagus)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

texts = [
    "Company profile bringing you advanced technology",
    "This document describes our infrastructure"
]

vectors = embeddings.embed_documents(texts)

print("Total vectors:", len(vectors))
print("Vector dimension:", len(vectors[0]))
