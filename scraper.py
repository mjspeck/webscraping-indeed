import re
import datetime as dt
from time import sleep

from bs4 import BeautifulSoup
import urllib
import pandas as pd

def location_res(result):
    '''Function to extract location from Indeed search result'''
    
    tag = result.find(name='span', attrs={'class':'location'}) #find appropriate tag
    try:
        if re.search("<",tag.renderContents()): # helps clean the data; extract text instead of html code
            return tag.find(name='span', attrs={'itemprop':'addressLocality'}).renderContents()
        else:
            return entry.renderContents()
    except:
        return 'NaN'
    
def company_res(result):
    '''Function to extract company name from Indeed search result'''
    
    tag = result.find(name='span', attrs={'itemprop':'name'}) #find appropriate tag
    try: #First try statement accounts for whether there is any company at all
        try: #Second try statement accounts for whether there any nested tags
            return tag.find('a').renderContents()
        except:
            return tag.renderContents()
    except:
        return 'NaN'
    
def job_res(result):
    '''Function to extract job title'''
    
    try: #Accounts for missing job title
        tag = result.find(name='a', attrs={'data-tn-element':'jobTitle'})
        return tag.renderContents()
    except:
        return 'NaN'
    
def salary_res(result):
    '''Function to extract salary'''
    
    tag = result.find(name='td', attrs={'class':'snip'})
    tag2 = tag.find('nobr')
    try: # Try statement is especially important for this function since most results don't have a salary
        return tag2.renderContents()
    except:
        return 'NaN'
    
def all_funcs(search):
    '''
    This function iterates through each result on a single Indeed.com results
    page then applies the four functions above to extract the relevant
    information. It takes a search argument in order to also keep track of the 
    search term used, since location can give a different value than the actual
    city or location searched.'''
    
    entries=[]
    for result in soup.find_all(name='div', attrs={'class':' row result'}):
        result_data=[]
        result_data.append(job_res(result))
        result_data.append(company_res(result))
        result_data.append(location_res(result))
        result_data.append(salary_res(result))
        result_data.append(search)
        entries.append(result_data)
    return entries

def scrape(cities_list, max=3000):
    max_results_per_city = max
    results = [] #Empty list that will contain all results
    a = dt.datetime.now() # Start time of process
    print(a)

    for city in city_list: # Iterate through cities
        for start in range(0, max_results_per_city, 10): #Iterate through results pages
            url="http://www.indeed.com/jobs?q=data+scientist+%2420%2C000&l=" + city + "&start=" + str(start)
            html = urllib.urlopen(url).read()
            soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
            data = all_funcs(city) #use functions from before to extract all job listing info
            for i in range(len(data)): #add info to results list
                results.append(data[i])
            sleep(1)
        print(city + " DONE")
        print("Elapsed time: " + str(dt.datetime.now() - a)) #Update user on progress

    b = dt.datetime.now()
    c = b - a
    print(c)

    #Turn results list into dataframe
    df = pd.DataFrame(results,columns=['Job Title','Company','Location','Salary','Search Term'])
    
    name = str(dt.datetime.now())
    df.to_csv(f'./csvs/unclean_scraped_data/{now}.csv') #Save data
    
cities = ['New+York', 'Chicago', 'San+Francisco', 'Austin', 'Seattle', 
        'Los+Angeles', 'Philadelphia', 'Atlanta', 'Dallas', 'Pittsburgh', 
        'Portland', 'Phoenix', 'Denver', 'Houston', 'Miami', 'Washington%2C+DC', 
        'Baltimore', 'El+Paso', 'Boston','Bethesda%2C+MD','Morrisville%2C+NC',
        'Palo+Alto%2C+CA','Redmond%2C+WA','Mountain+View%2C+CA','El+Segundo%2C+CA',
        'Herndon%2C+VA','Menlo+Park%2C+CA', 'Collegeville%2C+PA','Roseland%2C+NJ',
        'Princeton%2C+NJ','St.+Louis%2C+MO', 'Tampa%2C+FL','Cambridge%2C+MA',
        'Stamford%2C+CT','Santa+Clara%2C+CA','Detroit', 'Ann+Arbor%2C+MI', 
        'Des+Moines%2C+IA', 'Minneapolis%2C+MN','New+Orleans']
    
scrape(cities)