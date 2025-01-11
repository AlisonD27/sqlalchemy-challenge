from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# connect to the database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect database into new model and reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session from Python to the DB
session = Session(engine)

## home route
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API<h2></center>"
        f"<center><h3>Select from one of the available routes:<h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
           )

# api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
   # return the previous year's precipitation as a json 
   previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()

   session.close()
   # dictionary with the date as the key and the precipitation (prcp) as the value
   precipitation = {date: prcp for date, prcp in results}
   # convert to json
   return jsonify(precipitation)

# api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # show a list of stations
    results = session.query(Station.station).all()
    session.close()

    stationsList = list(np.ravel(results))
    # convert to a Json and display
    return jsonify(stationsList)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    # return the previous year temperatures
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= previousYear).all()
    
    session.close()

    temperatureList = list(np.ravel(results))

    #jsonify list of temps
    return jsonify(temperatureList)

# /api/v1.0/start/end
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    # select statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        temperatureList = list(np.ravel(results))
        return jsonify(temperatureList)
    
    else:

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()

        session.close()

        temperatureList = list(np.ravel(results))
        return jsonify(temperatureList)
## app launcher
if __name__ == '__main__':
    app.run(debug=True)
