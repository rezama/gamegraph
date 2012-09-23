'''
Created on Sep 21, 2012

@author: reza
'''
from common import FILE_CONDOR_PLAN
from params import NUM_TRIALS

def queue_job(f, args):
    args_no_space = args.replace('app_', '').replace('.py', '').\
                replace(' ', '-').replace('--', '-').replace('--', '-')
    f.write('arguments = %s\n' % args) 
    f.write('stdout = ../log/%s\n' % args_no_space)
    f.write('stderr = ../log/%s\n' % args_no_space)
    f.write('queue\n')
    

if __name__ == '__main__':

    f = open(FILE_CONDOR_PLAN, 'w')
    f.write('+Group = "GRAD"\n')
    f.write('+Project = "AI_ROBOTICS"\n')
    f.write('+ProjectDescription = "Studying impact of domain ergodicity on reinforcement learning and self-play"\n')
    f.write('\n')
    f.write('universe = vanilla\n')
    f.write('executable = /usr/bin/python\n')
    f.write('getenv = true\n')
    f.write('transfer_executable = false\n')  
    f.write('\n')
    
    for app in ['app_sarsa', 'app_ntd', 'app_hc']:
        for domain in ['minigammon', 'nannon', 'midgammon', 'nohitgammon']:
            for offset in [0, 1, 2, 3]:
                for trial in range(NUM_TRIALS):
                    args = '%s.py --domain %s --offset %d --trial %d' % (app, domain, offset, trial)
                    queue_job(f, args)
            for chooseroll in ['0.0', '0.1', '0.5', '0.9', '1.0']:
                for trial in range(NUM_TRIALS):
                    args = '%s.py --domain %s --chooseroll %s --trial %d' % (app, domain, chooseroll, trial)
                    queue_job(f, args)

    f.close()