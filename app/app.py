import time
import requests
import requests_cache
from maps import find_location

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

requests_cache.install_cache('github_cache', backend='sqlite', expire_after=180)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # user inputs
        demand = request.form.get('DEMAND')
        supply = request.form.get('SUPPLY')
        rent = request.form.get('RENT')
        recent_tx = request.form.get('RTX')
        human_presense = request.form.get('HMP')
        vibe = request.form.get('VIBE')
        print("rent {} supply {} demand {} recent tx {} human presence {} vibe {}".format(rent,supply,demand,recent_tx,human_presense,vibe))

        params = {
            "rent_weight":rent,
            "supply_weight":supply,
            "demand_weight":demand,
            "num_joints_weight":vibe,
            "num_users_weight":human_presense,
            "num_trans_weight":recent_tx}
        find_location(params=params)
        return render_template("temp.html")

    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
