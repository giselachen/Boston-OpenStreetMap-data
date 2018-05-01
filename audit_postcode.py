# imports
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

def is_postcode(elem):
    """This function takes an element and returns whether it contains an attrib key
    'addr:street'.

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    return (elem.attrib["k"] == "addr:postcode")

def audit_postcode(filename):
    """This function takes an osm file and add unusual street type names in to the
    returned defaultdict(set).

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    osmfile = open(filename, "r")
    postcode_types = defaultdict(int)
    for event, elem in ET.iterparse(osmfile, events = ("start",)):
        for tag in elem.iter("tag"):
            if is_postcode(tag):
                postcode_types[tag.attrib["v"]] += 1

    osmfile.close()
    return postcode_types

postcode_audit = audit_postcode('boston_massachusetts.osm')

print "total number of unique zipcodes: ", len(postcode_audit)
print "---------------------------------------------------------------------------------"
pprint.pprint(dict(postcode_audit))
