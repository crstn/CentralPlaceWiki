var fs = require('fs'),
    JSONStream = require('JSONStream');

var stream = fs.createReadStream('/Users/carsten/wikidata-20151102-all.json', {encoding: 'utf8'}),
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

            labelDE = '""';
            labelEN = '""';

            if(obj.labels["de"]){
                labelDE = escapeSlashes(obj.labels["de"]["value"]);
            }

            if(obj.labels["en"]){
                labelEN = escapeSlashes(obj.labels["en"]["value"]);
            }

            // skip if there is no english or german label
            if((obj.labels["en"] !=  '""') || (obj.labels["en"] !=  '""')){
                console.log("INSERT INTO pages VALUES ('"+labelDE+"', '"+labelEN+"', '', '', ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326), '"+obj.id+"');")

                if(obj.aliases["de"]){
                    for(var alias in obj.aliases["de"]){
                        console.log("INSERT INTO pages VALUES ('"+escapeSlashes(obj.aliases["de"][alias]["value"])+"', '', '"+labelDE+"', '"+labelEN+"',  ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326), '"+obj.id+"');")
                    }
                }


                if(obj.aliases["en"]){
                    for(var alias in obj.aliases["en"]){
                        console.log("INSERT INTO pages VALUES ( '', '"+escapeSlashes(obj.aliases["en"][alias]["value"])+"', '"+labelDE+"', '"+labelEN+"',  ST_SetSRID(ST_MakePoint("+loc.longitude+", "+loc.latitude+"),4326), '"+obj.id+"');")
                    }
                }
            }
        }
    }
});

stream.pipe(parser);
