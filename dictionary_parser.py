import os
import re
import json
import pdfplumber
from pypdf import PdfReader

class DictionaryParser:
    def __init__(self, pdf_path="ASPT2015_dictionnaire de tumZabt & lexique fra-mzb_v15.10.pdf", cache_path="dictionary.json"):
        self.pdf_path = pdf_path
        self.cache_path = cache_path

    @staticmethod
    def clean_text(text):
        if not text:
            return ""
        return text.strip()

    def is_entry_head(self, line):
        if "/" not in line:
            return False
        parts = line.split("/", 1)
        left, right = parts[0].strip(), parts[1].strip()
        if not left or not right:
            return False
        upper_letters = sum(1 for c in right if c.isupper())
        total_letters = sum(1 for c in right if c.isalpha())
        if total_letters > 0 and (upper_letters / total_letters) >= 0.7:
            return True
        return False

    def parse_pdf(self):
        print(f"[*] البدء في استخراج النصوص من: {self.pdf_path}...")
        raw_lines = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        raw_lines.extend(text.splitlines())
        except Exception as e:
            print(f"[!] تفشل الأداة pdfplumber ({e})، يتم التحويل إلى pypdf...")
            reader = PdfReader(self.pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    raw_lines.extend(text.splitlines())

        print(f"[*] تم استخراج {len(raw_lines)} سطر. جاري معالجة الكلمات وتفكيكها...")
        
        entries = []
        current_entry = None

        for line in raw_lines:
            cleaned = line.strip()
            if not cleaned:
                continue

            if self.is_entry_head(cleaned):
                if current_entry:
                    entries.append(self.finalize_entry(current_entry))
                
                parts = cleaned.split("/", 1)
                headword = parts[0].strip()
                root = parts[1].strip()
                
                current_entry = {
                    "headword": headword,
                    "root": root,
                    "pos": "",
                    "raw_lines": [cleaned],
                    "senses": [],
                    "notes": [],
                    "french_meanings": []
                }
            else:
                if current_entry:
                    current_entry["raw_lines"].append(cleaned)
        
        if current_entry:
            entries.append(self.finalize_entry(current_entry))

        print(f"[+] تم حفظ وتنسيق {len(entries)} كلمة بنجاح.")
        
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
            
        return entries

    def finalize_entry(self, entry):
        raw_text = " ".join(entry["raw_lines"])
        entry["raw_entry"] = raw_text
        
        pos_match = re.search(r'\b(v\.intr\.|v\.tr\.|v\.|adj\.|adv\.|n\.m\.|n\.f\.|n\.|part\.\s+et\s+pron\.|part\.)', raw_text)
        if pos_match:
            entry["pos"] = pos_match.group(1)

        senses = re.split(r'(\d+°|\d+º|\$\d+^{\\circ}\$|\$\d+^{\\bcirc}\$)', raw_text)
        if len(senses) > 1:
            for i in range(1, len(senses), 2):
                sense_num = senses[i]
                sense_content = senses[i+1] if i+1 < len(senses) else ""
                clean_sense = sense_content.split("n.v.:")[0].split("cf.:")[0].strip()
                if clean_sense:
                    entry["senses"].append(f"{sense_num} {clean_sense}")
                    entry["french_meanings"].append(clean_sense)
        else:
            parts = raw_text.split("/", 1)
            meaning_part = parts[1] if len(parts) > 1 else raw_text
            meaning_part = re.sub(r'^(.*?)\b(v\.intr\.|v\.tr\.|v\.|adj\.|adv\.|n\.m\.|n\.f\.|n\.)', '', meaning_part)
            meaning_part = re.sub(r'\(.*?\)', '', meaning_part)
            
            clean_meaning = meaning_part.split("n.v.:")[0].split("cf.:")[0].split("dér.:")[0].strip()
            if clean_meaning:
                entry["french_meanings"].append(clean_meaning)

        note_matches = re.findall(r'\b(n\.v\.:|cf\.:|ex\.\s*à:|loc\.\s*à:|dér\s*\.\s*:|syn\.:|ant\.:)(.*?)(?=\b(?:n\.v\.:|cf\.:|ex\.\s*à:|loc\.\s*à:|dér\s*\.\s*:|syn\.:|ant\.:)|$)', raw_text)
        for tag, content in note_matches:
            entry["notes"].append(f"{tag} {content.strip()}")

        del entry["raw_lines"]
        return entry

    def load_or_parse(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self.parse_pdf()
