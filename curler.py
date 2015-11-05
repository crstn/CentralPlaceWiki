# -*- coding: utf-8 -*-
from lxml import etree        # XML parsing
# encoding=utf8
import sys, os

reload(sys)
sys.setdefaultencoding('utf8')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ns = '{http://www.mediawiki.org/xml/export-0.10/}'

curlfile = open("curl.sh", "a")
infile = "dewiki-20150901-pages-articles1.xml"

# for the parsing, we follow the approach explained here:
# http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
pages = etree.iterparse(infile, events=('end',), tag=ns+'page')

# go through wikipedia pages in dump, one by one:
for event, page in pages:
    title = page.find(ns+'title').text.encode('utf8')
    curlfile.write('curl -L "https://de.wikipedia.org/wiki/'+title+'" > "testpages/'+title+'.html";\n')

curlfile.close()
