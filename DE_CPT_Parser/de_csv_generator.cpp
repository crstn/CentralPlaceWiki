/*	Title: de_csv_generator.cpp
*	Author: Michael Garod
*	Date: 11/3/15
*	Description: Read a collection of text files (source text of DE Lists of
*		Central	Places) and outputs into a CSV by "place;state;center"
*	Note: Text files were obtained manually. They were manually preprocessed to
*		eliminate unnecessary lines (those before, and after the tables).
*	Input: source_list.txt via commandline (This calls the 13 German files)
*	Output: de_central_places.csv, errorlog.txt
*	Usage: <Program Name> <Source List File>
*/
#include <iostream>
#include <fstream>
#include <iterator>
#include <string>
#include <exception>
using namespace std;

// Deletes the last 4 characters of any string. Used to remove ".txt".
string deleteExtension(string str){
	if (str.length() < 4){
		throw 1;
	}

	for (int i = 4; i > 0; --i){
		str.erase(str.end()-1);
	}
	return str;
}

/* Gets the Center which can be: {Oberzentren, Mittelzentren mit oberzentralen
/	Teilfunktionen, Mittelzentren...}
/	PRECONDITION: Title line is of the form "== Center =="
*/
string extractCenter(string str){
	// Remove equal sign and whitespace from beginning
	while(str[0] == '=' || str[0] == ' '){
		str.erase(str.begin());
	}
	// Remove equal sign and whitespace from end
	while(str[str.length()-1] == '=' || str[str.length()-1] == ' '){
		str.erase(str.end()-1);
	}
	return str;
}

/* If str contains a '/' or '\' then merely announce that this must be
/	handled individually.
*/
bool containsSlash(string str){
	if (str.find('/') < string::npos || str.find('\\') < string::npos){
		return true;
	}
	return false;
}

/* Gets the PageTitle from within "| [[PageTitle|DisplayText]]"
/	PRECONDITION: PageTitle is of the form "[[PageTitle]]"
/	or "[[PageTitle|DisplayText]]"
*/
string extractPlace(string str){
	// Remove "| [[" from beginning
	while (str[0] == '|' || str[0] == ' ' || str[0] == '['){
		str.erase(str.begin());
	}
	// Case "[[PageTitle]]", delete all after the first close bracket (']')	
	// Note: If str.find() fails, it returns string::npos (string max)
	if (str.find(']') < string::npos){
		str.erase(str.find(']'));
	}
	// Case: "[[PageTitle|DisplayTest]]", delete all after v-bar ('|')
	if(str.find('|') < string::npos){
		str.erase(str.find('|'));
	}
	
	// Case: Line contains a '}'. These occur due to improper wiki formatting.
	if(str.find('}') < string::npos){
		str.erase(str.find('}'));
	}

	if(str.length() <= 1)
	{
		//cout << "Got a string with 1 or less chars: " << str << endl;
		//cout << "  It has length: " << str.length() << endl;
		return "";
	}

	return str;
}

int main(int argc, char** argv){

	if(argc != 2){
		cout << "Usage: " << argv[0] << " <Source List File>\n";
		return 1;
	}

	ifstream listfile(argv[1]);
	ofstream errorfile("errorlog.txt");
	string filename;

	ofstream csvfile("de_central_places.csv");
	csvfile << "place;state;center\n";

	// Loop through every wikipedia file in your list file
	// BEGIN FILE
	while (listfile >> filename){

		ifstream wikifile(filename);
		string state = deleteExtension(filename);

		string line;
		string center;
		// BEGIN LINE
		while (getline(wikifile, line)){
			// Case: Section/Table title "== Oberzentren =="
			if(line[0] == '='){
				center = extractCenter(line);
			}
			/* Case: At beginning of a newline in the table means that the
			/	following line will contain a place name.
			*/
			else if(line[0] == '|' && line[1] == '-'){
				getline(wikifile, line);
				
				if(!containsSlash(line)){
					string place = extractPlace(line);
				/* Due to improper wiki formatting sometimes, the page contains
				/	a close bracket ('}') directly after a new line. We catch
				/	these because we always assume that the first line after
				/	a new line will contain a place name. We simply don't print
				/	these lines with nothing in them.
				*/
					if(place.length() > 1){
						csvfile <<place<<";"<<state<<";"<<center<<endl;
					}
					else{
						cout << "ERROR: Place with 0 chars\n";
						cout << place << ";" << state << ";" << center << endl;
					}
				}
				else if(containsSlash(line)){
					errorfile << ";" << state << ";" << center << ";" << line << endl;
					continue;
				}
				else{
					/*	if line[0] == '!', do nothing
					/	if line[0] == '{', do nothing
					*/
				}
			}// END LINE
		}// END WIKI FILE
	}// END LIST FILE




	return 0;
}