import numpy as np
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify# Import the dependencies.



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine)


# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results from your precipitation analysis
      (i.e. retrieve only the last 12 months of data) to a dictionary using 
      date as the key and prcp as the value"""
    
    recent_query =session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent = list(map(int,(recent_query.date.replace("-", ", ").split(', '))))

    #Grab the integer values for year, month, and day
    year = recent[0]
    month = recent[1]
    day = recent[2]

    # Calculate the date one year from the last date in data set.
    last_year = dt.date(year, month, day) - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()

    # Convert list of tuples into normal list
    results_ls = []
    
    for date, prcp in results:
        results_dict = {}
        results_dict["date"] = date
        results_dict["prcp"] = prcp
        results_ls.append(results_dict)

    return jsonify(results_ls)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.station).all()
    session.close()
    
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most-active station for the previous year of data.
    Return a JSON list of temperature observations for the previous year."""
    most_active = session.query(Measurement.station, Measurement.date).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    recent = list(map(int,(most_active.date.replace("-", ", ").split(', '))))

    #Grab the integer values for year, month, and day
    year = recent[0]
    month = recent[1]
    day = recent[2]

    # Calculate the date one year from the last date in data set.
    last_year = dt.date(year, month, day) - dt.timedelta(days=365)
    # Query most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active.station).filter(Measurement.date > last_year ).all()
    session.close()
    

    results_ls = []
    for date, tobs in results:
        results_dict = {}
        results_dict["date"] = date
        results_dict["tobs"] = tobs
        results_ls.append(results_dict)

    return jsonify(results_ls)



@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""

    # Get Min, Avg, and Max for tobs starting at date entered in API call
    results_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()


    resluts_start_ls = list(np.ravel(results_start))
    return jsonify(resluts_start_ls)



@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Get Min, Avg, and Max for tobs starting at date entered in API call and ending in date entered in the API call
    session = Session(engine)

    """For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""

    # go back one year from start date and go to end of data for Min/Avg/Max temp   
    results_start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()


    resluts_start_end_ls = list(np.ravel(results_start_end))
    return jsonify(resluts_start_end_ls)

if __name__ == '__main__':
    app.run(debug=True)
