import pandas as pd
from geopy.distance import great_circle
from sqlalchemy import create_engine

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
links = pd.merge(left=links, right=right, how='left', on='to')

# left join to find the IDs of all 'linked-to' pages
print 'Performing self-join'
links = pd.merge(left=links, right=right, how='left', left_on='to', right_on='to')

# links.info()

print 'Performing another left join to get the FROM lats and lons'

geotags.rename(columns={'from_lat': 'to_lat', 'from_lon': 'to_lon', 'gt_name': 'to' }, inplace=True)

links = pd.merge(left=links, right=geotags, how='left', left_on='fromid', right_on='gt_page_id')
links.drop(['gt_type', 'gt_country', 'gt_region', 'gt_page_id'], axis=1, inplace=True)

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


# we can write these dataframes to CSV files:
print 'Exporting processed CSVs.'

# make sure all integers are integers in the output:
pages[['page_id']] = pages[['page_id']].astype(int)
# the links are a bit trickier becaue the 'toid' column contains NaN values, which cannot be cast to int.
# So we'll replace them with -1 here, and replace those with Null again in PostGIS later
links[['toid']] = links[['toid']].fillna(-1.0).astype(int)

# the pages dataframe did have one dublicates for me (no idea why), and this one didn't solve it:
# pages.drop_duplicates()
# so I had to go into the CSV and delete the line after export, otherwise it causes a hiccup in the DB import

pages.to_csv('/Volumes/Solid Guy/CPT Python Data/pages_processed.csv', escapechar='\\', encoding='utf-8', index=False)
links.to_csv('/Volumes/Solid Guy/CPT Python Data/links_processed.csv', escapechar='\\', encoding='utf-8', index=False)

# ... or write them directly to the DB:

# this requires some cleanup afterwards, so I did it the CSV way

# engine = create_engine('postgresql://localhost:5432/cpt')
# pages.to_sql('pages', engine)
# links.to_sql('links', engine)

print 'Good night'
