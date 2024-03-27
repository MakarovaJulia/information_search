from flask import Flask, render_template, flash
from forms import SearchForm
from task5 import get_pages

app = Flask(__name__, template_folder='template')

app.config['SECRET_KEY'] = '25298acbde3308ee6f62abc70fbee87a'

@app.route("/", methods=["POST", 'GET'])
def search():
    form = SearchForm()
    result_list = None
    if form.validate_on_submit():
        query = form.query.data
        result_list = get_pages(query)
        print(query)
        print(result_list)
    return render_template("search.html", form = form, result_list=result_list)

if __name__ == "__main__":
    app.run()