from keybert import KeyBERT
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")

sample_topics = [
    ['neural', 'network', 'gradient', 'loss'],
    ['vision', 'object', 'detection', 'image'],
    ['graph', 'embedding', 'node', 'representation'],
    ['quantum', 'physics', 'entanglement', 'measurement'],
    ['language', 'model', 'generation', 'context']
]

def generate_topic_keybert_spacy(topic_words):
    text = ' '.join(topic_words)
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=2)
    return ", ".join([kw[0].title() for kw in keywords])

def generate_topic_t5(topic_words):
    prompt = "Generate a topic title: " + ', '.join(topic_words)
    inputs = t5_tokenizer(prompt, return_tensors="pt", max_length=64, truncation=True)
    outputs = t5_model.generate(**inputs, max_length=16, num_beams=4, early_stopping=True)
    return t5_tokenizer.decode(outputs[0], skip_special_tokens=True)

print("{:<50} | {:<40} | {}".format("TOPIC WORDS", "KEYBERT+spaCy", "T5 GENERATED"))
print("-"*120)
for topic in sample_topics:
    kb_name = generate_topic_keybert_spacy(topic)
    t5_name = generate_topic_t5(topic)
    print("{:<50} | {:<40} | {}".format(", ".join(topic), kb_name, t5_name))
