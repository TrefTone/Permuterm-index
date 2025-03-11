# **Permuterm Index Search: Code Explanation and Theory**

## **Introduction**

The given code implements a **Permuterm Index Search** system using a **Trie data structure**. It allows efficient wildcard searches on indexed words from text documents (TXT, PDF, and DOCX). The key feature of this system is the use of **rotated permutations of words** to facilitate fast pattern matching.

This document thoroughly explains the theory behind the **Permuterm Index**, discusses the **data structures used**, explains key **variables**, and provides a **step-by-step breakdown** of the code.

---

## **Theory**

### **Permuterm Indexing**
The **Permuterm Index** is a type of indexing that supports wildcard searches efficiently. It works by **storing rotated versions of words** along with their original forms, making it possible to perform searches with leading or trailing wildcards.

#### **Wildcard Search**
A standard word "hello" can have wildcard searches like:
- `hel*` → Matches "hello", "helmet", etc.
- `*lo` → Matches "hello", "solo", etc.
- `h*l*` → Matches "hollow", "helical", etc.

To enable such searches, we rotate words by appending a special character (e.g., `$`) at the end:

| Word  | Rotations Stored in Index |
|--------|--------------------------|
| hello  | `hello$`, `ello$h`, `llo$he`, `lo$hel`, `o$hell`, `$hello` |

By doing this, **any wildcard query can be mapped to a prefix search in the Trie data structure**.

### **Data Structures Used**

#### **1. Trie (Prefix Tree)**
A **Trie** is a tree-like data structure used for storing strings efficiently. It is particularly useful in prefix-based search operations. Each node represents a character, and words are formed by traversing from the root to a leaf node.

##### **Why Trie?**
- **Fast Search:** Supports prefix searching in **O(m)** time (where `m` is the length of the query string).
- **Efficient Storage:** Stores multiple words compactly with shared prefixes.
- **Wildcard Matching:** Helps in retrieving words quickly based on a given prefix.

#### **2. Dictionary (Hash Map)**
Dictionaries (hash maps) are used to store **posting lists**, which map words to the documents and positions where they occur. This allows for fast retrieval during search queries.

#### **3. Default Dictionary**
The **defaultdict** from Python’s collections module is used to store word positions efficiently. It automatically creates an empty list when a new key is accessed.

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
## **Code Breakdown**

### **Imports and Global Variables**
```python
import re
import streamlit as st
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX
from collections import defaultdict
import pandas as pd
```
#### **Explanation:**
- `re`: Regular expressions for text processing.
- `streamlit`: Used for building a web-based UI for the application.
- `fitz`: Library for extracting text from PDFs.
- `docx`: Library for extracting text from DOCX files.
- `defaultdict`: Efficient storage of word-posting lists.
- `pandas`: Used to display tabular data.

---

### **Class: TrieNode**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.words = set()
```
#### **Explanation:**
- **`self.children`** → Stores child nodes (characters of the word).
- **`self.is_end`** → Marks if a word ends at this node.
- **`self.words`** → Stores words that pass through this node.

---

### **Class: PermutermIndex**
```python
class PermutermIndex:
    def __init__(self):
        self.trie = TrieNode()
        self.word_map = {}
        self.posting_list = defaultdict(set)
```
#### **Explanation:**
- **`self.trie`** → The root node of the Trie.
- **`self.word_map`** → A dictionary to check if a word exists.
- **`self.posting_list`** → Stores document positions for each word.

```python
    def insert(self, word, doc_id, position):
        self.word_map[word] = True
        self.posting_list[word].add((doc_id, position + 1))
        rotated_word = word + "$"
        for i in range(len(rotated_word)):
            rotated = rotated_word[i:] + rotated_word[:i]
            self._insert_into_trie(rotated, word)
```
#### **Insertion Process:**
1. Store word in `word_map`.
2. Update `posting_list` with document ID and word position.
3. Rotate the word and insert all rotated forms into the Trie.

```python
    def _insert_into_trie(self, rotated, word):
        node = self.trie
        for char in rotated:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.words.add(word)
        node.is_end = True
```
#### **Trie Insertion Process:**
1. Traverse through the Trie, inserting characters.
2. Store the original word in each node.

---

### **Wildcard Search**
```python
    def search(self, query):
        if '*' not in query:
            return [(query, self.posting_list[query])] if query in self.word_map else []
```
#### **Search Flow:**
1. If no wildcard (`*`), directly check in `word_map`.
2. If `*` exists, modify the query into rotated format:
   - `*word` → `word$`
   - `word*` → `$word`
   - `w*d` → `d$w`
3. Perform a Trie lookup.

---

### **Document Processing**
```python
def process_document(text):
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    normalized_words = [word for word in words if word not in STOPWORDS]
    return normalized_words
```
#### **Steps:**
1. Extract words using regex.
2. Convert to lowercase.
3. Remove stopwords.

---

### **Final Streamlit App**
```python
st.title("Permuterm Index Search")

uploaded_files = st.file_uploader("Upload documents", type=["txt", "pdf", "docx"], accept_multiple_files=True)

permuterm = PermutermIndex()
```
#### **UI Components:**
- Upload files
- Process text into the Permuterm Index
- Perform searches based on user input

---

## **Conclusion**
This project implements a **Trie-based Permuterm Index** for efficient wildcard search. The combination of Tries and hash maps enables **fast indexing and retrieval**, making it suitable for large-scale document searches.

Future enhancements could include:
- **Phrase searches** (multi-word queries)
- **Better ranking of results**
- **Optimized storage using compressed Tries**

