from base64 import b64decode
import os

from Fortuna import random_int, random_float
from MonsterLab import Monster
from flask import Flask, render_template, request, send_file
from pandas import DataFrame
from zipfile import ZipFile, ZIP_DEFLATED
from joblib import dump
from io import BytesIO

from app.data import Database
from app.graph import figure
from app.machine import Machine

SPRINT = 3
APP = Flask(__name__)


@APP.route("/")
def home():
    return render_template(
        "home.html",
        sprint=f"Sprint {SPRINT}",
        monster=Monster().to_dict(),
        password=b64decode(b"VGFuZ2VyaW5lIERyZWFt"),
    )


@APP.route("/data", methods=["GET", "POST"])
def data():
    if SPRINT < 1:
        return render_template("data.html")

    db = Database()
    options = [1024, 2048, 4096]
    amount = request.values.get("amount", type=int) or options[1]

    if request.method == 'POST' and int(amount) in options:
        db.reset()
        db.seed(int(amount))

    return render_template(
        "data.html",
        options=options,
        amount=amount,
        count=db.count(),
        table=db.html_table(),
    )


@APP.route("/view", methods=["GET", "POST"])
def view():
    if SPRINT < 2:
        return render_template("view.html")
    db = Database()
    options = ["Level", "Health", "Energy", "Sanity", "Rarity"]
    x_axis = request.values.get("x_axis") or options[1]
    y_axis = request.values.get("y_axis") or options[2]
    target = request.values.get("target") or options[4]
    graph = figure(
        df=db.dataframe(),
        x=x_axis,
        y=y_axis,
        target=target,
    ).to_json()
    return render_template(
        "view.html",
        options=options,
        x_axis=x_axis,
        y_axis=y_axis,
        target=target,
        count=db.count(),
        graph=graph,
    )


@APP.route("/model", methods=["GET", "POST"])
def model():
    if SPRINT < 3:
        return render_template("model.html")
    db = Database()
    options = ["Level", "Health", "Energy", "Sanity", "Rarity"]
    filepath = os.path.join("app", "model.joblib")
    retrain = request.values.get("retrain", type=lambda v: v.lower() == 'true',
                                 default=False)
    if not os.path.exists(filepath) or retrain:
        df = db.dataframe()
        machine = Machine(df[options])
        machine.save(filepath)
    else:
        machine = Machine.open(filepath)
    stats = [round(random_float(1, 250), 2) for _ in range(3)]
    level = request.values.get("level", type=int) or random_int(1, 20)
    health = request.values.get("health", type=float) or stats.pop()
    energy = request.values.get("energy", type=float) or stats.pop()
    sanity = request.values.get("sanity", type=float) or stats.pop()
    prediction, confidence = machine(DataFrame(
        [dict(zip(options, (level, health, energy, sanity)))]
    ))
    info = machine.info()
    return render_template(
        "model.html",
        info=info,
        level=level,
        health=health,
        energy=energy,
        sanity=sanity,
        prediction=prediction,
        confidence=f"{confidence:.2%}",
    )


@APP.route("/download", methods=["POST"])
def download():
    machine_path = os.path.join("app", "model.joblib")
    model_path = os.path.join("app/temp", "rfc.joblib")
    csv_path = os.path.join("app/temp", "monsters.csv")

    model = None
    if os.path.exists(machine_path):
        machine = Machine.open(machine_path)
        model = dump(machine._model, model_path)

    db = Database()
    db.dataframe().to_csv(csv_path)

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w', ZIP_DEFLATED) as zf:
        zf.write(csv_path, arcname="monsters.csv")
        if model:
            zf.write(model_path, arcname="rfc.joblib")
    memory_file.seek(0)

    return send_file(memory_file, mimetype='application/zip',
                     as_attachment=True, download_name='model.zip')


if __name__ == '__main__':
    APP.run()
