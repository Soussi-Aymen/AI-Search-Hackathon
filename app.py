from flask import Flask, render_template, request
import openai
from datetime import datetime

openai.api_key = ""

app = Flask(__name__)

def extract_seo_focus_areas(report: str) -> dict:
    output = {
        "missing_platforms": set(),
        "weak_presence": set(),
        "recommendations": [],
        "benchmark_gaps": [],
        "competitor_advantage": []
    }

    if "Areas for Improvement" in report:
        section = report.split("Areas for Improvement")[1].split("**3.")[0]
        if "Medium" in section.lower():
            output["missing_platforms"].add("Medium")
        if "TikTok" in section.lower():
            output["weak_presence"].add("TikTok")

    if "Recommendations" in report:
        section = report.split("Recommendations")[1]
        section = section.split("**4.")[0] if "**4." in section else section
        lines = [line.strip("- ").strip() for line in section.strip().split("\n") if line.strip().startswith("-")]
        output["recommendations"].extend(lines)
        for line in lines:
            if "Medium" in line:
                output["missing_platforms"].add("Medium")
            if "TikTok" in line:
                output["weak_presence"].add("TikTok")

    if "Competitor Benchmarking" in report:
        section = report.split("Competitor Benchmarking")[1]
        if "Adidas" in section and "Medium" in section:
            output["competitor_advantage"].append("Adidas uses Medium")
            output["benchmark_gaps"].append("Nike lacks Medium strategy vs Adidas")
        if "Foot Locker" in section:
            output["competitor_advantage"].append("Foot Locker receives fewer visits")

    output["missing_platforms"] = list(output["missing_platforms"])
    output["weak_presence"] = list(output["weak_presence"])
    return output

def get_visibility_report(brand, website, socials):
    prompt = f"""
    Analyze the AI search visibility for the brand '{brand}'.
    Consider presence on platforms like Google Search, YouTube, Instagram, LinkedIn, Wikipedia, Medium, and TikTok.
    Website: {website}
    Socials: {socials}

    1. Identify platform presence.
    2. Highlight areas for improvement.
    3. Recommend improvements.
    4. Benchmark against competitors.
    """

    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are an expert AI visibility analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        brand = request.form["brand"]
        website = request.form["website"]
        socials = request.form["socials"]
        report = get_visibility_report(brand, website, socials)
        seo_data = extract_seo_focus_areas(report)

        return render_template("results.html", brand=brand, report=report, seo=seo_data, timestamp=datetime.now())
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)