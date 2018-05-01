# imports
import xml.etree.cElementTree as ET
import re
import pprint
from collections import defaultdict

# set up re to find street types
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# assemble a list of expected street names
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Terrace", "Way"]


def audit_street_type(street_types, street_name):
    """This function takes in a defaultdict(set) and street name in the value attribute of
    the address tag, check the last word and if it's an unexpected name for a street name
    in the address it adds it into the defaultdict

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    match = street_type_re.search(street_name)
    if match:
        street_type = match.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    """This function takes an element and returns whether it contains an attrib key
    'addr:street'.

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    return (elem.attrib["k"] == "addr:street") or (elem.attrib["k"] == "addr:street_1")

def audit_street(filename):
    """This function takes an osm file and add unusual street type names in to the
    returned defaultdict(set).

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    osmfile = open(filename, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osmfile, events = ("start",)):
        for tag in elem.iter("tag"):
            if is_street_name(tag):
                audit_street_type(street_types, tag.attrib["v"])
    osmfile.close()
    return street_types

street_name_audit = audit_street("boston_massachusetts.osm")

print "number of street names that might need revision: ", len(street_name_audit)
print "---------------------------------------------------------"
pprint.pprint(dict(street_name_audit))
