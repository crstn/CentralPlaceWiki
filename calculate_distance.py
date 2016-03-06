import pandas as pd
from geopy.distance import great_circle
# from sqlalchemy import create_engine

geotags = pd.read_csv('/Volumes/Solid Guy/CPT Python Data/geo_tag.csv', escapechar='\\', encoding='utf-8')

print 'Geotagged pages loaded, links are next...'

links = pd.read_csv('/Volumes/Solid Guy/CPT Python Data/links.csv', escapechar='\\', encoding='utf-8')

print 'Links loaded, housekeeping'

links.drop('toid', axis=1, inplace=True)
links.drop('id', axis=1, inplace=True)

print 'Copying part of table for self-join'

right = links[['fromid','from']]

print 'Housekeeping...'
right = right.drop_duplicates()


right.rename(columns={'fromid': 'toid', 'from': 'to'}, inplace=True)
# right.to_csv('/Volumes/Solid Guy/CPT Python Data/uniqueArticles.csv', escapechar='\\', encoding='utf-8')

# left join to find the IDs of all 'linked-to' pages
print 'Performing self-join'
links = pd.merge(left=links, right=right, how='left', on='to')


# links.info()
# print geotags
# print links


print 'Performing another left join to get the FROM lats and lons'
geotags.rename(columns={'gt_lat': 'from_lat', 'gt_lon': 'from_lon'}, inplace=True)
links = pd.merge(left=links, right=geotags, how='left', left_on='fromid', right_on='gt_page_id')

links.drop(['gt_name', 'gt_type', 'gt_country', 'gt_region', 'gt_page_id'], axis=1, inplace=True)

# print links

print 'And another one to get the TO lats and lons'
geotags.rename(columns={'from_lat': 'to_lat', 'from_lon': 'to_lon'}, inplace=True)

links = pd.merge(left=links, right=geotags, how='left', left_on='toid', right_on='gt_page_id')
links.drop(['gt_name', 'gt_type', 'gt_country', 'gt_region', 'gt_page_id'], axis=1, inplace=True)

# print links

print "Calculating distance for all linked pairs of pages where both pages have geotags. This will take a while."

links["dist_sphere_meters"] = map(lambda fromlat, fromlon, tolat, tolon: great_circle((fromlat, fromlon), (tolat, tolon)).meters, links["from_lat"], links["from_lon"], links["to_lat"], links["to_lon"])

# print links


links.drop(['total_references'], axis=1, inplace=True)
print links


print 'Final join to have all pages in one table later.'

geotags.rename(columns={'to_lat': 'lat', 'to_lon': 'lon', 'gt_page_id': 'page_id', 'gt_type': 'type', 'gt_country': 'country', 'gt_region': 'region'}, inplace=True)
right.rename(columns={'toid': 'page_id', 'to': 'page'}, inplace=True)

# right.info()
# geotags.info()

pages = pd.merge(left=right, right=geotags, how='outer', on='page_id')


pages[['page_id']] = pages[['page_id']].astype(int)
links[['toid']] = links[['toid']].fillna(-1.0).astype(int)

pages.to_csv('/Volumes/Solid Guy/CPT Python Data/pages_processed.csv', escapechar='\\', encoding='utf-8', index=False)
links.to_csv('/Volumes/Solid Guy/CPT Python Data/links_processed.csv', escapechar='\\', encoding='utf-8', index=False)

print "That's all, folks."

# this requires some cleanup afterwards, so I did it the CSV way

# engine = create_engine('postgresql://localhost:5432/cpt')
# pages.to_sql('pages', engine)
# links.to_sql('links', engine)
