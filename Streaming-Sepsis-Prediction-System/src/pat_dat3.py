import fhirclient.models.observation as o
import fhirclient.models.patient as p
import fhirclient.models.bundle as b
#import datetime as dtp
from dateutil.parser import parse as dtparse
from fhirclient import client
import datetime
import requests
import json
import numpy as np
import get_sepsis_score_python


#  Class that gets all the data for a patient id from a FHIR server and do aggragations on it.
#  Parameters are a patient id as a string and a FHIR Client to use
class pat_dat:
    # The list of observations we will include
    # Note that I've used them as they get returned from the FHIR data structure: they have leading and trailing blanks.
    # I did this so that we don't have to trim them every single time we read a measure and need to add it to the structure.
    # Kind of a pain for us referencing it but I think (not tested) that it makes things run much faster.
    observation_list = set([' respiration ', ' etco2 ', ' pt_inr ', ' systemicsystolic ', '   bun    ', ' fibrinogen ', ' creatinine ', '   ptt   ', ' potassium ', ' systemicmean ', '  hgb   ', ' glucose  ', ' platelets \n', ' heartrate ', ' chloride ', '  wbc   ', ' systemicdiastolic ', ' phosphate ', '   ast   ', ' total_bilirubin ', ' calcium ', '   hct   ', ' sao2 ', ' alkaline_phosphate ', '   wbc   ', ' magnesium '])

    def __init__(self, pat_id, smart_fhirclient):
        self.patientID = str(pat_id)
        smart = smart_fhirclient

        # Structure of data will be a dictionary with entries for each  observation type in our list.
        # Under each entry at that level will be another dictionary with only two values:
        #    dt - for a numpy area of dates
        #    value - for a numpy area of the measurements.
        # so for instance to reference the array of dates for respiration you would use pat_dat[' respiration ']['dt']
        self.pat_dat = {}
        # This is another dictionary of the aggragation functions for each observation type.  Right now it all
        # defaults to the numpy average function but if we want something different for a particular observation
        # type just link the function in the lines after the for loop sets the default.
        self.pat_ag_func = {}
        for obn in self.observation_list:
           self.pat_dat[obn] = { 'dt' : np.zeros(0), 'value': np.zeros(0) }
           self.pat_ag_func[obn] = np.average

        # set up the search.
        search = o.Observation.where(struct={'subject': 'Patient/'+pat_id})
        # run the search and get the observations.
        obs = search.perform(smart.server)

        # code stolen from William directly to loop through the results using URL instead of FHIRClient interface.
        # gets the bundles back which have 10 observations per bundle as json info and concatenates it together.
        lastUrl = ""
        jsonArray = []
        lastObject = obs.as_json()
        jsonArray.append(obs.as_json())
        # Print it out -
        lc = 0
        while 1 == 1:
            nex = lastObject
            lastUrl = nex['link'][1]['url']
            r = requests.get(lastUrl)
            if nex['link'][1]['relation'] == 'previous':
                break
            jsonArray.append(r.json())

            lastObject = r.json()

        #print jsonArray

        # More stuff stolen mostly.  This one loops through the jsonArray, gets the particular opservations
        # and places them into the pat_dat data structure.
        # if an observation type comes up we don't have in our observation list it just fails the try and skips it.
        # There is one observation that fails because it does not have an effective date
        for record in jsonArray:
            for rec2 in (record['entry']):
               try:
                    measure_name = str(rec2['resource']['code']['coding'][0]['display'])
                    dt = dtparse(rec2['resource']['effectiveDateTime'])
                    value = rec2['resource']['valueQuantity']['value']
                    self.pat_dat[measure_name]['dt'] = np.append(self.pat_dat[measure_name]['dt'],   dt)
                    self.pat_dat[measure_name]['value'] = np.append( self.pat_dat[measure_name]['value']  ,value)

               except:
                    pass

    # Return a data structure with all the observation types aggragated for how ever much data we have.
    # the return is a dictionary of the items in our observation list with the values.
    #  If there is not data for an obeservation type Nan Will be returned.
    # No parameters
    def get_aggragation_all(self):
        pat_ag = {}
        for obn in self.observation_list:
           pat_ag[obn] = self.pat_ag_func[obn](self.pat_dat[obn]['value'])
        return pat_ag

    # Return a data structure with all the observation types aggragated for the data between two date times
    # the return is a dictionary of the items in our observation list with the values.
    #  If there is not data for an obeservation type Nan Will be returned.
    # Parameters - Two strings that specify the start and Stop datetimes inclusive.
    def get_aggragation_for_dates_old(self, start_date, end_date):
        search_date = dtparse(start_date)
        search_date2 = dtparse(end_date)
        pat_ag = {}
        for obn in self.observation_list:
           pat_ag[obn] = self.pat_ag_func[obn](self.pat_dat[obn]['value'][(self.pat_dat[obn]['dt'] >= search_date) & (self.pat_dat[obn]['dt'] <= search_date2)])

        return pat_ag

    def get_aggragation_for_dates(self, start_date, end_date):
        # search_date = dtparse(start_date)
        # search_date2 = dtparse(end_date)
        pat_ag = {}
        for obn in self.observation_list:
           pat_ag[obn] = self.pat_ag_func[obn](self.pat_dat[obn]['value'][(self.pat_dat[obn]['dt'] >= start_date) & (self.pat_dat[obn]['dt'] <= end_date)])

        return pat_ag


    # Return the a dictionary with the dt and value numpy arrays for a particular observation type
    def get_measure_data(self, measure):
        return self.pat_dat[measure]

    # Return the whole pat_dat data structure.
    def get_raw_pat_data(self):
        return self.pat_dat

    # Return a data structure with a count of total observations for each observation types
    # the return is a dictionary of the items in our observation list with the counts.
    #  If there is not data for an obeservation type Nan will be returned.
    def get_measure_counts_all(self):
        pat_cnt = {}
        for obn in self.observation_list:
           pat_cnt[obn] = np.size(self.pat_dat[obn]['dt'])

        return pat_cnt

    def get_measure_total_count_all(self):
        pat_cnt = 0
        for obn in self.observation_list:
           pat_cnt = pat_cnt + np.size(self.pat_dat[obn]['dt'])

        return pat_cnt

    # Return a data structure with a count of observations for each observation types between two dates
    # the return is a dictionary of the items in our observation list with the counts.
    #  If there is not data for an obeservation type Nan will be returned.
    # Parameters - Two strings that specify the start and Stop datetimes inclusive.
    def get_measure_counts_for_dates(self, start_date, end_date):
        search_date = dtparse(start_date)
        search_date2 = dtparse(end_date)
        pat_cnt = {}
        for obn in self.observation_list:
            pat_cnt[obn] = sum((self.pat_dat[obn]['dt'] >= search_date) & (
                                                    self.pat_dat[obn]['dt'] <= search_date2))
        return pat_cnt
    #
    # This works but kind of hate this funtion - creating a huge numpy array to min and max on.
    # wanted to just min max each observation list and then take the min and max of those.
    # This method has one distinct advantage though - it works.
    def get_min_max_dts(self):

        all_dates = np.zeros(0)
        for obn in self.observation_list:
            all_dates = np.concatenate((all_dates, self.pat_dat[obn]['dt']))

        return { 'min': np.min(all_dates), 'max': np.max(all_dates)}


