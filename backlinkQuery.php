<?php
/*
Implement:
	recusive backlinkQuery to 6 levels
	eliminate cycles in the search graph
	ORIGIN as command line parameter
 */

// Bump up the memory a bit
ini_set('memory_limit', '256M');

// Change ORIGIN to inspect a different place	
define('ORIGIN', "Rego Park");
$depth = 0;
$depthlimit = 2;
$visited = array();		// will not BL recur if it has already been done
$TODOqueue = array();

// Time Logging
$starttime = microtime(true);

// Setting the curl options for the initial query
	$ch = curl_init();
	// Setting true returns the query as a string (default is to print/echo)
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	// Identify yourself to Wikipedia. May need to provide email later.
	curl_setopt($ch, CURLOPT_USERAGENT, "CUNY Hunter College");

// Making a file for outputting. Will overwrite any pre-existing file.
	$filename = str_replace(array(" ","'","\""), array("_","\'","\\\""), ORIGIN);
	$outputhandle = fopen($filename."_bl_results.csv", "w");
	// Write the CSV header
	fwrite($outputhandle, '"origin","pageid","title","depth"'."\n");

// Begin recursion
$TODOqueue[ORIGIN] = $depth;

	while($depth <= $depthlimit)
	{
		foreach ($TODOqueue as $key => $value)
		{

			executeBLQ($ch, $key, $value, $outputhandle, $TODOqueue);
			unset($TODOqueue[$key]);
		}
		$depth++;
	}

/*
	foreach(array_combine(array_keys($TODOqueue), $TODOqueue)
			 as $page => $depth)
		{
			echo $page."\n";
			echo $depth."\n";
		}
*/


// Time Logging and cleanup
	curl_close($ch);
	fclose($outputhandle);
	$endtime = microtime(true);
	echo "Completion time: ".($endtime - $starttime)."\n";

/*** FUNCTIONS ***/
//
function executeBLQ($ch, $pagename, $depth, $outputhandle, &$TODOqueue)
{
// Make the API call
	$query = backlinkQuery($pagename);
	$childdepth = $depth + 1;
	// Setting the API Call. Will return as JSON
	curl_setopt($ch, CURLOPT_URL, $query);
	// json_decode(true) returns the JSON API Call as an associative array
	$response = json_decode(curl_exec($ch), true);
	echo "in execeuteBLQ: $pagename at depth $depth\n";


// Does the initial query exceed 500 results? If yes, we will loop.
	if (isset($response["query-continue"]["backlinks"]["blcontinue"]))
	{	// Get the next continue code and generate the query
		$continue = $response["query-continue"]["backlinks"]["blcontinue"];
		$query = backlinkQueryContinue($pagename, $continue);

		while (isset($continue)) {
		echo "Current continue code: ".$continue."\n";
		// Run the next API Call including the continue code
		curl_setopt($ch, CURLOPT_URL,$query.$continue);
		$response = json_decode(curl_exec($ch), true);

		// Prepare the next continue code and its query
		if (isset($response["query-continue"]["backlinks"]["blcontinue"])) {	
			$continue = $response["query-continue"]["backlinks"]["blcontinue"];
			$query = backlinkQueryContinue($pagename, $continue);
		}
		else{	// While() break condition: This query had <= 500 results
			unset($continue);
		}

		// Append the response to the output CSV file:
		foreach($response["query"]["backlinks"] as $entry){				
			fwrite($outputhandle, '"'.ORIGIN.
				                  '",'.$entry["pageid"].
				                  ',"'.$entry["title"].
				                  '",'.$childdepth."\n");
			// Add all children to the $TODOqueue
			$title = $entry["title"];
			$TODOqueue[$title] = $childdepth;
		}
		// Do not rapidly bombard Wikipedia or they will ban your IP
		sleep (1);
		}
	}
	else // If no continue, record results
	{
		foreach($response["query"]["backlinks"] as $entry){				
			fwrite($outputhandle, '"'.ORIGIN.
				                  '",'.$entry["pageid"].
				                  ',"'.$entry["title"].
				                  '",'.$childdepth."\n");
			// Add all children to the $TODOqueue
			$title = $entry["title"];
			$TODOqueue[$title] = $childdepth;
		}
		sleep (1);
	}	
}

// Generates the backlink query for $title
function backlinkQuery($title)
{	
	$title = symbolToCode($title);
	$API = "http://en.wikipedia.org/w/api.php?";
	$q = "action=query&list=backlinks&format=json&bltitle=".$title."&blnamespace=0&bllimit=500";
	return $API.$q;
}

// Generates the backlink query for $title with $continue code
function backlinkQueryContinue($title, $continue)
{	
	$title = symbolToCode($title);
	$continue = symbolToCode($continue);
	$API = "http://en.wikipedia.org/w/api.php?";
	$q = "action=query&list=backlinks&format=json&bltitle=".$title."&blcontinue=".$continue."&blnamespace=0&bllimit=500";
	return $API.$q;
}

// Converts human language into the requisite Wiki language for the query
function symbolToCode($title)
{
	$search  = array(' ', '|');
	$replace = array('%20', '%7C');
	return(str_replace($search, $replace, $title));
}

/*** END FUNCTIONS ***/

?>