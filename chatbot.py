import anthropic,chromadb 
from chromadb.utils.embedding_functions 
import SentenceTransformerEmbeddingFunction
client = anthropic.Anthropic() 
chroma = chromadb.Client() 
ef = SentenceTransformerEmbeddingFunction('all-MiniLM-L6-v2') 
col = chroma.create_collection('docs', embedding_function=ef) 
# Index sample documents 
docs = [
     "Python was created by Guido van Rossum and first released in 1991.", 
     "The Transformer architecture was introduced by Google in 2017.", 
     "RAG combines retrieval with generation to reduce hallucinations.",
] 
col.add(documents=docs, ids=['d1','d2','d3'])

def rag_query(question: str) -> str: 
    results = col.query(query_texts=[question], n_results=2) 
    context = '\n'.join(results['documents'][0]) 
    prompt = f'Context:\n{context}\n\nQuestion: {question}' 
    resp = client.messages.create( 
        model="claude-sonnet-4-20250514", 
        max_tokens=256, 
        system="Answer only from the provided context.", 
        messages=[{"role": "user", "content": prompt}] 
    ) 
    return resp.content[0].text 

print(rag_query('When was the Transformer introduced?'))