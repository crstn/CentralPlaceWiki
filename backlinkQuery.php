<?php
ini_set('memory_limit', '256M');

// Time Logging
$starttime = microtime(true);


// Setting strings for the query
	// $origin = "What links here"
	// Change $origin to inspect a different place
	$origin = "Cold War";
	$query = backlinkQuery($origin);
	$continue = "";


// Setting up curl to the selected query
	$ch = curl_init();
	// Setting the API Call. Will return as JSON
	curl_setopt($ch, CURLOPT_URL, $query);
	// True returns the query as a string (default is to print/echo)
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	// Identify yourself to Wikipedia. May need to provide email as well.
	curl_setopt($ch, CURLOPT_USERAGENT, "CUNY Hunter College");


// Make the API call
	// json_decode(true) returns the JSON API Call as an associative array
	$response = json_decode(curl_exec($ch), true);
	$allresponses = array($response);
	$counter = 0;

	// Opening file for outputting. Will overwrite any pre-existing file.
	$filename = str_replace(array(" ","'","\""), array("_","\'","\\\""),$origin);
	$outputhandle = fopen($filename."_bl_results.JSON", "w");

// Does the initial query exceed 500 results? If yes, we will loop.
	if (isset($response["query-continue"]["backlinks"]["blcontinue"]))
	{	// Get the next continue code and generate the query
		$continue = $response["query-continue"]["backlinks"]["blcontinue"];
		$query = backlinkQueryContinue($origin, $continue);
	}	
	
	while (isset($continue))
	{
		echo "Current continue code: ".$continue."\n";
		// Run the next API Call including the continue code
		curl_setopt($ch, CURLOPT_URL,$query.$continue);
		$response = json_decode(curl_exec($ch), true);

		// Prepare the next continue code and its query
		if (isset($response["query-continue"]["backlinks"]["blcontinue"]))
		{	
			$continue = $response["query-continue"]["backlinks"]["blcontinue"];
			$query = backlinkQueryContinue($origin, $continue);
		}
		else
		{	// Break condition: This query had <= 500 results
			unset($continue);
		}

		// Append the response to $allresponses[]
		$allresponses[] = $response;
		
		// Do not rapidly bombard Wikipedia or they will ban your IP
		sleep (1);

		// Prevents memory overload by writing, then erasing every 10k results
//		$counter++;
//		if ($counter == 20)
//		{
//			echo "Writing to file...\n";
//
//			writeToOutputJSON($allresponses, $origin, $outputhandle);
//			$allresponses = array();
//			$counter = 0;
//		}
	} #END WHILE

// Write any remaining responses to output file
	if(isset($allresponses[0]))
	{	// If exactly 20*n queries, then array[0]==NULL
		// writeToOutputJSON($allresponses, $origin, $outputhandle);	
		fwrite($outputhandle, json_encode($allresponses));
	}

// Time Logging and cleanup
	curl_close($ch);
	$endtime = microtime(true);
	echo "Completion time: ".($endtime - $starttime)."\n";


/*** FUNCTIONS ***/
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
function symbolToCode($origin)
{
	$search  = array(' ', '|');
	$replace = array('%20', '%7C');
	return(str_replace($search, $replace, $origin));
}

// Write all backlinks to a file
//function writeToOutputJSON($allresponses, $origin, $outputhandle)
//{
//	// Manually creating a JSON object
//	// Is there a predefined method for this already?
//	// Need ensure that entry[title]&[origin] characters are properly escaped
//	foreach($allresponses as $response)
//	{
//		foreach($response["query"]["backlinks"] as $entry)
//		{	
//			$insert = "{\"pageid\":".$entry["pageid"].
//						", \"title\":\"".addslashes($entry["title"])."\"".
//						", \"linksto\":\"".$origin."\"}\n";
//			fwrite($outputhandle, $insert);
//		}
//	}
//}

/*** END FUNCTIONS ***/

?>