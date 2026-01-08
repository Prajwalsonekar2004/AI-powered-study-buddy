import streamlit as st
import pandas as pd
import nltk
import re
from collections import Counter
from nltk.corpus import stopwords

nltk.download('stopwords')

st.set_page_config(page_title="AI-Powered Study Buddy", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("study_buddy_clean.csv")

df = load_data()

stop_words = set(stopwords.words('english'))

# FUNCTIONS

def exam_focused_summary(text, max_sentences=3):
    if not text:
        return "Please enter some study text."

    sentences = text.replace("\n", " ").split(". ")

    words = re.findall(r'\w+', text.lower())
    words = [w for w in words if w not in stop_words]
    freq = Counter(words)

    sentence_scores = {}
    for sent in sentences:
        for word in sent.lower().split():
            if word in freq:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + freq[word]

    ranked = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    summary = ". ".join(ranked[:max_sentences])

    return summary if summary else "Unable to generate summary."

def difficulty_level(answer):
    length = len(str(answer).split())
    if length <= 3:
        return "Easy"
    elif length <= 8:
        return "Medium"
    else:
        return "Hard"

# Add difficulty column
df["difficulty"] = df["answer"].apply(difficulty_level)

# UI

st.title("AI-Powered Study Buddy")
st.write("Exam-time assistant for quick understanding, revision, and practice.")

menu = st.sidebar.selectbox(
    "Choose a feature",
    ["Summarize Notes", "Quick Q&A", "Flashcards", "Quiz Practice"]
)

# SUMMARIZE
if menu == "Summarize Notes":
    st.subheader("Summarize Study Notes")
    text = st.text_area("Paste your study notes here")
    if st.button("Generate Summary"):
        st.success(exam_focused_summary(text))

# Q&A
elif menu == "Quick Q&A":
    st.subheader("Instant Question Answering")
    sample = df.sample(1).iloc[0]
    st.write("**Question:**", sample["question"])
    if st.button("Show Answer"):
        st.info(sample["answer"])

# FLASHCARDS
elif menu == "Flashcards":
    st.subheader("Flashcards")
    sample = df.sample(1).iloc[0]
    st.write("**Question:**", sample["question"])
    if st.button("Flip Card"):
        st.success(sample["answer"])

# QUIZ
elif menu == "Quiz Practice":
    st.subheader("Quiz Practice")

    level = st.selectbox("Select difficulty", ["Easy", "Medium", "Hard"])

    # Lock quiz using session state
    if "quiz" not in st.session_state:
        st.session_state.quiz = df[df["difficulty"] == level].sample(3)

    quiz = st.session_state.quiz

    score = 0
    for idx, row in quiz.iterrows():
        ans = st.text_input(row["question"], key=idx)
        if ans:
            if ans.lower() in str(row["answer"]).lower():
                score += 1

    if st.button("Submit Quiz"):
        st.info(f"Your score: {score} / 3")
        del st.session_state.quiz
