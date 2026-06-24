from flask import Flask, render_template, request, jsonify
from dictionary_parser import DictionaryParser
from search_engine import SearchEngine

app = Flask(__name__)

# تحميل البيانات وبناء الفهرس عند بدء تشغيل الخادم مرة واحدة فقط لتوفير الموارد
parser = DictionaryParser()
dictionary_data = parser.load_or_parse()
search_engine = SearchEngine(dictionary_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json() or {}
    sentence = data.get("sentence", "").strip()
    if not sentence:
        return jsonify({"stats": {"total": 0, "matched": 0, "unmatched": 0}, "analysis": []})
    
    analysis_payload = search_engine.analyze_sentence(sentence)
    return jsonify(analysis_payload)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
