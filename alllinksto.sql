SELECT "to", SUM(links.links + links.mentions)
FROM links
GROUP BY "to"
LIMIT 10