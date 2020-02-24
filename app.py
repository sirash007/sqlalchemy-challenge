import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import numpy as np
import datetime as dt

#################################################
# Database Setup
# Found a lot of help on line.
# wokrs quite well
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp_range<br/>"
            )

@app.route("/api/v1.0/precipitation")
def precipitation_data():
    # Create our session (link) from Python to the DB


    """Return a list of measurement data including the date and precipitation"""
    # Query all measurements for precipitation, date, station and tobs (temp observed)
    session = Session(engine)
    precip_results = session.query(Measurement.date, Measurement.prcp, Measurement.station).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, precipitation, station in precip_results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = precipitation
        precipitation_dict["station"] = station
        all_precipitation.append(precipitation_dict)
    
    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():

    """Return a list of all station names"""
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp, Measurement.station, Measurement.tobs).all()
    session.close()

    # Pull from Measurement query above
    station_list = [(row[2]) for row in results]
    stations_unique = np.unique(np.array(station_list)).tolist()
   
    return jsonify(stations_unique)


@app.route("/api/v1.0/tobs")
def temps():
    """Return a list of temperature data for the last 1 year on record"""
    # Query all measurements for date and tobs (temp observed), filtered by the last 1 year of data
    
    query_date = "2016-08-23"
    session = Session(engine)
    temp_results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
    filter(func.strftime(Measurement.date) >= query_date)
    session.close()
    
    # Create a dictionary from the row data and append to a list of temperature data from the final year.
    one_year_temp = []
    for date, temp, station in temp_results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = temp
        temp_dict["station"] = station
        one_year_temp.append(temp_dict)

    return jsonify(one_year_temp)

@app.route("/api/v1.0/temp_range")
def temp_range():
    #######################
    ### ADJUST START DATE
    begin_date= "2014-08-06"
    ### ADJUST END DATE
    end_date = "2015-08-06"
    #######################
    
    #Query all measurements for date and tobs (temp observed), filtered by the specified range of data
    session = Session(engine)
    temp_results = session.query(Measurement.date, Measurement.tobs).\
    filter(func.strftime(Measurement.date) >= begin_date).filter(func.strftime(Measurement.date) <= end_date) 
    session.close()

    date = [(row[0]) for row in temp_results]
    tobs = [(row[1]) for row in temp_results]
    
    #Setup dictionary
    temp_dict = {}
    temp_dict["min"] = int(min (tobs))
    temp_dict["avg"] = int(sum(tobs) / len(tobs))
    temp_dict["max"] = int(max (tobs))
    
    ## Return the dictionary
    return ( temp_dict )

if __name__ == '__main__':
    app.run(debug=True)
