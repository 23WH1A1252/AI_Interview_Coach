import re

# Load transcript
with open("data/transcript.txt", "r") as f:    
    text = f.read().lower()

# Common filler words
filler_words = ["um", "uh", "like", "you know", "actually", "basically"]

# Count filler words
filler_count = {}
for word in filler_words:
    count = len(re.findall(r"\b" + word + r"\b", text))
    filler_count[word] = count

# Basic text statistics
words = text.split()
sentences = re.split(r'[.!?]', text)

print("🔍 TEXT ANALYSIS REPORT")
print("----------------------")
print("Total words:", len(words))
print("Total sentences:", len([s for s in sentences if s.strip()]))

print("\nFiller Word Usage:")
for word, count in filler_count.items():
    print(f"{word}: {count}")
unique_words = set(words)
vocab_richness = len(unique_words) / len(words)

print("Vocabulary Richness:", round(vocab_richness, 2))

