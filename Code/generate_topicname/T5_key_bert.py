from keybert import KeyBERT


# Load models
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

# Sample topics
sample_topics = [
    ['neural', 'network', 'gradient', 'loss'],
    ['vision', 'object', 'detection', 'image'],
    ['graph', 'embedding', 'node', 'representation'],
    ['quantum', 'physics', 'entanglement', 'measurement'],
    ['language', 'model', 'generation', 'context']
]

# Generate topic title using KeyBERT
def generate_topic_keybert_spacy(topic_words):
    text = ' '.join(topic_words)
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=2)
    return ", ".join([kw[0].title() for kw in keywords])

# Print output
print("{:<50} {}".format("TOPIC WORDS", "KEYBERT+spaCy"))
print("-" * 80)
for topic in sample_topics:
    kb_name = generate_topic_keybert_spacy(topic)
    print("{:<50} {}".format(", ".join(topic), kb_name))