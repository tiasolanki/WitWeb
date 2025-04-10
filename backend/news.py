from flask import Flask, request, jsonify
from flask_cors import CORS
import eventregistry
from eventregistry import *
import json
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  

apiKey = os.getenv("NEWS_API_KEY")

er = EventRegistry(apiKey)

@app.route('/get-news', methods=['POST'])
def get_news():
    data = request.json
    keywords_input = data.get('keywords')
    if not keywords_input:
        return jsonify({'error': 'No keywords provided'}), 400

    if isinstance(keywords_input, str):
        keywords_list = [keyword.strip() for keyword in keywords_input.split(',')]
    elif isinstance(keywords_input, list):
        keywords_list = keywords_input
    else:
        return jsonify({'error': 'Keywords must be a string or a list'}), 400

    try:
        q = QueryArticlesIter(
            keywords=QueryItems.OR(keywords_list),
            minSentiment=0.4,
            dataType=["news", "blog"]
        )

        articles = []
        for art in q.execQuery(er, sortBy="date", maxItems=2):
            articles.append({
                'Title': art.get('title', 'N/A'),
                'Date': art.get('date', 'N/A'),
                'Content': art.get('body', 'N/A'),
                'Link': art.get('url', 'N/A')
            })

        return jsonify(articles)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)