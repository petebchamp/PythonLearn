
import sys
import datetime as dt
import re
import os
from pylive import live_plotter
import numpy as np
import json
import pyodbc

file_path = '\\\<SERVER>\jboss-as-7.1.1.Final\standalone\log\\'
file_name = '<FILE>.log' #'HealthTRAC-12.30.0-24927.log' # 'HealthTRAC-12.30.0-24927.log.2019-09-20'
play_start = '2019-10-02 9:00:00' #Unless blank, format must be '%Y-%m-%d %H:%M'
play_end = '' #'2019-09-26 11:00' #Unless blank, format must be '%Y-%m-%d %H:%M'
realtime = False #True
window_length = 5

full_file_name = file_path + file_name
if not os.path.isfile(full_file_name):
    print('The path {} does not exist.' .format(full_file_name))
    sys.exit()

#realtime runs from now until midnight. If not realtime and no start time given, run from 8:00am to 5:00pm.
if realtime:
    play_time = dt.datetime.now() + dt.timedelta(hours = 1)
    play_start = play_time
    play_end = dt.datetime.combine(dt.date.today(), dt.time(23, 59, 59))
else:    
    if not play_start:
        play_start = dt.datetime.combine(dt.date.today(), dt.time(8))
        
    if not play_end:
        play_end = dt.datetime.combine(dt.date.today(), dt.time(17))
    

play_start = dt.datetime.strptime(str(play_start), '%Y-%m-%d %H:%M:%S')
play_end = dt.datetime.strptime(str(play_end), '%Y-%m-%d %H:%M:%S')    

#Get URL parameters, from '=' to '&'
def get_url_param(url, param_name):
    pattern =  r'' + param_name + '=' + '.+?&' #.+?&, with ? after .+, ensures non-greediness (i.e. find first &)
    match_obj = re.search(pattern, url + '&')

    if match_obj:
        param_value = re.sub('&', '', re.sub(param_name + '=', '', match_obj.group()))
    else:
        param_value = ''

    return param_value


#Initialize plot values
plot = True
size = 60
#x_vec = np.flip(np.linspace(0,-20,size+1)[0:-1]) #Returns same as below
x_vec = np.array(sorted(list(n * -1 for n in range(size))))
y_vec_lp = np.array(list(n * 0 for n in range(size)))
y_vec_lp_avg = np.array(list(n * 0 for n in range(size)))
y_vec_pap = np.array(list(n * 0 for n in range(size)))
y_vec_pap_avg = np.array(list(n * 0 for n in range(size)))
line_lp = []
line_lp_avg = []
line_pap = []
line_pap_avg = []


STARTSTOP_STRINGS = ['Starting KP.ORG', 'Starting FROM_LANDING_PAGE', 'Stopping KP.ORG', 'Stopping FROM_LANDING_PAGE']
hrn = ''
member_hrn = ''
nuid = ''
stop = False
pause = False
playing = False

#Initialize metrics
total_count_lp = 0
total_count_pap = 0
window_count_lp = 0
window_count_pap = 0
avg_duration_lp = 0
avg_duration_pap = 0
window_avg_duration_lp = 0
window_avg_duration_pap = 0
max_duration_lp = 0
max_duration_pap = 0
window_max_duration_lp = 0
window_max_duration_pap = 0
min_duration_lp = 99999
min_duration_pap = 99999
window_min_duration_lp = 99999
window_min_duration_pap = 99999

#DB Connection
driver = 'SQL Server'
server = 'CSC2CWN00001008.CLOUD.KP.ORG'
database = 'HealthTRAC_Dev' #'D425827_DEV'
conn = pyodbc.connect("DRIVER={%s};\
                      SERVER=%s;\
                      DATABASE=%s;\
                      Trusted_Connection=%s" % (driver, server, database, "yes"))
conn.autocommit = True
cursor = conn.cursor()

