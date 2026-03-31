import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def processing_text(text):
    text = text.lower()
    clean_text = ""

    for ch in text:
        if ch not in string.punctuation:
            clean_text += ch

    tokens = word_tokenize(clean_text)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    filtered_text = [
        lemmatizer.lemmatize(word, pos='v')
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(filtered_text)