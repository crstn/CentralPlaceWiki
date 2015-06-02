<?php
/*	Usage:
	php backlinkQuery.php (string) (int)

	string will be ORIGIN
	int will be depthlimit
*/
// Bump up the memory a bit
ini_set('memory_limit', '256M');

if(!isset($argv[1]) || !isset($argv[2]))
{
	echo "Missing arguments\n";
	exit(1);
}

// Change second argument to inspect a different place (global constant)	
define('ORIGIN', $argv[1]);
$depth = 0;
$depthlimit = $argv[2];
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
	fwrite($outputhandle, '"origin","pageid","title","depth","parent"'."\n");

// Begin search for N generations of children
// Items in the queue are pairs where Key==Title => Value==Depth
	$TODOqueue[ORIGIN] = $depth;

	while($depth <= $depthlimit)
	{
		$remaining = count($TODOqueue);
		foreach ($TODOqueue as $key => $value)
		{
		// If not yet visited, then executeBLQ() (eliminates cycles in graph)
			if(!isset($visited[$key]))
			{
				echo "Executing: $key at depth $value\n";
				executeBLQ($ch, $key, $value, $outputhandle, $TODOqueue);
				$visited[$key] = $value;
			}
			else
			{
				echo "Already visited $key\n";
			}

			unset($TODOqueue[$key]);
			echo "Items remaining at this depth: ".--$remaining."\n";
		}
		$depth++;
		
	}

// Time Logging and cleanup
	curl_close($ch);
	fclose($outputhandle);
	$endtime = microtime(true);
	echo "Completion time: ".($endtime - $starttime)."\n";

/*** FUNCTIONS ***/
// Runs make the API call(s) and records all results to a CSV file
function executeBLQ($ch, $pagename, $parentdepth, $outputhandle, &$TODOqueue)
{
	// Make the API call
	$query = makeBLQ($pagename);
	$childdepth = $parentdepth + 1;
	// Setting the API Call. Will return as JSON
	curl_setopt($ch, CURLOPT_URL, $query);
	// json_decode(true) returns the JSON API Call as an associative array
	$response = json_decode(curl_exec($ch), true);
	
	// Does the initial query exceed 500 results? If yes, we will loop.
	if (isset($response["query-continue"]["backlinks"]["blcontinue"]))
	{	// Get the next continue code and generate the query
		$continue = $response["query-continue"]["backlinks"]["blcontinue"];
		$query = makeBLQContinue($pagename, $continue);

		while (isset($continue)) {
		echo "Current continue code: ".$continue."\n";
		// Run the next API Call including the continue code
		curl_setopt($ch, CURLOPT_URL,$query.$continue);
		$response = json_decode(curl_exec($ch), true);

		// Prepare the next continue code and its query
		if (isset($response["query-continue"]["backlinks"]["blcontinue"])) {	
			$continue = $response["query-continue"]["backlinks"]["blcontinue"];
			$query = makeBLQContinue($pagename, $continue);
		}
		else{	// While() break condition: The last query had <=500 results
			unset($continue);
		}

		// Append the response to the output CSV file:
		foreach($response["query"]["backlinks"] as $entry){				
			fwrite($outputhandle, '"'.ORIGIN.
				                  '",'.$entry["pageid"].
				                  ',"'.$entry["title"].
				                  '",'.$childdepth.
				                  ',"'.$pagename.'"'."\n");
			// Add all children to the $TODOqueue
			$title = $entry["title"];
			$TODOqueue[$title] = $childdepth;
		}
		// Do not rapidly bombard Wikipedia or they will ban your IP
		sleep (1);
		}
	}
	 // If initial query has <=500 results, simply record results
	else
	{
		foreach($response["query"]["backlinks"] as $entry){				
			fwrite($outputhandle, '"'.ORIGIN.
				                  '",'.$entry["pageid"].
				                  ',"'.$entry["title"].
				                  '",'.$childdepth.
				                  ',"'.$pagename.'"'."\n");
			// Add all children to the $TODOqueue
			$title = $entry["title"];
			$TODOqueue[$title] = $childdepth;
		}
		sleep (1);
	}	
}

// Generates the backlink query for $title
function makeBLQ($title)
{	
	$title = symbolToCode($title);
	$API = "http://en.wikipedia.org/w/api.php?";
	$q = "action=query&list=backlinks&format=json&bltitle=".$title."&blnamespace=0&bllimit=500";
	return $API.$q;
}

// Generates the backlink query for $title with $continue code
function makeBLQContinue($title, $continue)
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
	return str_replace($search, $replace, $title);
}

/*** END FUNCTIONS ***/

?>