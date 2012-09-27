'''
Created on Dec 13, 2011

@author: reza
'''
import os
import gzip

from common import FOLDER_AVG, FOLDER_TRIALS
from params import NUM_TRIALS

def compute_all():
    processed_bases = []
    for (dirpath, dirname, filenames) in os.walk(FOLDER_TRIALS): #@UnusedVariable
        for filename in filenames:
            filename = filename.replace('.gz', '') # remove .gz extension
            filename = filename.replace('.txt', '') # remove .txt extension
            if filename.rfind('-') >= 0:
                filename = filename[:filename.rfind('-')] # remove trial
            basename = filename
            if basename not in processed_bases:
                processed_bases.append(basename)
                compute_average(basename)
        break
    

def compute_average(basename):
    print 'Processing %s...' % basename
    
    favg = open('%s/%s.txt' % (FOLDER_AVG, basename), 'w')
    
    table = {}
    table_count = {}
    
    num_existing = 0
    for t in range(NUM_TRIALS):
        datafile = '%s/%s-%d.txt' % (FOLDER_TRIALS, basename, t)
        datafile_gz = datafile + '.gz'
#        print 'Reading values from %s' % datafile
        try:
            if os.path.isfile(datafile_gz):
                f = gzip.open(datafile_gz, 'r')
            else:
                f = open(datafile, 'r')
            
            for line in f:
                line_stripped = line.rstrip()
                two_values = line_stripped.split()
                if len(two_values) != 2:
                    print 'file %s, bad line: %s' % (datafile, line)
                key = int(two_values[0])
                value = float(two_values[1])
                table[key] = table.get(key, 0) + value
                table_count[key] = table_count.get(key, 0) + 1
            num_existing += 1
        except IOError as e: #@UnusedVariable
            print "Couldn't read from %s" % datafile

    keylist = table.keys()
    keylist.sort()
    for key in keylist:
        favg.write('%d %f\n' % (key, float(table[key]) / table_count[key])) 

    favg.close()
    
if __name__ == '__main__':
    
    compute_all()
    
#    for alg in ['td']:
#        for game in ['nohitgammon']:
#            for graph in ['base', 'base-0back']:
#                basename = '%s-%s-graph-%s' % (alg, game, graph)
#                compute_average(basename)

#    for alg in ['rl']:
#        for game in ['midgammon']:
#            for graph in ['base']:
#                for ergo in ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']:
#                    for exp in ['back', 'hit']:
#                        basename = '%s-%s-graph-%s-%s%s' % (alg, game, graph, ergo, exp)
#                        compute_average(basename)

#        for game in ['minigammon']:
#            for graph in ['base']:
#                for ergo in ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']:
#                    basename = '%s-%s-graph-%s-ergo%s' % (alg, game, graph, ergo)
#                    compute_average(basename)

#    for alg in ['td']:
#        for game in ['midgammon']:
#            for graph in ['d4s8']:
#                for ergo in ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100']:
#                    basename = '%s-%s-graph-%s-ergo%s' % (alg, game, graph, ergo)
#                    compute_average(basename)

#    for alg in ['td', 'hc', 'hc-challenge']:
#        for game in ['minigammon', 'nannon']:
#            for p in ['1.00', '0.75', '0.50', '0.25', '0.00']:
#                basename = '%s-%s-p-%s' % (alg, game, p)
#                compute_average(basename)
#            for offset in ['0', '1', '2', '3', '4', '5', '6']:
#                basename = '%s-%s-offset-%s' % (alg, game, offset)
#                compute_average(basename)
