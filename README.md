# Text Filter Plugin for SublimeText FilterPipes

This plugin contains a set of text filter commands for SublimeText maintained
largely for my own personal use. This plugin relies on FilterPipes to do all
its heavy lifting.

To use this plugin you must also install FilterPipes, either through
[PackageControl](https://packagecontrol.io) or by downloading it directly
from [github.com/tylerl/FilterPipes](https://github.com/tylerl/FilterPipes).

This plugin defines the following commands:

* **Pretty Print JSON**  
  Parse a chunk of JSON and then dump it back out with formatting.

* **Delete Blank Lines**  
  Yup. Deletes lines which are blank

* **Join lines as List**  
  Creates a JSON-style list with one item per line. Saves you like 10 seconds.

* **Parse URL**  
  Parses a URL using urllib and then dumps the result out as a python dict.
  Turns out to be surprisingly useful with long and complex URLs with a lot of
  query string parameters.

* **UnParse URL**  
  Takes the result of the above command and puts it back into URL form. Turns
  `Parse URL` into a much more powerful *editing* tool rather than just a
  visualization tool.

* **Strip all spaces**  
  Useful in rare occasions.

* **Pack DEFLATE** and **Unpack DEFLATE**  
  Compress and then base-64 encode a block of content. This variant is
  compatible with certain other protocols such as the request encoding in 
  SAML. The "Unpack" command reverse the process.

* **Pack GZip** and **Unpack GZip**  
  Same as above but uses GZip semantics on the compression instead of raw
  DEFLATE. This is the result of what you'd get if you used command-line tools
  like `cat file.txt | gzip | base64`. If you want to pull a file into sublime
  and you you're worried about copy-paste munging something up, then run that
  command from the command line, paste the base64 content into sublime, and then
  use this command to unpack it.

  Note that all the Pack and Unpack commands assume UTF-8 encoding. You can 
  go mess around in filters.py to change that assumption if it matters to you.
