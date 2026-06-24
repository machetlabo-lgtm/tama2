import re
import unicodedata

class SearchEngine:
    def __init__(self, dictionary_data):
        self.dictionary_data = dictionary_data
        self.reverse_index = {}
        self.french_stop_words = {
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'un', 'une', 'des', 
            'le', 'la', 'les', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'ce', 'cet', 'cette', 'ces'
        }
        self.stem_rules = {
            'veux': 'vouloir', 'veut': 'vouloir', 'voulons': 'vouloir', 'voulez': 'vouloir', 'veulent': 'vouloir',
            'vais': 'aller', 'va': 'aller', 'allons': 'aller', 'allez': 'aller', 'vont': 'aller',
            'peux': 'pouvoir', 'peut': 'pouvoir', 'pouvons': 'pouvoir', 'pouvez': 'pouvoir', 'peuvent': 'pouvoir',
            'aide': 'aider', 'aides': 'aider', 'aidons': 'aider', 'aidez': 'aider', 'aident': 'aider',
            'envoie': 'envoyer', 'envoies': 'envoyer', 'envoyons': 'envoyer', 'envoyez': 'envoyer', 'envoient': 'envoyer',
            'lettre': 'lettre', 'lettres': 'lettre'
        }
        self.build_index()

    def normalize_text(self, text):
        if not text:
            return ""
        text = text.replace("'", " ").replace("’", " ")
        text = text.lower()
        nkfd_form = unicodedata.normalize('NFKD', text)
        text = "".join([c for c in nkfd_form if not unicodedata.combining(c)])
        text = re.sub(r'[.,\/#!$%\^&\*;:{}=\-_`~()?¿¡"°º]', ' ', text)
        return text.strip()

    def stem_word(self, word):
        word = word.strip()
        if word in self.stem_rules:
            return self.stem_rules[word]
        if len(word) > 4 and word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        if len(word) > 4 and word.endswith('x'):
            return word[:-1]
        return word

    def build_index(self):
        print("[*] بناء الفهرس العكسي للبحث السريع لمرة واحدة فقط...")
        for entry in self.dictionary_data:
            searchable_blocks = []
            if entry.get("french_meanings"):
                searchable_blocks.extend(entry["french_meanings"])
            if entry.get("senses"):
                searchable_blocks.extend(entry["senses"])

            seen_tokens = set()
            for block in searchable_blocks:
                norm_block = self.normalize_text(block)
                for token in norm_block.split():
                    if token not in self.french_stop_words and len(token) > 1:
                        stemmed = self.stem_word(token)
                        seen_tokens.add(stemmed)
                        seen_tokens.add(token)

            for token in seen_tokens:
                if token not in self.reverse_index:
                    self.reverse_index[token] = []
                if entry not in self.reverse_index[token]:
                    self.reverse_index[token].append(entry)

    def analyze_sentence(self, sentence):
        normalized_sentence = self.normalize_text(sentence)
        tokens = normalized_sentence.split()
        
        results = []
        stats = {"total": len(tokens), "matched": 0, "unmatched": 0}

        for token in tokens:
            if token in self.french_stop_words:
                continue

            stemmed = self.stem_word(token)
            matches = []

            if stemmed in self.reverse_index:
                matches = self.reverse_index[stemmed]
            elif token in self.reverse_index:
                matches = self.reverse_index[token]

            if matches:
                stats["matched"] += 1
                status = "Trouvé"
            else:
                stats["unmatched"] += 1
                status = "Non trouvé"

            results.append({
                "token": token,
                "stemmed": stemmed,
                "status": status,
                "matches": matches
            })

        return {"stats": stats, "analysis": results}
