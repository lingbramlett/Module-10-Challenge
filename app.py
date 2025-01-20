# Import dependencies
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

#################################################
# Database Setup
#################################################
# Create engine to connect to the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the database
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Route 1: Homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Route 2: Precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query the last 12 months of precipitation data
    last_12_months = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= "2016-08-23"
    ).all()

    # Convert results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in last_12_months}

    return jsonify(precipitation_dict)

# Route 3: Stations data
@app.route("/api/v1.0/stations")
def stations():
    # Query all station names
    stations_list = session.query(Station.station).all()

    # Convert list of tuples into a list
    stations = list(np.ravel(stations_list))

    return jsonify(stations)

# Route 4: Temperature observations of the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(
        func.count(Measurement.station).desc()
    ).first()[0]

    # Query the last 12 months of temperature observations for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station
    ).filter(Measurement.date >= "2016-08-23").all()

    # Convert list of tuples into a list of dictionaries
    temperature_list = [
        {"date": date, "temperature": tobs} for date, tobs in temperature_data
    ]

    return jsonify(temperature_list)

# Route 5: Start and Start-End Range
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Query to calculate TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ).filter(Measurement.date >= start).all()

    # Convert query results to a dictionary
    temp_stats = {
        "start_date": start,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2],
    }

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Query to calculate TMIN, TAVG, and TMAX for dates between the start and end date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert query results to a dictionary
    temp_stats = {
        "start_date": start,
        "end_date": end,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2],
    }

    return jsonify(temp_stats)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
