#This is my app
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

#DB Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)
Measurements = base.classes.measurement
Stations = base.classes.station


#Create the Applicatgion
app = Flask(__name__)

#routes
@app.route("/")
def homepage():
    return(
        f"Welcome to Pete's Weather App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;stop&gt;"
        f"<br><br>"
        f"For the 'start' and 'start'/'stop' routes please use the format below when entering dates"
        f"<br><br>"
        f"&lt;start&gt; route<br>"
        f"/api/v1.0/YYYY-MM_DD"
        f"<br><br>"
        f"&lt;start&gt;/&lt;stop&gt; route<br>"
        f"/api/v1.0/YYYY-MM_DD/YYYY-MM-DD"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    sess = Session(engine)
    #Query
    weatherdata = sess.query(Measurements.date, Measurements.prcp)
    #Place in Dataframe for data clean up
    weatherdata_df = pd.read_sql_query(sql = weatherdata.statement,con = engine)
    sess.close()
    #Replace null values with '0'
    weatherdata_df['prcp'] = weatherdata_df['prcp'].fillna(0)
    #Create dictionary for jsonify
    prcp_dict = dict(zip(weatherdata_df['date'], weatherdata_df['prcp']))

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    sess = Session(engine)
    Station_Data = sess.query(Stations.station).all()
    sess.close()

    station_list = list(np.ravel(Station_Data))
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    sess = Session(engine)
    # Find the most recent date in the data set.
    max_date1 = sess.query(Measurements.date).order_by(Measurements.date.desc()).first()
    #Use DateTime on most recent date.
    max_date = datetime.strptime(max_date1[0], '%Y-%m-%d')
    #Create a variable that will return all the dates for the last year,
    #starting at the most recent date.
    year_ago = max_date - relativedelta(years=1)
    #Station with the most activity.
    max_station = sess.query(Measurements.station).group_by(Measurements.station)\
    .order_by(func.count(Measurements.station).desc()).first()
    #Return the actual value of max_station
    max_station=max_station[0]
    #Put it all together
    station_hist= sess.query(Measurements.date,Measurements.tobs)\
    .filter(Measurements.station == max_station).filter(Measurements.date >= year_ago)
    #Create Dataframe for clean up
    yearly_temp_df = pd.read_sql_query(sql = station_hist.statement,con = engine)
    sess.close()
    yearly_temp_df['tobs'] = yearly_temp_df['tobs'].fillna(0)
    #Dataframe to dictionary
    yearlytemp_dict = dict(zip(yearly_temp_df['date'], yearly_temp_df['tobs']))
    yearlytemp_dict

    return jsonify(yearlytemp_dict)


@app.route("/api/v1.0/<start>")
def route_tempstart(start):
    sess = Session(engine)
    #List
    st_holder = []
    #Queries
    #Minimum Temperature for User Defined Timeframe (start date only)
    t_min = sess.query(Measurements.date, func.min(Measurements.tobs))\
    .filter(Measurements.date >= start)
    for date, tobs in t_min:
        t_min_dict = {}
        t_min_dict['date'] = date
        t_min_dict['MIN_tobs'] = tobs
        st_holder.append(t_min_dict)
    #Average Temperature for User Defined Timeframe (start date only)
    t_avg = sess.query(Measurements.date, func.round(func.avg(Measurements.tobs),2))\
    .filter(Measurements.date >= start)
    for date, tobs in t_avg:    
        t_avg_dict = {}
        t_avg_dict['date'] = date
        t_avg_dict['AVG_tobs'] = tobs
        st_holder.append(t_avg_dict)
    #Maximum Temperature for User Defined Timeframe (start date only)
    t_max = sess.query(Measurements.date, func.max(Measurements.tobs))\
    .filter(Measurements.date >= start)
    sess.close()
    #Write dictionary to list
    for date, tobs in t_max:
        t_max_dict = {}
        t_max_dict['date'] = date
        t_max_dict['MAX_tobs'] = tobs
        st_holder.append(t_max_dict)
    #Jsonify list
    return jsonify(st_holder)

@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start,end):
    sess = Session(engine)
    #List
    ste_holder = []
    #Queries
    #Minimum Temperature for User Defined Timeframe (start and end date)
    t_min = sess.query(Measurements.date, func.min(Measurements.tobs))\
    .filter(Measurements.date >= start)\
    .filter(Measurements.date <= end)
    for date, tobs in t_min:
        t_min_dict = {}
        t_min_dict['date'] = date
        t_min_dict['MIN_tobs'] = tobs
        ste_holder.append(t_min_dict)
    #Average Temperature for User Defined Timeframe (start and end date)
    t_avg = sess.query(Measurements.date, func.round(func.avg(Measurements.tobs),2))\
    .filter(Measurements.date >= start)\
    .filter(Measurements.date <= end)
    for date, tobs in t_avg:    
        t_avg_dict = {}
        t_avg_dict['date'] = date
        t_avg_dict['AVG_tobs'] = tobs
        ste_holder.append(t_avg_dict)
    #Maximum Temperature for User Defined Timeframe (start and end date)
    t_max = sess.query(Measurements.date, func.max(Measurements.tobs))\
    .filter(Measurements.date >= start)\
    .filter(Measurements.date <= end)
    sess.close()
    #Write dictionary to list 
    for date, tobs in t_max:
        t_max_dict = {}
        t_max_dict['date'] = date
        t_max_dict['MAX_tobs'] = tobs
        ste_holder.append(t_max_dict)
    #Jsonify list
    return jsonify(ste_holder)
    return

if __name__ == '__main__':
    app.run(debug=True)