# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta
import datetime as dt
from datetime import datetime as dtime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

#Session opened and closed for each api call below:

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
        f"<br>"
        f"You can edit the below dates to change the required range, using format: YYYY-MM-DD:<br>"
        f"/api/v1.0/2010-01-01<br/>"
        f"/api/v1.0/2010-01-01/2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation values for latest year
    from_date = dt.date(2017,8,23) - relativedelta(years=1)
    output = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= from_date).order_by(Measurement.date)

    #Close Session
    session.close()


    # Create a dictionary from the row data and append to a list of all precipitation measurements
    all_measurements = []
    
    for date, prcp in output:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_measurements.append(measurement_dict)

    return jsonify(all_measurements)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    stations = session.query(Station)

    #Close Session
    session.close()

    # Create a dictionary from the row data and append to a list of all stations
    all_stations = []

    for row in stations:
        station_dict = {}
        station_dict["id"] = row.id
        station_dict["station"] = row.station
        station_dict["name"] = row.name
        station_dict["longitude"] = row.longitude
        station_dict["latitude"] = row.latitude
        station_dict["elevation"] = row.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query temperature values for latest year for the most active station
    from_date = dt.date(2017,8,23) - relativedelta(years=1)
    output = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281')\
    .filter(Measurement.date >= from_date).order_by(Measurement.date)

    #Close Session
    session.close()

    # Create a dictionary from the row data and append to a list of all temperature measurements
    all_temps = []
    
    for date, tobs in output:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["tobs"] = tobs
        all_temps.append(temps_dict)

    return jsonify(all_temps)


@app.route("/api/v1.0/<start>")
def summary_from(start):

    from_date = dtime.strptime(start, '%Y-%m-%d')

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query summary values from the start date forward
    summary_measurements = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= from_date).first()
    
    #Close Session
    session.close()

    # Create a dictionary from the summary information
    summary_results = {}
    summary_results["Min"] = summary_measurements[0]
    summary_results["Max"] = summary_measurements[1]
    summary_results["Avg"] = summary_measurements[2]

    return jsonify(summary_results)

@app.route("/api/v1.0/<start>/<end>")
def summary_fromto(start, end):

    from_date = dtime.strptime(start, '%Y-%m-%d')
    to_date = dtime.strptime(end, '%Y-%m-%d')

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query summary values from between the start and end dates
    summary_measurements = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= from_date).filter(Measurement.date <= to_date).first()
    
    #Close Session
    session.close()

    # Create a dictionary from the summary information
    summary_results = {}
    summary_results["Min"] = summary_measurements[0]
    summary_results["Max"] = summary_measurements[1]
    summary_results["Avg"] = summary_measurements[2]

    return jsonify(summary_results)

if __name__ == '__main__':
    app.run(debug=True)