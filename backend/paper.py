import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


app = Flask(__name__)
CORS(app)  

def get_paperinfo(paper_url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(paper_url, headers=headers)

    if response.status_code == 200:
        paper_doc = BeautifulSoup(response.text, "html.parser")
    else:
        if response.status_code == 429:
            return response.status_code
        else:
            print("Status code:", response.status_code)
            return "error"
    return paper_doc

def get_tags(doc):
    paper_tag = doc.select("[data-lid]")
    cite_tag = doc.select("[title=Cite] + a")
    link_tag = doc.find_all("h3", {"class": "gs_rt"})
    author_tag = doc.find_all("div", {"class": "gs_a"})

    return paper_tag, cite_tag, link_tag, author_tag

def get_papertitle(paper_tag):
    paper_names = []
    for tag in paper_tag:
        paper_names.append(tag.select("h3")[0].get_text())
    return paper_names

def get_link(link_tag):
    links = []
    for i in range(len(link_tag)):
        try:
            links.append(link_tag[i].a["href"])
        except:
            links.append('NA')
    return links

def get_author_year_publi_info(authors_tag):
    years = []
    publication = []
    authors = []
    for i in range(len(authors_tag)):
        authortag_text = (authors_tag[i].text).split()
        try:
            year = int(re.search(r"\d+", authors_tag[i].text).group())
        except:
            year = 0
        years.append(year)
        publication.append(authortag_text[-1])
        author = authortag_text[0] + " " + re.sub(",", "", authortag_text[1])
        authors.append(author)
    return years, publication, authors

@app.route('/get-research-papers', methods=['POST'])
def get_research_papers():
    data = request.json
    keyword = data.get('keyword')
    page_range = data.get('page_range')

    keyword = keyword.replace(" ", "+")
    page_range = page_range.split("-")
    page_start = (int(page_range[0]) * 10) - 10
    page_stop = int(page_range[1]) * 10

    paper_data = {
        "paper_title": [],
        "year": [],
        "author": [],
        "publication": [],
        "url_of_paper": [],
    }

    for i in tqdm(range(page_start, page_stop, 10)):
        url = (
            "https://scholar.google.com/scholar?start="
            + str(i)
            + "&q="
            + keyword
            + "+&hl=en&as_sdt=0,5"
        )

        doc = get_paperinfo(url)
        if doc == 429:
            return jsonify({"error": "Too many requests, Google Scholar is blocking"}), 429
        elif doc == "error":
            return jsonify({"error": "Unable to fetch webpage"}), 500
        else:
            paper_tag, _, link_tag, author_tag = get_tags(doc)
            paper_titles = get_papertitle(paper_tag)
            years, publications, authors = get_author_year_publi_info(author_tag)
            links = get_link(link_tag)
            
            # Add paper information to the dictionary
            paper_data["paper_title"].extend(paper_titles)
            paper_data["year"].extend(years)
            paper_data["author"].extend(authors)
            paper_data["publication"].extend(publications)
            paper_data["url_of_paper"].extend(links)
            
            # Introduce a delay to avoid being blocked
            sleep(5)

    return jsonify(paper_data), 200

if __name__ == '__main__':
    app.run(debug=True)
