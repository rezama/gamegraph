'''
Created on Dec 13, 2011

@author: reza
'''
from common import NUM_TRIALS

def compute_average(basename):
    print 'Processing %s...' % basename
    
    favg = open('../data/avg/%s.txt' % basename, 'w')
    
    table = {}
    num_existing = 0
    for t in range(NUM_TRIALS):
        datafile = '../data/trials/%s-%d.txt' % (basename, t)

#        print 'Reading values from %s' % datafile
        try:
            f = open(datafile, 'r')
            for line in f:
                line_stripped = line.rstrip()
                two_values = line_stripped.split()
                key = int(two_values[0])
                value = float(two_values[1])
                table[key] = table.get(key, 0) + value
            num_existing += 1
        except IOError as e:
            print "Couldn't read from %s" % datafile

    keylist = table.keys()
    keylist.sort()
    for key in keylist:
        favg.write('%d %f\n' % (key, float(table[key]) / num_existing)) 

    favg.close()
    
if __name__ == '__main__':
#    for alg in ['td', 'hc', 'hc-challenge']:
#        for game in ['minigammon', 'nannon']:
#            for p in ['1.00', '0.75', '0.50', '0.25', '0.00']:
#                basename = '%s-%s-p-%s' % (alg, game, p)
#                compute_average(basename)
#            for offset in ['0', '1', '2', '3', '4', '5', '6']:
#                basename = '%s-%s-offset-%s' % (alg, game, offset)
#                compute_average(basename)
    for alg in ['td']:
        for game in ['midgammon']:
            for graph in ['d4s8']:
                for ergo in ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']:
                    basename = '%s-%s-graph-%s-ergo%s' % (alg, game, graph, ergo)
                    compute_average(basename)
        for game in ['minigammon']:
            for graph in ['base']:
                for ergo in ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']:
                    basename = '%s-%s-graph-%s-ergo%s' % (alg, game, graph, ergo)
                    compute_average(basename)