#######################################################################################################
##############  END of Class definition - Rest is functions using class to calculate sepsis scores
#########################################################################################################

# Just fill forward on a one dim array using vector methods
def ff(ar):
    mask = np.isnan(ar)
    idx = np.where(~mask, np.arange(mask.shape[0]), 0)
    np.maximum.accumulate(idx, out=idx)
    return ar[idx]

# Fill forward and then back - kind of stupid method - fill forward reverse array, fill forward again, reverse back
def ff_and_bf (ar):
    ar=ff(ar)
    ar=ar[::-1]
    ar=ff(ar)
    return ar[::-1]

# Takes a snapshot of each patient measurement for a set of dates.   Missing data is filled in by first fill forward
# and then fill back.  It is assumed that the calcuations will be done from the last date for which we have data and
# and then going backward in time.   This only works because we are doing test cases.  In real life we would want to
# specify the end date probably.
# Parameters:
#               patient_id:  The patient who's data we want to calculate agregates for.  String of the Patient id.
#               interval_secs;  The interval between snapshots in seconds.
#               calc_cnt:  How many snapshots we want to do.
#               window_secs:  Time frame over when we want to do the agregation in seconds.
#
# So patient_id = '1', interval_secs = 600, calc_cnt = 40 and window_secs = 72000 would mean we calculate our aggregates
# for over the previous 2 hours and we do 40 aggregates that take place every 10 minutes. The last aggregate will be at
# the time the last measurement for the patient was made and go back in time with one every 10 minutes.  If a particular
# measure has no values recorded over the entire window than the value from a previous aggregate will be used if there
# is one.   Just to fill in values at the very begining of the dates returned back fill may be used.
#
# The return is a dictionary with entries for datas ('dt') which is the dates of the snapshots and then an entry
# for each observation type which will be a numpy array of values.  For a given patient the aggregate will be NaN if
# no data existed.
def get_patient_aggregate_data(patient_id = '212',
                              window_secs = 72000,
                              interval_secs = 600,
                              calc_cnt = 40):
    settings = {
        'app_id': 'my_web_app',
        'api_base': "http://35.192.2.85:8080/baseDstu2/",
        'count': '500'
    }

    smart = client.FHIRClient(settings=settings)
    pd = pat_dat(patient_id,smart)

    pat_ag_dat = {}
    for obn in pd.observation_list:
        pat_ag_dat[obn] = np.zeros(0)
    pat_ag_dat['dt'] = np.zeros(0)

    end_tm = pd.get_min_max_dts()['max']
    for i  in range(calc_cnt):
        start_tm = end_tm - datetime.timedelta(seconds=window_secs)
        new_vals = pd.get_aggragation_for_dates(start_tm, end_tm)
        pat_ag_dat['dt'] = np.append(pat_ag_dat['dt'], end_tm )
        for obn in pd.observation_list:
            pat_ag_dat[obn] = np.append(pat_ag_dat[obn], new_vals[obn] )
        end_tm = end_tm - datetime.timedelta(seconds=interval_secs)

    pat_ag_dat['dt'] = pat_ag_dat['dt'][::-1]
    for obn in pd.observation_list:
        pat_ag_dat[obn] = pat_ag_dat[obn][::-1]
        pat_ag_dat[obn] = ff_and_bf(pat_ag_dat[obn])

    return pat_ag_dat


