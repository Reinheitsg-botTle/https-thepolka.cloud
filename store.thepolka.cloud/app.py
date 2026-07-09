from flask import Flask, render_template

app = Flask(__name__)

SERVICES = [
    {
        "name": "(1) AWS Cloud Consultation",
        "value": "$50.00",
        "description": "One-hour architecture and AWS advising session with 15 minute grace periods."
    },

    {
        "name": "(2) Cloud Deployment",
        "value": "$200",
        "description": "First time website or application deployment to AWS or Cloudflare. Each following deployment is $10 value off as a loyalty thank you."
    },

    {
        "name": "(3) Linux Server Support",
        "value": "$35 per hour",
        "description": "Linux administration and routine maintenance."
    },

    {
        "name": "(4) AI Application Development",
        "value": "Starting at $700 per package",
        "description": "Custom AI-powered software and workflow automation. Every 3rd package returns a credit of $100."
    },

    {
        "name": "(5) Privacy First Electronic Mail Service",
        "value": "Starting at $3,000 per annual provider",
        "description": "Discreet HR upgrade offering more employee safety on an email template of firstname@company/#lastnameinternalonly. See example in directory."
    },

    {
        "name": "(6) CRM Admin",
        "value": "$24,000 baseline per annual",
        "description": "Includes $12,000 credit in CRM admin when ordered on first consultation. ONLY PAY HALF THE COST!"
    },


]

@app.route("/")
def index():
    return render_template(
        "index.html",
        title="ThePolka.Cloud Boutique",
        services=SERVICES,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006, debug=True)
