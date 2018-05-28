# -*- coding: utf-8 -*-
"""

@author: Evan Lowry
        evanwlowry@gmail.com
"""
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os.path
import time

def get_url(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    
    try:
        with closing(get(url, stream=True)) as resp:
            if good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def get_job_totals(level,field, state='US'):
    """
    This function scapes a url at engineerjobs.com and returns the number of 
    jobs posted with the parameters as criteria
    """
    
    field=field.lower()
    level=level.lower()
    state=state.upper()
    
    if state == 'US':
        st='';
    else: 
        full_st_list=['alabama','alaska','arizona','arkansas','california','colorado','connecticut','delaware','florida','georgia','hawaii','idaho','illinois','indiana','iowa','kansas','kentucky','louisiana','maine','maryland','massachusetts','michigan','minnesota','mississippi','missouri','montana','nebraska','nevada','new-hampshire','new-jersey','new-mexico','new-york','north-carolina','north-dakota','ohio','oklahoma','oregon','pennsylvania','rhode-island','south-carolina','south-dakota','tennessee','texas','utah','vermont','virginia','washington','west-virginia','wisconsin','wyoming']
        st_list=['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
        index = [i for i, s in enumerate(st_list) if state in s]
        st=full_st_list[index[0]]
        
    raw_html=get_url('https://www.engineerjobs.com/'+level+'/'+field+'/'+st+'/')
    html = BeautifulSoup(raw_html, 'html.parser')
    
    for p in html.select('span'):
       num_jbs=(p.text).split()  
       
    num_jbs=int(num_jbs[0].replace(',',''))
    print('Total number of ' + level + ' ' + field + ' jobs in ' + st + ': ' +str(num_jbs))
    
    return num_jbs

def for_all_states(field,level):
    """
    Run get_job_totals for every state in the US. The script saves the data in 
    a csv file each time the function is called
    """
    
    st_list=['AL','AZ','AR','CA','CO','CT','DE','FL','GA','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
    jobs=[]
    
    for st in st_list:
        njbs=get_job_totals(level,field,st)
        jobs.append(njbs)
        time.sleep(4)
    
    fname='job_stats_'+field+'_'+level+'.csv'
    os.path.isfile(fname) 
    now=datetime.datetime.now()
    date=str(now.month)+'-'+str(now.day)+'-'+str(now.year)+'-'+str(now.hour)+':'+str(now.minute)

    if os.path.isfile(fname) is False:
        csv=open(fname, "w")
        csv.truncate()
        csv.close()
        df_header=pd.DataFrame(st_list)
        df_header.to_csv(fname, index=False)
        df = pd.read_csv(fname)
        df_new = pd.DataFrame({date : jobs})
        df=df.join(df_new)
        df.to_csv(fname, index=False)
    else:
        df = pd.read_csv(fname)
        df_new = pd.DataFrame({date : jobs})
        df=df.join(df_new)
        df.to_csv(fname, index=False)
        
def main():
    """
    Modify the fields and levels that you are interested in scraping
    """
    fields=['software-engineering','chemical-engineering','petroleum-engineering','process-engineering','mechanical-engineering','civil-engineering','electrical-engineering','computer-engineering','']
    levels=['entry-level','mid-level','senior-level','jobs']
    for lvl in levels:
        for fld in fields:
            for_all_states(fld,lvl)

    
