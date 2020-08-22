import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime 
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine,reflect=True)
Measurement=Base.classes.measurement
Station=Base.classes.station

app=Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to Home Page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start_date'<br/>"
        f"/api/v1.0/'start_date'/'end_date'<br/>"
        f"(start_date and end_date should be in yyyy/mm/dd format)"
        )
    
@app.route('/api/v1.0/precipitation')
def precipitation():
    
    session=Session(engine)
    last_date=session.query(Measurement.date).all()[-1][0]
    last_date_origin=dt.datetime.strptime(last_date,"%Y-%m-%d")
    last_date_p1=last_date_origin-dt.timedelta(days=365)
    last_date_p1=last_date_p1.strftime('%Y-%m-%d')
    last_y=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=last_date_p1).order_by(Measurement.date.asc()).all()
    session.close()

    precipitation_results={}
    for i in last_y:
        precipitation_results[i[0]]=i[1]
    

    return jsonify(precipitation_results)
    

@app.route('/api/v1.0/stations')
def station():
    session=Session(engine)

    stations=session.query(Measurement.station,func.count(Measurement.station))\
    .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()

    station_list=[station[0] for station in stations]

    return jsonify(station_list)


@app.route('/api/v1.0/tobs')
def tobs():
    #get the most active station
    session=Session(engine)

    stations=session.query(Measurement.station,func.count(Measurement.station))\
    .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    
    target=stations[0][0]

    #get the dates/temperature data
    sessison=Session(engine)
    last_date=session.query(Measurement.date).all()[-1][0]
    last_date_origin=dt.datetime.strptime(last_date,"%Y-%m-%d")
    last_date_p1=last_date_origin-dt.timedelta(days=365)
    last_date_p1=last_date_p1.strftime('%Y-%m-%d')
    last_date_p1

    temperature=session.query(Measurement.date,Measurement.tobs)\
    .filter(Measurement.date>=last_date_p1).filter(Measurement.station==target).all()

    session.close()

    temperature_df=pd.DataFrame(temperature)
    
    temperature_results={}
    for i in range(len(temperature_df)):
        row=temperature_df.iloc[i]
        temperature_results[row[0]]=row[1]
    
    return (jsonify([f'The most active station is {target}',temperature_results]))
           

@app.route('/api/v1.0/<start>')
def start(start):
    session=Session(engine)
    
    highest=session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).first()[0]
    lowest=session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).first()[0]
    average=round(session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).first()[0],1)
        
    session.close()

    results=[{'Highest Temperature':highest,'Average Temperature':average,'Lowest temperature':lowest}]
    
    return jsonify(results)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):

    session=Session(engine)
        
    highest=session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).\
            filter(Measurement.date<=end).first()[0]
    lowest=session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date>=start).\
            filter(Measurement.date<=end).first()[0]
    average=round(session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date>=start).\
            filter(Measurement.date<=end).first()[0],1)
        
    session.close()

    results=[{'Highest Temperature':highest,'Average Temperature':average,'Lowest temperature':lowest}]
    
    return jsonify(results)

@app.route('/test')
def test():
    n=[1,2,3]
    return (
        f"test<br/>"
        f"test2<br/>"
        f"{n}<br/>"
        f"test3<br/>"
    )

if __name__=="__main__":
    app.run(debug=True)