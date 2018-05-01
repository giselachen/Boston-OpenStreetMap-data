# check for potential problems in the tags

import re
import xml.etree.cElementTree as ET
import pprint

# use re to categorize tags
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(elem, keys):
    """This function takes in an element in a xml file and catalog the <tag> subelement into the following four
    categories using regulare xpression:
    "lower", for tags that contain only lowercase letters and are valid,
    "lower_colon", for otherwise valid tags with a colon in their names,
    "problemchars", for tags with problematic characters, and
    "other", for other tags that do not fall into the other three categories.

    It returns the count in the first element of the value in the list and a set of examples in the second element
    of the list.

    This is an modified version of the code from
    https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54456296460923#"""

    if elem.tag == "tag":

        # look for key tags that are all lower cases
        if lower.match(elem.attrib["k"]):
            keys["lower"][0] += 1
            keys["lower"][1].add(elem.attrib["k"])

        # look for key tags that are lower cases separated with a colon
        elif lower_colon.match(elem.attrib["k"]):
            keys["lower_colon"][0] += 1
            keys["lower_colon"][1].add(elem.attrib["k"])

        # look for key tags that have problematic characters
        elif problemchars.match(elem.attrib["k"]):
            keys["problemchars"][0] += 1
            keys["problemchars"][1].add(elem.attrib['k'])

        # all other key tags
        else:
            keys["other"][0] += 1
            keys['other'][1].add(elem.attrib['k'])
    return keys



def process_map(filename):
    """This function takes an osm file in xml format and counts the number of the tags classified in the
    key_type function using iterparse and store examples in a set.
    It returns the information in a dictionary with the categories as the key and the count as value[0] and
    exmples as as set in value[1]

    It's a modified version of codes from
    https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54456296460923#"""

    keys = {"lower": [0, set()], "lower_colon": [0, set()], "problemchars": [0, set()], "other": [0, set()]}
    for _, elem in ET.iterparse(filename):
        keys = key_type(elem, keys)

    return keys

tag_survey = process_map('boston_massachusetts.osm')

for key in tag_survey:
    print key, ": ", tag_survey[key][0]

print "-------------------------------------------"
for key in tag_survey:
    if key not in "problemchars":
        print key, " examples: "
        pprint.pprint(tag_survey[key][1])
        print "--------------------------------------------------------------------------------"
