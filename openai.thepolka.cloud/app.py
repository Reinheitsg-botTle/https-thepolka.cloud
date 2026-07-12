from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    countries = [
        {
            "name":"United States",
            "gdp":"30.5T",
            "company":"Microsoft",
            "x":"28%",
            "y":"38%"
        },
        {
            "name":"China",
            "gdp":"19.2T",
            "company":"Tencent",
            "x":"62%",
            "y":"35%"
        },
        {
            "name":"Japan",
            "gdp":"4.4T",
            "company":"Toyota",
            "x":"82%",
            "y":"28%"
        }
    ]

    return render_template(
        "index.html",
        countries=countries
    )

if __name__ == "__main__":
    app.run(debug=True)
