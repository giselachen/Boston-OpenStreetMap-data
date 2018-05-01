# imports
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

def is_tourism(elem):
    """This function takes an element and returns whether it contains an attrib key
    'tourism'.

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    return (elem.attrib["k"] == "tourism")

def audit_tourism(filename):
    """This function takes an osm file and add leisure values into a default dict.

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    osmfile = open(filename, "r")
    tourism_types = defaultdict(int)
    for event, elem in ET.iterparse(osmfile, events = ("start",)):
        for tag in elem.iter("tag"):
            if is_tourism(tag):
                tourism_types[tag.attrib["v"]] += 1

    osmfile.close()
    return tourism_types

tourism_audit = audit_tourism("boston_massachusetts.osm")

print "types of tourism: ", len(tourism_audit)
print "---------------------------------------------------------------------------------"
pprint.pprint(dict(tourism_audit))
