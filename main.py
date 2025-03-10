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

    def insert(self, word, position):
        self.word_map[word] = True
        self.posting_list[word].add(position + 1)  # Start index from 1
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
    
    def display_trie(self, node=None, level=0, max_depth=4, prefix=""):
        if node is None:
            node = self.trie
        if level > max_depth:
            return ""
        
        tree_str = ""
        for char, child in node.children.items():
            tree_str += "  " * level + f"|-- {char}\n"
            tree_str += self.display_trie(child, level + 1, max_depth, prefix + char)
        return tree_str

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

uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf", "docx"])

document_text = ""
if uploaded_file is not None:
    file_type = uploaded_file.type
    
    if file_type == "text/plain":
        document_text = uploaded_file.read().decode("utf-8")
    elif file_type == "application/pdf":
        document_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document_text = extract_text_from_docx(uploaded_file)
    
    st.text_area("Document Content", document_text, height=200)
    
    tokens = process_document(document_text)
    permuterm = PermutermIndex()
    for idx, word in enumerate(tokens):
        permuterm.insert(word, idx)
    
    query = st.text_input("Enter a search query (with * for wildcard):")
    if st.button("Search"):
        results = permuterm.search(query)
        st.write("Matching words:", results)
    
    if st.button("Show Posting List"):
        st.write("Posting List:", dict(permuterm.posting_list))
    
    if st.button("Show Trie (Depth 4)"):
        trie_representation = permuterm.display_trie()
        st.text(trie_representation)
