import requests
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

### WEB SCRAPPER - ca.Indeed ###

# Build a string the main URL, search term, and location
def get_url(query, loc):
    url = 'https://ca.indeed.com/jobs?'
    query = 'q=' + urllib.parse.quote_plus(query)
    loc = '&l=' + urllib.parse.quote_plus(loc)
    url += query + loc
    return url

# Request HMTL from URL, create and return a SOUP object with it 
def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    page = requests.get(url, headers=headers)
    return BeautifulSoup(page.content, 'html.parser')

# Scrap the given number of pages for the given search term and location
# Return a df with the collected data
def scrap_jobs(query, loc, pages):
    # get pages/soup
    for start in np.arange(0, (pages*10)+1, 10):
        url = get_url(query, loc)+ '&start='+str(start)
        soup = get_soup(url)
        # get all cards in the webpage
        regex = re.compile('.*jobsearch-SerpJobCard.*')
        cards = soup.find_all(class_=regex)
        # create lists if first run
        if start == 0: 
            title, company, salary, location, post_url = [], [], [], [], []
        # get data
        for card in cards:
            if str( card.find(class_='title')) != 'None':
                title.append( card.find('h2', class_='title').find('a')['title'])
                company.append( card.find(class_='company').text.strip())

                if str( card.find(class_='salaryText')) != 'None':
                       salary.append( card.find( class_='salaryText').text.strip())
                else:
                       salary.append('NA')

                location.append( card.find(class_='location accessible-contrast-color-location').text)
                post_url.append( card.find(class_='title').find('a')['href'])

    # Build DF
    df = pd.DataFrame(title, columns = ['title'])

    df['company'], df['salary'],  = company, salary
    df['location'], df['post_url'] = location, post_url
    
    return df

def get_summary(df, pay, bins):
    # Calculate average Salary
    average_sal = []
    salaries = df[df.salary.str.contains(pay)]
    for txt in salaries['salary'].values:
        result = re.findall('[\d]*[,.]*[0-9]+', txt)
        result = ([float(i.replace(',','')) for i in result])

        if len(result) > 1:
            average_sal.append( np.mean(result))
        else:
            average_sal.append(result[0])

    # Print summarized data
    s = """{} - {}
    Average Salary ${:,.2f}, calculated from a sample of {} jobs
    posted by {} unique companies."""

    print(s.format( query.upper(), loc.upper(),
                    np.mean(average_sal), 
                    len(salaries), 
                    len(salaries.company.unique())))

    print('\nSome titles found:')
    print(salaries.title.unique()[:5])
    # plot charts
    plt.hist(average_sal, bins=bins)
    plt.title('Salaries Distribution')
    plt.show()


# Get inputs
print('Search Term: ')
query = input()

print('Location: ')
loc = input()

print('Number of Pages to be Scrapped: ')
pages = int(input())

print('Building data frame')
df = scrap_jobs(query, loc, pages)
df.to_csv('jobs.csv', index=False)
print('Data frame saved...')

print('Build Summary? [y/n]')
if(input().upper() == 'Y'):
    print('Yealy salary or hourly pay? [year/hour]')
    pay = input() #hour, year

    print('Number of bins in the histogram:')
    bins = int(input())
    print('##==##==##==##==##==##==##==##==##')
    get_summary(df, pay, bins)