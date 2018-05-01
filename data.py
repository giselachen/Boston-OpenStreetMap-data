# imports
import xml.etree.cElementTree as ET
import re
import csv
import codecs
import cerberus

# osm file to be processed
OSM_PATH = "boston_massachusetts.osm"

# set up csv files for export
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# set up re for matching problem characters
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# set up schema for validation
SCHEMA = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# assemble a mappinng dictionary for cleaning street names
mapping = {"Ave": "Avenue", "Ave.": "Avenue", "Ct": "Court", "Dr": "Drive",    "HIghway": "Highway", "Hwy": "Highway", "Pkwy": "Parkway", "Pl": "Place", "place": "Place","Rd": "Road", "rd.": "Road", "Sq.": "Square", "ST": "Street", "St": "Street", "St,": "Street", "St.": "Street", "Street.": "Street", "st": "Street", "street": "Street"}

# helper functions for audit/cleaning tag elements
def is_street_name(elem):
    """This function takes an element and returns whether it contains an attrib key
    'addr:street'.

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    return (elem.attrib["k"] == "addr:street") or (elem.attrib["k"] == "addr:street_1")

def clean_street_name(name, mapping):
    """This function takes a string and a mapping dictionary and return a string of a curated street name
    found in the boston_massachusetts.osm

    This is a modification from
    https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923#"""

    # delete number after street name,
    if "," in name:
        return name.split(",")[0]

    # delete suite number after street and fixed one abbreviated street type
    elif "#" in name:
        if "Harvard" in name:
            return "Harvard Street"
        else:
            name_split_pound = name.split("#")
            return name_split_pound[0]

    # map all street names in question to standard street names
    else:
        name_as_list = name.split(" ")
        if name_as_list[-1] in mapping.keys():
            name_as_list[-1] = mapping[name_as_list[-1]]
            name = " ".join(name_as_list)
            return name
        else:
            return name

def is_postcode(elem):
    """This function takes an element and returns whether it contains an attrib key
    'addr:street'.

    This is an modification from https://classroom.udacity.com/nanodegrees/nd002/parts/0021345404/modules/316820862075461/lessons/5436095827/concepts/54446302850923"""

    return (elem.attrib["k"] == "addr:postcode")

def clean_postcode(postcode):
    """This function takes an string and returns a string of 5 digit postcode in the boston_massachusetts.osm"""

    # delete -XXXX after the five digit postcode
    if "-" in postcode:
        return postcode.split("-")[0]

    # delete MA in the postcodes
    elif "MA" in postcode:
        new_postcode = postcode.replace("MA ", "")
        if len(new_postcode) == 5:
            return new_postcode
        else:
            return "00000"

    # return "00000" for postcodes that are less than 5 digits
    elif len(postcode) < 5:
        return "00000"

    # return "00000" for postcodes that are outside the area
    elif postcode == "01125" or postcode == "20052" or postcode == "01238" or postcode == "01240" or postcode == "01250":
        return "00000"
    else:
        return postcode

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # process node elements
    if element.tag == 'node':

        # first assemble node_attribs
        for field in node_attr_fields:
            node_attribs[field] = element.attrib[field]

        # next process tags associated with the node
        for secondary_tag in element.iter("tag"):

            # skip tags with problem characters
            if problem_chars.match(secondary_tag.attrib["k"]):
                continue
            else:
                tag = {}
                tag_as_list = secondary_tag.attrib["k"].split(":")

                # assign tag type, tag key and tag value
                if len(tag_as_list) == 2:
                    tag["type"] = tag_as_list[0]
                    tag["key"] = tag_as_list[-1]

                    # clean postcode
                    if is_postcode(secondary_tag):
                        tag["value"] = clean_postcode(secondary_tag.attrib["v"])

                    # clean street names
                    elif is_street_name(secondary_tag):
                        tag["value"] = clean_street_name(secondary_tag.attrib["v"], mapping)
                    else:
                        tag["value"] = secondary_tag.attrib["v"]
                elif len(tag_as_list) == 1:
                    tag["type"] = default_tag_type
                    tag["key"] = secondary_tag.attrib["k"]
                    tag["value"] = secondary_tag.attrib["v"]
                else:
                    tag["type"] = tag_as_list[0]
                    tag["key"] = ":".join(tag_as_list[-2:])
                    tag["value"] = secondary_tag.attrib["v"]

                # add tag id to processed tags
                tag["id"] = node_attribs["id"]
                tags.append(tag)
        return {'node': node_attribs, 'node_tags': tags}

    # process way elements
    elif element.tag == 'way':

        # first assemble way attributes
        for field in WAY_FIELDS:
            way_attribs[field] = element.attrib[field]

        # next assign way_nodes relationships
        nd_index = 0
        way_node = {}
        for nd in element.iter("nd"):
            way_node = {"id": None, "node_id": None, "position": None}
            way_node["id"] = way_attribs["id"]
            way_node["node_id"] = nd.attrib["ref"]
            way_node["position"] = nd_index
            nd_index += 1
            way_nodes.append(way_node)

        # next process tags associated with the way
        for secondary_tag in element.iter("tag"):

            # skip tags with problem characters
            if PROBLEMCHARS.match(secondary_tag.attrib["k"]):
                continue
            else:
                tag = {}
                tag_as_list = secondary_tag.attrib["k"].split(":")

                # assign tag type, tag key, tag value
                if len(tag_as_list) == 2:
                    tag["type"] = tag_as_list[0]
                    tag["key"] = tag_as_list[-1]

                    # clean postcode
                    if is_postcode(secondary_tag):
                        tag["value"] = clean_postcode(secondary_tag.attrib["v"])

                    # clean street names
                    elif is_street_name(secondary_tag):
                        tag["value"] = clean_street_name(secondary_tag.attrib["v"], mapping)
                    else:
                        tag["value"] = secondary_tag.attrib["v"]
                elif len(tag_as_list) == 1:
                    tag["type"] = default_tag_type
                    tag["key"] = secondary_tag.attrib["k"]
                    tag["value"] = secondary_tag.attrib["v"]
                else:
                    tag["type"] = tag_as_list[0]
                    tag["key"] = ":".join(tag_as_list[-2:])
                    tag["value"] = secondary_tag.attrib["v"]

                # add tag id to processed tags
                tag["id"] = way_attribs["id"]
                tags.append(tag)
        print tags
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
process_map(OSM_PATH, validate=False)
