import pickle

write_file_name = '101010.txt'

def main():
    to_write_file_list = ['aaa','bbb','ccc']
    with open(write_file_name, 'wb') as wf:
        pickle.dump(to_write_file_list, wf)   

    with open(write_file_name, 'rb') as lf:
        readList = pickle.load(lf)
        print(readList) 

if __name__ == "__main__":
    # execute only if run as a script
    main()