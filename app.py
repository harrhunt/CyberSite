from flask import Flask, render_template
import sass

sass.compile(dirname=('static/styles/sass', 'static/styles'), output_style='compressed')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
