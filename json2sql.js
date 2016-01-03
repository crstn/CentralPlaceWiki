var fs = require('fs'),
    JSONStream = require('JSONStream');

var stream = fs.createReadStream('/Volumes/Solid Guy/wikidata-20151102-all.json', {encoding: 'utf8'}),
    parser = JSONStream.parse('*');

function escapeSlashes( str ) {
    return str.replace(/'/g, "''");
}

// keeping track of the previous objects to make sure we don't insert duplicates
prevDE = '';
prevEN = '';
prevLoc = '';

parser.on('data', function (obj) {
    // create insert statements for every wikidata item that has coordinates (property P625, see https://www.wikidata.org/wiki/Property:P625)
    if(obj.claims["P625"]){

        p625 = obj.claims["P625"];
        if(p625[0].mainsnak.datavalue){ // check whether this one actually has coordinates

            loc = p625[0].mainsnak.datavalue.value;

            labelDE = '""';
            labelEN = '""';

            // check the title for the corresponding wiki pages in german and english, see https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#Site_Links

            if(obj.sitelinks.dewiki)
                labelDE = obj.sitelinks.dewiki.title;

            if(obj.sitelinks.enwiki)
                labelEN = obj.sitelinks.enwiki.title;


            // skip if there is no english nor a german label
            // or if the item is the same as the previous one
            if(((labelDE !=  '""') || (labelEN !=  '""')) && ((labelDE != prevDE) || (labelEN != prevEN) || (loc != prevLoc))){
                console.log("INSERT INTO pages VALUES ('"+labelDE+"', '"+labelEN+"', ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326), '"+obj.id+"');")

                prevDE = labelDE;
                prevEN = labelEN;
                prevLoc = loc;

            }

        }
    }
});

stream.pipe(parser);