# This is my dummy sepsis function that just return random values.
def get_sepesis_score_python(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16,var17,var18,var19,var20,var21,var22,var23,var24,var25,var26,var27,var28,var29,var30,var31,var32,var33,var34,var35):
    scorer = get_sepsis_score_python.initialize()
    #score = scorer.get_sepsis_score_python(1)

    #print str(var1), str(var2), str(var3), str(var4), str(var5), str(var6), str(var7), str(var8), str(var9), str(var10), str(var11), str(var12), str(var13), str(var14), str(var15), str(var16),str(var17), str(var18), str(var19), str(var20), str(var21), str(var22), str(var23), str(var24),str(var25), str(var26), str(var27), str(var28), str(var29), str(var30), str(var31), str(var32), str(var33), str(var34), str(var35)
    score = scorer.get_sepsis_score_python(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16,var17,var18,var19,var20,var21,var22,var23,var24,var25,var26,var27,var28,var29,var30,var31,var32,var33,var34,var35)
    return score

# Calculate sepsis values from an array of aggregated data.
# Returns a dictionary with to entries 'dt' - array of dates, 'values' - the sepsis values
# To call it you need the agregated data and the patient age and patient gender from the Patient FHIR data.
# this where where the parameters get mapped for Dr. Nemati's sepsis calculation get done.
# Few issues:
#    1) For items we don't have any data for I map them to None here - not sure if that works.  Might be better to
#       do Nan - not sure here.  Might be better to have some other default value.
#    2) For data missing for a particuler patient the data array will ben NaN. Might be better to map these to None
#       or maybe some other defualt value.
#    3) I have one measure left I could not figure out what parameter it would be pt_inr - so it's not input to the
#       the sepsis algorithm at this point.
def call_the_magic_sepsis_algorithm (adata, pat_age, pat_gender):
    default_val = False            

    sepsis_scores = { 'dt': np.copy(adata['dt']), 'value':    np.zeros(len(adata['dt'])) }
    for i in range(len(adata['dt'])):
        sepsis_scores['value'][i] = get_sepesis_score_python(
                            var1 = nan_to_false(adata[' heartrate '][i]),
                            var2 = nan_to_false(adata[' sao2 '][i]),
                            var3 = default_val,
                            var4 = nan_to_false(adata[' systemicsystolic '][i]),
                            var5 = nan_to_false(adata[' systemicmean '][i]),
                            var6 = nan_to_false(adata[' systemicdiastolic '][i]),
                            var7 = nan_to_false(adata[' respiration '][i]),
                            var8 = nan_to_false(adata[' etco2 '][i]),
                            var9 = default_val,
                            var10 = default_val,
                            var11 = default_val,
                            var12 = default_val,
                            var13 = default_val,
                            var14 = default_val,
                            var15 = nan_to_false(adata['   ast   '][i]),
                            var16 = nan_to_false(adata['   bun    '][i]),
                            var17 = nan_to_false(adata[' alkaline_phosphate '][i]),
                            var18 = nan_to_false(adata[' calcium '][i]),
                            var19 = nan_to_false(adata[' chloride '][i]),
                            var20 = nan_to_false(adata[' creatinine '][i]),
                            var21  = default_val,
                            var22 = nan_to_false(adata[' glucose  '][i]),
                            var23 = nan_to_false(adata[' magnesium '][i]),
                            var24 = nan_to_false(adata[' phosphate '][i]),
                            var25 = nan_to_false(adata[' potassium '][i]),
                            var26 = nan_to_false(adata[' total_bilirubin '][i]),
                            var27 = default_val,
                            var28 = nan_to_false( adata['   hct   '][i]),
                            var29 = nan_to_false(adata['  hgb   '][i]),
                            var30 = nan_to_false(adata['   ptt   '][i]),
                            var31 = nan_to_false(adata['  wbc   '][i]),
                            var32 = nan_to_false(adata[' fibrinogen '][i]),
                            var33 = nan_to_false(adata[' platelets \n'][i]),
                            var34 = 1.0,
			    var35 = 1.0)
    print 'test', str(sepsis_scores)                                
    return sepsis_scores
                            