#Read log file and start interating
try:
    with open(full_file_name, 'r') as file:
        while not stop:
            line = file.readline()

            if 'URL for this FROM_LANDING_PAGE' in line:
                pattern = r'http://healthtrac'
                pattern = pattern + '.+'
                url = re.search(pattern, line).group()
                hrn = get_url_param(url, 'hrn')
                nuid = get_url_param(url, 'nuid')
                    
            elif 'URL for this KP.ORG is : http://' in line:
                pattern = r'http://healthtrac'
                pattern = pattern + '.+'                    
                url = re.search(pattern, line).group()
                hrn = get_url_param(url, 'hrn')
                member_hrn = get_url_param(url, 'memberHrn')
                nuid = get_url_param(url, 'nuid')
                    
            elif 'URL for this KP.ORG is : https://' in line:
                    pattern = r'https://healthtrac'
                    pattern = pattern + '.+'                    
                    url = re.search(pattern, line).group()
                    hrn = get_url_param(url, 'hrn')
                    member_hrn = get_url_param(url, 'memberHrn')
                    nuid = ''

            if any(s in line for s in STARTSTOP_STRINGS): #list comprehension - Starting or stopping action

                try:
                    log_datetime = (dt.datetime.strptime(line[:24], '%d %b %Y %H:%M:%S,%f'))
                except ValueError:
                    print('Invalid date string: ' + log_datetime)
                    continue #Next line
  
                #Kick off play (or replay) when we get to a file in the replay window
                if not playing:
                    if log_datetime < play_start:
                        continue #Next line
                    else:
                        playing = True
                        play_time = log_datetime
                        window_end_datetime = play_time + dt.timedelta(minutes = window_length)
               
                #While realtime or replaying, simulate log gap times (and plot zeroes) (i.e. periods of inactivity)
                while play_time <= log_datetime:
                    play_time = play_time + dt.timedelta(seconds = 30)
                    
                    if plot:
                        y_vec_lp[-1] = 0
                        y_vec_pap[-1] = 0
                        line_lp, line_lp_avg, line_pap, line_pap_avg = live_plotter(x_vec, y_vec_lp, line_lp, y_vec_lp_avg, line_lp_avg, y_vec_pap, line_pap, y_vec_pap_avg, line_pap_avg, identifier = 'PHT Activity', pause_time = .2)
                        y_vec_lp = np.append(y_vec_lp[1:], 0.0)
                        y_vec_lp_avg = np.append(y_vec_lp_avg[1:], y_vec_lp_avg[-1])
                        y_vec_pap = np.append(y_vec_pap[1:], 0.0)
                        y_vec_pap_avg = np.append(y_vec_pap_avg[1:], y_vec_pap_avg[-1])                        

                #Stop replay/file iteration
                if log_datetime > play_end:
                    playing = False
                    break
 
                #Set variables based on type of line
                if 'Starting KP.ORG' in line:
                    action = 'start'
                    target = 'pap'
                elif 'Starting FROM_LANDING_PAGE' in line:
                    action = 'start'
                    target = 'lp'
                elif 'Stopping KP.ORG' in line:
                    action = 'stop'
                    target = 'pap'
                elif 'Stopping FROM_LANDING_PAGE' in line:
                    action = 'stop'
                    target = 'lp'
               
                #start/stop actions
                if action == 'start':
                    event_start = log_datetime
                elif action == 'stop': #Action stopped, so calculate metrics and plot data
                    event_end = log_datetime
                    duration = (event_end - event_start).total_seconds() * 1000 #microseconds

                    #Reset (sub)window metrics, if window passed
                    if play_time > window_end_datetime:
                        window_end_datetime = window_end_datetime + dt.timedelta(minutes = window_length)
                        window_count_lp = 0
                        window_max_duration_lp = 0
                        window_min_duration_lp = 99999
                        window_avg_duration_lp = 0
                        window_count_pap = 0
                        window_max_duration_pap = 0
                        window_min_duration_pap = 99999
                        window_avg_duration_pap = 0

                    #Landing Page metrics
                    if target == 'lp':
                        total_count_lp += 1
                        if duration > max_duration_lp:
                            max_duration_lp = duration
                        if duration < min_duration_lp:
                            min_duration_lp = duration
                        avg_duration_lp = round(((avg_duration_lp * (total_count_lp - 1)) + duration) / total_count_lp, 1)

                        window_count_lp += 1
                        if duration > window_max_duration_lp:
                            window_max_duration_lp = duration
                        if duration < window_min_duration_lp:
                            window_min_duration_lp = duration
                        window_avg_duration_lp = round(((window_avg_duration_lp * (window_count_lp - 1)) + duration) / window_count_lp, 1)

                    #Personal Action Plan metrics
                    elif target == 'pap':
                        total_count_pap += 1
                        if duration > max_duration_pap:
                            max_duration_pap = duration
                        if duration < min_duration_pap:
                            min_duration_pap = duration
                        avg_duration_pap = round(((avg_duration_pap * (total_count_pap - 1)) + duration) / total_count_pap, 1)

                        window_count_pap += 1                    
                        if duration > window_max_duration_pap:
                            window_max_duration_pap = duration    
                        if duration < window_min_duration_pap:
                            window_min_duration_pap = duration                                            
                        window_avg_duration_pap = round(((window_avg_duration_pap * (window_count_pap - 1)) + duration) / window_count_pap, 1)                    
                    
                    
                    #Construct dict (json)
                    activity = {"hrn": str(hrn),
                                "nuid": nuid,
                                "target": target,                                
                                "event_start": str(event_start),
                                "event_end": str(event_end),
                                "duration": duration
                                }                    

                    if target == 'lp':
                        y_vec_lp[-1] = duration
                        y_vec_pap[-1] = 0                        
                        activity.update({"total_count_lp": total_count_lp})
                        activity.update({"max_duration_lp": max_duration_lp})
                        activity.update({"min_duration_lp": min_duration_lp})
                        activity.update({"avg_duration_lp": avg_duration_lp})
                        activity.update({"window_count_lp": window_count_lp})
                        activity.update({"window_max_duration_lp": window_max_duration_lp})
                        activity.update({"window_min_duration_lp": window_min_duration_lp})
                        activity.update({"window_avg_duration_lp": window_avg_duration_lp})                        
                    elif target == 'pap':
                        y_vec_lp[-1] = 0
                        y_vec_pap[-1] = duration
                        activity.update({"member_hrn": member_hrn})
                        activity.update({"total_count_pap": total_count_pap})
                        activity.update({"max_duration_pap": max_duration_pap})
                        activity.update({"min_duration_pap": min_duration_pap})
                        activity.update({"avg_duration_pap": avg_duration_pap})
                        activity.update({"window_count_pap": window_count_pap})
                        activity.update({"window_max_duration_pap": window_max_duration_pap})
                        activity.update({"window_min_duration_pap": window_min_duration_pap})
                        activity.update({"window_avg_duration_pap": window_avg_duration_pap})

                    json_activity = (json.dumps(activity))
                    print(json_activity)
                    print()

                    #Write to DB
                    sql = "INSERT INTO dbo.PHTActivity (Activity)"
                    cursor.execute(sql + " VALUES (?)", json_activity)
                    
                    #Plot
                    if plot:
                        y_vec_lp_avg[-1] = avg_duration_lp
                        y_vec_pap_avg[-1] = avg_duration_pap                       

                        line_lp, line_lp_avg, line_pap, line_pap_avg = live_plotter(x_vec, y_vec_lp, line_lp, y_vec_lp_avg, line_lp_avg, y_vec_pap, line_pap, y_vec_pap_avg, line_pap_avg, identifier = 'PHT Activity', pause_time = .2)
                        y_vec_lp = np.append(y_vec_lp[1:], 0.0)
                        y_vec_lp_avg = np.append(y_vec_lp_avg[1:], y_vec_lp_avg[-1])
                        y_vec_pap = np.append(y_vec_pap[1:], 0.0)
                        y_vec_pap_avg = np.append(y_vec_pap_avg[1:], y_vec_pap_avg[-1])

                    #End 'stop' action

except SystemExit:
    print()

except KeyboardInterrupt:
    sys.exit()

finally:
    if file:
        file.close()
        
    conn.close()
