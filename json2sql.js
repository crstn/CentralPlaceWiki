var fs = require('fs'),
    JSONStream = require('JSONStream');

var stream = fs.createReadStream('wikidata-20151102-all.json', {encoding: 'utf8'}),
    parser = JSONStream.parse('*');

function escapeSlashes( str ) {
    return str.replace(/'/g, "''");
}

parser.on('data', function (obj) {
    // create insert statements for every wikidata item that has coordinates (property P625, see https://www.wikidata.org/wiki/Property:P625)
    if(obj.claims["P625"]){
        p625 = obj.claims["P625"];
        if(p625[0].mainsnak.datavalue){ // check whether this one actually has coordinates
            loc = p625[0].mainsnak.datavalue.value;
            if(obj.labels["de"] && obj.labels["en"]){
                console.log("INSERT INTO pages VALUES ('"+escapeSlashes(obj.labels["de"]["value"])+"', '"+escapeSlashes(obj.labels["en"]["value"])+"', ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326));")
            } else if(obj.labels["de"]){ // in case there is only a english label
                console.log("INSERT INTO pages VALUES ('"+escapeSlashes(obj.labels["de"]["value"])+"', '', ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326));")
            } else  if(obj.labels["en"]){ // in case there is only a german label
                console.log("INSERT INTO pages VALUES ('', '"+escapeSlashes(obj.labels["en"]["value"])+"',  ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326));")
            } // skip if there is no english or german label
        }
    }
});

stream.pipe(parser);
