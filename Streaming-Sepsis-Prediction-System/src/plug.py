from pat_dat3 import get_patient_sepsis_scores 
res = get_patient_sepsis_scores(patient_id = '1', window_secs = 1000, interval_secs = 100, calc_cnt = 3)

timeList = []
for timeL in res['dt']:
    timeList.append( (timeL.time))


print str(timeList)

#print res['value']