def nan_to_false(x):
    if np.isnan(x):
        ans = False
    else:
        #print str(x)
        ans = float(x)

    return ans

def get_patient_sepsis_scores(patient_id = '212',
                              window_secs = 72000,
                              interval_secs = 600,
                              calc_cnt = 40,
                              patient_age = 35,
                               patient_gender = 'Female'):

    pat_ag_data = get_patient_aggregate_data(patient_id ,
                              window_secs ,
                              interval_secs ,
                              calc_cnt )

    return call_the_magic_sepsis_algorithm(pat_ag_data,  patient_age, patient_gender)
# Calculate sepsis values from an array of aggregated data.
# Returns a dictionary with to entries 'dt' - array of dates, 'values' - the sepsis values
# To call it you need the agregated data and the patient age and patient gender from the Patient FHIR data.
# this where where the parameters get mapped for Dr. Nemati's sepsis calculation get done.
# Few issues:
#    1) For items we don't have any data for I map them to None here - not sure if that works.  Might be better to
#       do Nan - not sure here.  Might be better to have some other default value.
#    2) For data missing for a particuler patient the data array will ben NaN. Might be better to map these to None
#       or maybe some other defualt value.
#    3) I have one measure left I could not figure out what parameter it would be pt_inr - so it's not input to the
#       the sepsis algorithm at this point.
#rint get_patient_sepesis_scores()
