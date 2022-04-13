from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from commands import db
import json
import pandas as pd
import ast

app = Flask(__name__)
CORS(app)
api = Api(app)


class DNDStore(Resource):
    def get(self):
        shop = db.records(f"SELECT * FROM shop")
        r_v = {"store": [{"item": s[0], "cost": s[1], "currency": s[2]} for s in shop]}
        # print(json.dumps(r_v))
        return r_v, 200


api.add_resource(DNDStore, "/dndstore")

if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
    # app.run()  # run our Flask app
