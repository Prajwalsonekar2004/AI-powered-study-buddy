import streamlit as st
import pandas as pd
import nltk
import re
from collections import Counter
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import random

nltk.download('punkt')
nltk.download('stopwords')

st.set_page_config(page_title="AI-Powered Study Buddy", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv(r"C:\Users\sudhanshu\Downloads\AI Powerd study_buddy\study_buddy_clean.csv")

df = load_data()
stop_words = set(stopwords.words('english'))

# Functions

def exam_focused_summary(text, max_sentences=3):
    sentences = sent_tokenize(text)
    words = re.findall(r'\w+', text.lower())
    words = [w for w in words if w not in stop_words]
    freq = Counter(words)

    sentence_scores = {}
    for sent in sentences:
        for word in re.findall(r'\w+', sent.lower()):
            if word in freq:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + freq[word]

    ranked = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    return " ".join(ranked[:max_sentences])

def difficulty_level(answer):
    length = len(answer.split())
    if length <= 3:
        return "Easy"
    elif length <= 8:
        return "Medium"
    else:
        return "Hard"

df['difficulty'] = df['answer'].apply(difficulty_level)

# UI

st.title(" AI-Powered Study Buddy")
st.write("Exam-time assistant for quick understanding, revision, and practice.")

menu = st.sidebar.selectbox(
    "Choose a feature",
    ["Summarize Notes", "Quick Q&A", "Flashcards", "Quiz Practice"]
)

# Summarize
if menu == "Summarize Notes":
    st.subheader("Summarize Study Notes")
    text = st.text_area("Paste your study notes here")
    if st.button("Generate Summary"):
        st.success(exam_focused_summary(text))

# Q&A
elif menu == "Quick Q&A":
    st.subheader("Instant Question Answering")
    sample = df.sample(1).iloc[0]
    st.write("**Question:**", sample['question'])
    if st.button("Show Answer"):
        st.info(sample['answer'])

# Flashcards
elif menu == "Flashcards":
    st.subheader("Flashcards")
    sample = df.sample(1).iloc[0]
    st.write("**Question:**", sample['question'])
    if st.button("Flip Card"):
        st.success(sample['answer'])

# Quiz
elif menu == "Quiz Practice":
    st.subheader("Quiz Practice")
    level = st.selectbox("Select difficulty", ["Easy", "Medium", "Hard"])
    quiz = df[df['difficulty'] == level].sample(3)

    score = 0
    for i, row in quiz.iterrows():
        ans = st.text_input(row['question'], key=i)
        if ans:
            if ans.lower() in row['answer'].lower():
                score += 1

    if st.button("Submit Quiz"):
        st.info(f"Your score: {score} / 3")
