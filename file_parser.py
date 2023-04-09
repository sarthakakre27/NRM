import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt

def atoi(s):
    i, base, sign = 0, 0, 1
     
    # handle the case where s contains no digits (or input is malformed)
    if not (set(s) & set('0123456789')):
      return 0
     
    # increment past whitespace (ignore)
    while s[i] == ' ':
        i += 1
     
    # compute sign (2s complement)
    if s[i] == '-' or s[i] == '+':
        sign = 1 - 2 * (s[i] == '-')
        i += 1
 
    # loop as long as the next input is a digit
    while i < len(s) and '0' <= s[i] <= '9':
               
        # test for overflow
        if (base > (sys.maxsize // 10) or
           (base == (sys.maxsize // 10) and
           (ord(s[i]) - ord('0')) > 7)):
           
          # clamp to +/- maxsize
          if sign == 1:
            return sys.maxsize
          else:
            return -(sys.maxsize) - 1
         
        base = 10 * base
        base += (ord(s[i]) - ord('0'))
        i += 1
     
    return base * sign

def parseFileGraphCreation(input_file):
    G = nx.DiGraph()
    node=dict()
    source=('\0','-1')
    # open the file in read mode
    with open(input_file, 'r') as f:
        # read the file line by line
        for line in f:
            # split the line by space
            line = line.split()

            # print the line
            # print(line,'aaaa')

            # G.add_node((line[0], atoi(line[1])))
            node[line[0]]=line[1]
    f.close()

    with open(input_file, 'r') as f:

        for line in f:
            # split the line by space
            line = line.split()

            # print the line
            # print(line,'bbbb')

            if(atoi(node[line[0]])==0):
               source=(line[0],0)

            for i in range(2,len(line)):
                G.add_edge((line[0],atoi(node[line[0]])),(line[i],atoi(node[line[i]])))     

    f.close()

    # print(list(G.nodes(data=True)))
    # nx.draw(G,with_labels=True)
    # plt.show()

    return [G,source]  
            

            
































if __name__ == '__main__':
    # take input file name from user in argument
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input file name")
    args = parser.parse_args()
    input_file = args.input_file

    # function call to parse the file
    G = nx.DiGraph()
    G = parseFileGraphCreation(input_file)
    # parse_file('data.txt')