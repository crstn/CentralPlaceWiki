import pandas as pd
from geopy.distance import great_circle

geotags = pd.read_csv('/Volumes/Solid Guy/CPT Python Data/geo_tag.csv', escapechar='\\', encoding='utf-8')

print 'Geotagged pages loaded, links are next...'

links = pd.read_csv('/Volumes/Solid Guy/CPT Python Data/links.csv', escapechar='\\', encoding='utf-8')

print 'Links loaded, housekeeping...'

links.drop('toid', axis=1, inplace=True)
links.drop('id', axis=1, inplace=True)

print 'Copying part of table for self-join...'

right = links[['fromid','from']]
right = right.drop_duplicates()

print 'Housekeeping...'
right.rename(columns={'fromid': 'toid', 'from': 'to'}, inplace=True)
# right.to_csv('/Volumes/Solid Guy/CPT Python Data/uniqueArticles.csv', escapechar='\\', encoding='utf-8')

# left join to find the IDs of all 'linked-to' pages
print 'Performing self-join'
links = pd.merge(left=links, right=right, how='left', left_on='to', right_on='totitle')

# left join to find the IDs of all 'linked-to' pages
print 'Performing self-join'
links = pd.merge(left=links, right=right, how='left', left_on='to', right_on='to')

# links.info()

print 'Performing another left join to get the FROM lats and lons'

geotags.rename(columns={'gt_lat': 'from_lat', 'gt_lon': 'from_lon'}, inplace=True)
links = pd.merge(left=links, right=geotags, how='left', left_on='fromid', right_on='gt_page_id')

links.drop(['gt_name', 'gt_type', 'gt_country', 'gt_region', 'to', 'gt_page_id'], axis=1, inplace=True)

print 'And another one to get the TO lats and lons'

geotags.rename(columns={'from_lat': 'to_lat', 'from_lon': 'to_lon'}, inplace=True)
links = pd.merge(left=links, right=geotags, how='left', left_on='toid', right_on='gt_page_id')

links.drop(['gt_name', 'gt_type', 'gt_country', 'gt_region', 'gt_page_id'], axis=1, inplace=True)

print 'Next up: calcluating distance. This is going to take a while.'

links["dist_sphere_meters"] = map(lambda fromlat, fromlon, tolat, tolon: great_circle((fromlat, fromlon), (tolat, tolon)).meters, links["from_lat"], links["from_lon"], links["to_lat"], links["to_lon"])

print 'Final left-join to have all pages in one table later.'

right.rename(columns={'toid': 'gt_page_id'}, inplace=True)
pages = pd.merge(left=right, right=geotags, how='outer', on='gt_page_id')

pages.rename(columns={'gt_page_id': 'page_id', 'to': 'page', 'to_lon': 'lon', 'to_lat': 'lat', 'gt_type': 'type', 'gt_country': 'country', 'gt_region': 'region'}, inplace=True)
pages.drop(['gt_name'], axis=1, inplace=True)

print 'Exporting processed CSVs.'

pages.to_csv('/Volumes/Solid Guy/CPT Python Data/pages_processed.csv', escapechar='\\', encoding='utf-8')
links.to_csv('/Volumes/Solid Guy/CPT Python Data/links_processed.csv', escapechar='\\', encoding='utf-8')

print 'Good night'
