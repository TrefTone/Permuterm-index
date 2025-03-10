import re
import streamlit as st
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX
from collections import defaultdict
import pandas as pd

# Top 30 stopwords (can be customized)
STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
    'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
])

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
        self.posting_list[word].add((doc_id, position + 1))
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
        if '*' not in query:
            return [(query, self.posting_list[query])] if query in self.word_map else []

        if query.startswith('*') and query.endswith('*') and query.count('*') == 2:
            middle = query.strip('*')
            return [(word, self.posting_list[word]) for word in self.word_map if middle in word]

        if query.startswith('*'):
            query = query[1:] + '$'
        elif query.endswith('*'):
            query = '$' + query[:-1]
        elif '*' in query:
            prefix, suffix = query.split('*')
            query = suffix + '$' + prefix

        return [(word, self.posting_list[word]) for word in self._search_in_trie(query)]

    def _search_in_trie(self, prefix):
        node = self.trie
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return list(node.words)

    def get_permuterm_data(self):
        data = []
        for word in self.word_map:
            rotated_word = word + "$"
            for i in range(len(rotated_word)):
                rotated = rotated_word[i:] + rotated_word[:i]
                data.append((rotated, word))
        return data

# Document Processing
def process_document(text):
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    normalized_words = [word for word in words if word not in STOPWORDS]
    return normalized_words

# File Extraction
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return " ".join([page.get_text("text") for page in doc])

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return " ".join([para.text for para in doc.paragraphs])

# Streamlit App
st.title("Permuterm Index Search")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "pdf", "docx"], accept_multiple_files=True)

permuterm = PermutermIndex()

doc_id = 0
for uploaded_file in uploaded_files:
    doc_id += 1
    file_type = uploaded_file.type
    if file_type == "text/plain":
        document_text = uploaded_file.read().decode("utf-8")
    elif file_type == "application/pdf":
        document_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document_text = extract_text_from_docx(uploaded_file)
    else:
        continue

    tokens = process_document(document_text)
    for idx, word in enumerate(tokens):
        permuterm.insert(word, doc_id, idx)

query = st.text_input("Enter a search query (with * for wildcard):")
if st.button("Search"):
    results = permuterm.search(query)
    if results:
        st.write("### Search Results")
        for word, positions in results:
            postings = defaultdict(list)
            for doc_id, pos in sorted(positions):
                postings[doc_id].append(str(pos))
            posting_str = '; '.join([f'doc{doc_id}:{", ".join(pos_list)}' for doc_id, pos_list in postings.items()])
            st.write(f"**{word}:** {posting_str}")
    else:
        st.write("No matching terms found.")

if st.button("Show Permuterm Index"):
    st.write("### Permuterm Index (Rotated Words)")
    data = permuterm.get_permuterm_data()
    df = pd.DataFrame(data, columns=["Rotated Term", "Original Term"])
    st.dataframe(df)
