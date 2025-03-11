**Understanding and Implementing Permuterm Index Search using Streamlit**

## Introduction
In modern information retrieval systems, searching for words with wildcard characters (such as "data*" or "*logy") is a common requirement. Traditional search techniques struggle with efficient wildcard searches, but the **Permuterm Index** provides a powerful way to handle such queries efficiently. This document explains the implementation of a **Permuterm Index Search** system using Python, **Streamlit** for UI, and **PyMuPDF** & **python-docx** for document processing.

This system allows users to upload documents (TXT, PDF, or DOCX), extract text, preprocess it, and build a permuterm index. Users can then perform wildcard searches using an optimized trie-based data structure.

---

## Theory: Understanding the Permuterm Index

### 1. What is a Permuterm Index?
A **Permuterm Index** is a search structure that enables efficient wildcard searches by rotating words and storing them in a trie. This allows quick lookup for queries with prefixes, suffixes, and infixes containing '*'.

### 2. Rotated Terms
Each word is augmented with a special symbol (`$`) and rotated multiple times to store all possible wildcard variations. For example:

```
word: "apple"
rotated terms: "apple$", "pple$a", "ple$ap", "le$app", "e$appl", "$apple"
```

### 3. Search Queries
Wildcard queries can be mapped to prefix searches in a trie:
- `app*` → Search for `$app` in the trie.
- `*ple` → Search for `ple$` in the trie.
- `*ppl*` → Check all words containing `ppl`.

### 4. Complexity
- **Insertion**: `O(m^2)`, where `m` is the word length.
- **Search**: `O(m)`, optimized using a trie.

---

## Methodology: How the System Works

1. **File Upload**: Users upload documents in TXT, PDF, or DOCX format.
2. **Text Extraction**: The content is extracted using `PyMuPDF` (for PDFs) and `python-docx` (for DOCX files).
3. **Preprocessing**:
   - Convert text to lowercase.
   - Tokenize words.
   - Remove stopwords.
4. **Permuterm Index Construction**:
   - Insert words into a trie after generating rotated terms.
   - Store document ID and position for each occurrence.
5. **Search Query Processing**:
   - Convert wildcard queries into prefix searches in the trie.
   - Retrieve matching words and their document positions.

---

## Code Explanation

### 1. **Imports & Stopwords**
```python
import re
import streamlit as st
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX
from collections import defaultdict
import pandas as pd
```
**Explanation:**
- `re`: Regular expressions for text processing.
- `streamlit`: GUI for web-based interaction.
- `fitz`: Extract text from PDFs.
- `docx`: Extract text from DOCX files.
- `defaultdict`: Efficient handling of dictionary data.
- `pandas`: Display structured data in a table.

```python
STOPWORDS = set(["a", "the", "is", "in", "of", "for", "on", "with", "at", "by", "this", "that", "it", "to" ... ])
```
**Explanation:**
- Defines common stopwords to remove unimportant words from documents.

### 2. **Trie Data Structure for Efficient Lookup**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.words = set()
```
**Explanation:**
- Each node in the trie stores:
  - `children`: Dictionary mapping characters to child nodes.
  - `is_end`: Marks end of a word.
  - `words`: Stores original words corresponding to rotated terms.

### 3. **Permuterm Index Class**
```python
class PermutermIndex:
    def __init__(self):
        self.trie = TrieNode()
        self.word_map = {}
        self.posting_list = defaultdict(set)
```
**Explanation:**
- `trie`: Root node of the trie.
- `word_map`: Tracks words inserted.
- `posting_list`: Stores document positions for each word.

```python
def insert(self, word, doc_id, position):
    self.word_map[word] = True
    self.posting_list[word].add((doc_id, position + 1))
    rotated_word = word + "$"
    for i in range(len(rotated_word)):
        rotated = rotated_word[i:] + rotated_word[:i]
        self._insert_into_trie(rotated, word)
```
**Explanation:**
- Appends `$` to mark word boundaries.
- Rotates the word and inserts variations into the trie.

```python
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
```
**Explanation:**
- Converts wildcard queries into valid prefix searches.
- Handles different types of wildcard patterns (`*word`, `word*`, `*word*`).

### 4. **Text Processing & File Handling**
```python
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return " ".join([page.get_text("text") for page in doc])
```
**Explanation:**
- Extracts text from PDFs using PyMuPDF.

```python
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return " ".join([para.text for para in doc.paragraphs])
```
**Explanation:**
- Reads text from DOCX files.

### 5. **Streamlit UI Integration**
```python
st.title("Permuterm Index Search")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "pdf", "docx"], accept_multiple_files=True)
```
**Explanation:**
- Creates a Streamlit interface for file uploads.

```python
query = st.text_input("Enter a search query (with * for wildcard):")
if st.button("Search"):
    results = permuterm.search(query)
    if results:
        st.write("### Search Results")
        for word, positions in results:
            st.write(f"**{word}:** {positions}")
    else:
        st.write("No matching terms found.")
```
**Explanation:**
- Takes user input and searches for wildcard queries in the permuterm index.

---

## Conclusion
This project demonstrates an efficient way to handle wildcard searches using a **Permuterm Index** with **Trie** data structures. The implementation allows users to upload documents, build an index, and search for words effectively. This approach optimizes search performance compared to traditional methods.

Future enhancements may include:
- **Fuzzy Search** for handling typos.
- **Phrase Queries** for multi-word searches.
- **Big Data Integration** for large-scale text processing.

