SELECT DISTINCT ON (l.from)  
       l.from, l.to, l.mentions, l.linkid, l.line_geom
FROM links l, centers_de c1, centers_de c2
WHERE l.from = c1.city
AND c1.type > 1
AND l.to = c2.city
AND c2.type = 1
ORDER BY l.from, l.mentions DESC ;