import os

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc

    reference: http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

print "boston_massachusetts.osm: " +  convert_bytes(os.path.getsize('boston_massachusetts.osm'))
print "small_sample.osm: " + convert_bytes(os.path.getsize('small_sample.osm'))
print "nodes.csv: " + convert_bytes(os.path.getsize('nodes.csv'))
print "nodes_tags.csv: " + convert_bytes(os.path.getsize('nodes_tags.csv'))
print "ways.csv: " + convert_bytes(os.path.getsize('ways.csv'))
print "ways_tags.csv: " + convert_bytes(os.path.getsize('ways_tags.csv'))
print "ways_nodes.csv: " + convert_bytes(os.path.getsize('ways_nodes.csv'))
