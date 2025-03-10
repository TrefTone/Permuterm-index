import re
import streamlit as st
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX
from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.words = set()

class PermutermIndex:
    def __init__(self):
        self.trie = TrieNode()
        self.word_map = {}
        self.posting_list = defaultdict(set)

    def insert(self, word, doc_id, position):
        self.word_map[word] = True
        self.posting_list[word].add((doc_id, position + 1))  # Start index from 1
        rotated_word = word + "$"
        
        for i in range(len(rotated_word)):
            rotated = rotated_word[i:] + rotated_word[:i]
            self._insert_into_trie(rotated, word)
    
    def _insert_into_trie(self, rotated, word):
        node = self.trie
        for char in rotated:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.words.add(word)
        node.is_end = True
    
    def search(self, query):
        if "*" not in query:
            return [query] if query in self.word_map else []
        
        if query.count("*") == 1:
            if query.startswith("*"):
                query = query[1:] + "$"
            elif "*" in query:
                prefix, suffix = query.split("*")
                query = suffix + "$" + prefix
            return self._search_in_trie(query)
        
        if query.count("*") == 2:
            prefix, middle, suffix = query.split("*")
            query = suffix + "$" + prefix
            potential_words = self._search_in_trie(query)
            return [word for word in potential_words if middle in word]
        
        return []
    
    def _search_in_trie(self, prefix):
        node = self.trie
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return list(node.words)

# Document Processing
def process_document(text):
    words = re.findall(r"\b\w+\b", text.lower())
    return words

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return " ".join([page.get_text("text") for page in doc])

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return " ".join([para.text for para in doc.paragraphs])

# Streamlit App
st.title("Permuterm Index Search")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "pdf", "docx"], accept_multiple_files=True)

documents = {}
permuterm = PermutermIndex()

doc_id = 0
for uploaded_file in uploaded_files:
    doc_id += 1
    file_type = uploaded_file.type
    file_name = uploaded_file.name
    
    if file_type == "text/plain":
        document_text = uploaded_file.read().decode("utf-8")
    elif file_type == "application/pdf":
        document_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document_text = extract_text_from_docx(uploaded_file)
    else:
        continue
    
    documents[doc_id] = (file_name, document_text)
    tokens = process_document(document_text)
    for idx, word in enumerate(tokens):
        permuterm.insert(word, doc_id, idx)

if documents:
    st.write("### Uploaded Documents")
    for doc_id, (file_name, _) in documents.items():
        st.write(f"**Document {doc_id}:** {file_name}")

query = st.text_input("Enter a search query (with * for wildcard):")
if st.button("Search"):
    results = permuterm.search(query)
    st.write("Matching words:", results)

if st.button("Show Posting List"):
    st.write("### Posting List (Sorted by Term)")
    sorted_posting_list = sorted(permuterm.posting_list.items(), key=lambda x: x[0])
    for word, positions in sorted_posting_list:
        term_frequency = len(positions)
        postings = defaultdict(list)
        for doc_id, pos in sorted(positions):
            postings[doc_id].append(str(pos))
        postings_str = "\n".join([f"doc{doc_id}:{','.join(pos_list)};" for doc_id, pos_list in postings.items()])
        st.write(f"<{word}: {term_frequency};\n\n {postings_str}>")