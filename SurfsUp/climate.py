# Import dependencies.
import datetime as dt
import numpy as np


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta




#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model.
Base = automap_base()
# Reflect the tables.
Base.prepare(autoload_with=engine)

# Save references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session from Python to the DB.
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
    """Available api routes:"""
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        
        f"Available Routes:<br/>"
        f"<br/>"
        
        f"Precipition:<br/>"
        f"<a href=http://127.0.0.1:5000/precipitation>"
        f"Precipitation amounts by date in the most recent year</a><br/>"
        f"<br/> "
        f"Stations:<br/>"
        f"<a href=http://127.0.0.1:5000/stations>"
        f"Weather station details</a></li><br/>"
        f"<br/>"
        f"Tobs:<br/>"
        f"<a href=http://127.0.0.1:5000/tobs>"
        f"Recorded Temperatures in the Most Recent Year</a><br/>"
        f"<br/>"
        f"Temperature Data with Start Date:<start><br/>"
        f"<a href=http://127.0.0.1:5000/2017-08-23>"
        f"Min, Avg and Max Temperatures For All Data  >=  the Start Date</a><br/>"
        f"<br/>"
        f"Temperature Data within Date Range:<start><end><br/>"
        f"<a href=http://127.0.0.1:5000/2016-08-23/2017-08-23>"
        f"Min, Avg and Max Temperatures For All Data in the Date Range</a><br/>"
    )


@app.route("/precipitation")
def precipitation():
    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

    # Open Session
    session = Session(engine)  
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - relativedelta(years=1)
    #year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    date_and_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    # Close Session
    session.close()

    # Iterate through query results, set each date as key and prcp as value   
    prcp_data_dict = {}
    for date, prcp in date_and_scores:
        prcp_data_dict[date] = prcp

    # Return the JSON representation of your dictionary.    
    return jsonify(prcp_data_dict)    

@app.route("/stations")
def stations():
    #Return a JSON list of stations from the dataset.

    # Open Session    
    session = Session(engine)
    # Query all station names
    results = session.query(Station.name).all()
    # Close Session
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return the JSON representation    
    return jsonify(all_stations)

@app.route("/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the previous year of data.     

    #Open Session 
    session = Session(engine)
    #Find the date 1 year prior
    year_ago = dt.date(2017,8,23) - relativedelta(years=1)   
    #year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query
    results = session.query(Measurement.tobs).filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').all()
    # Close Session
    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    # Convert list of tuples into normal list
    TOBS_data = list(np.ravel(results))

    # Return the JSON representation    
    return jsonify(TOBS_data)

@app.route("/<start>")
def start(start):

    # Open Session    
    session = Session(engine)
    # Find min, avg, and max temperature data on/after the start date
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    # Close Session
    session.close()

    # Append temperatures to a list
    temperatures = []
    for min_temp, avg_temp, max_temp in temperature_data:
        temperatures.append(min_temp)
        temperatures.append(avg_temp)
        temperatures.append(max_temp)

    return jsonify(temperatures)
        
@app.route("/<start>/<end>")
def start_end(start, end):
    

    # Open Session    
    session = Session(engine)
    # Find min, avg, and max temperature data between the two date ranges
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    # Close Session
    session.close()

    # Append temperatures to a list
    temperatures = []
    for min_temp, avg_temp, max_temp in temperature_data:
        temperatures.append(min_temp)
        temperatures.append(avg_temp)
        temperatures.append(max_temp)

    return jsonify(temperatures)

if __name__ == '__main__':
    app.run(debug=True)



