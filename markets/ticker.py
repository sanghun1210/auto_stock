import os

ticker_filename = 'ticker_code.txt'

def get_ticker_list():
    with open(os.path.join(os.getcwd(), ticker_filename), 'r') as f:
        list_file = []
        for line in f:
            list_file.append(line)
        return list_file