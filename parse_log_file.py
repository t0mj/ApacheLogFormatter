"""
Takes an apache log file and converts it to a dataframe (msgpack) for reporting.

Author: Thomas Johns @t0mj
"""
import argparse
import pandas as pd
import os
import re


# Read Chunk Function - Convert chunk to msg
def parse_log_file(log_file, chunks):
    path, input_file = os.path.split(log_file)
    # Safely create the output file
    if '.log' in input_file:
        output_file = path + input_file.replace('.log', '.msg')
    else:
        output_file = path + input_file + '.msg'
    data_list = []
    with open(input_file) as f:
        for line in f:
            # Get a tuple of the cleaned up record
            clean_line = parse_line(line)
            # Add it to the list in memory for converting to msgpack
            data_list.append(clean_line)
            if len(data_list) == chunks:
                # Once we reach our chunk limit, convert to msgpack
                convert_chunk_to_msgpack(data_list, output_file)
                data_list = []
        if data_list:
            # Get the final chunk if there is one
            convert_chunk_to_msgpack(data_list, output_file)

    print(f'Dataframe created and located at {output_file}')


# Convert chunk to msgpack
def convert_chunk_to_msgpack(data_list, output_file):
    # Our dataframe labels
    labels = ['ip', 'unused', 'user_id', 'datetime', 'request_method', 'resource', 'protocol',
              'status', 'return_size']
    df = pd.DataFrame.from_records(data_list, columns=labels)
    # Remove unused column
    df.drop('unused', axis=1, inplace=True)
    # Change data types
    df[['status', 'return_size']] = df[['status', 'return_size']].apply(pd.to_numeric)
    df.to_msgpack(output_file, append=True)


# Parsing function - clean up lines
def parse_line(line):
    regex = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+)\s?(\S+)?\s?(\S+)?" (\d{3}|-) (\d+|-)\s?'
    return re.match(regex, line).groups()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Takes an apache access log file and creates'
                                                 'a dataframe for reports.')
    parser.add_argument('log_file', help='The apache log file.')
    parser.add_argument('--chunks', default=2000, type=int,
                        help='The number of lines to chunk during dataframe creation.')
    args = vars(parser.parse_args())
    if not any(args.values()):
        parser.error('No arguments provided.')

    parse_log_file(**args)
