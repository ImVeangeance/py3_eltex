import json
import sys


class DumpLog:
    """Class for collecting data from .log file"""
    def __init__(self, destination, protocol, age, metric):
        """Constructor for basic data"""
        self.destination = destination
        self.protocol = protocol.strip('*[]')
        self.preference = int(protocol.split('/')[1].strip(']'))
        self.age = age[:-1]
        self.metric = int(metric)
        self.next_hop = []
        self.via = []

    def addition(self, next_hop, via):
        """Method for list-type data to collect all log from file"""
        self.next_hop.append(next_hop)
        self.via.append(via)

    def map_out(self, key):
        """json-like output for map"""
        third_dict = {}
        if len(self.next_hop) == 2:
            if self.next_hop[0] == key:
                third_dict = {"preference": self.preference, "age": self.age, "metric": self.metric, "via": self.via[0]}
            elif self.next_hop[1] == key:
                third_dict = {"preference": self.preference, "age": self.age, "metric": self.metric, "via": self.via[1]}
        else:
            third_dict = {"preference": self.preference, "age": self.age, "metric": self.metric, "via": self.via[0]}
        return third_dict


def parsing(collection_sample, file_name):
    """Log-file parsing, loading in memory string-by-string to avoid memory overload due to potential file size"""
    file_open = open(file_name, 'r')
    for line in file_open:
        parse = line.split()
        if parse[-2] != "via":
            if len(parse) == 6:
                collection_sample.append(DumpLog(parse[0], parse[1], parse[-4] + " " + parse[-3], parse[-1]))
            else:
                collection_sample.append(DumpLog(parse[0], parse[1], parse[-3], parse[-1]))
        else:
            collection_sample[-1].addition(parse[-3], parse[-1])
    file_open.close()


def to_sec_dict(collection_sample, elem_index, key):
    """Dictionary collecting for better json usage, because its works only with
    default python collections, ads second map to first
    Map view: keys -> 'destination', values -> other data"""
    sec_dict = {}
    for index in range(0, len(collection_sample)):
        for str_point in range(0, len(collection_sample[index].next_hop)):
            if collection_sample[index].next_hop[str_point] == collection_sample[elem_index].next_hop[0]:
                sec_dict[collection_sample[index].destination] = collection_sample[index].map_out(key)
    return sec_dict


def to_first_dict(diction, dump):
    """Creating first map, keys -> 'next_hop', values -> 'destination's"""
    for i in range(0, len(dump)):
        for j in range(0, len(dump[i].next_hop)):
            diction[dump[i].next_hop[j]] = to_sec_dict(dump, i, dump[i].next_hop[j])


if "__main__" == __name__:
    try:
        dump_coll = []
        parsing(dump_coll, sys.argv[1])
        try:
            dictionary = {}
            to_first_dict(dictionary, dump_coll)
            r_t = {"route_table": {"next_hop": dictionary}}
            file_out = open(sys.argv[-1], 'w')
            json.dump(r_t, file_out, indent=2)
            file_out.close()
        except IOError:
            print("'Out' file name does not wrote!")
    except IOError:
        print("Incorrect file name or file is not in the current directory!")
