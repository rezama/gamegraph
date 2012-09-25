'''
Created on Sep 21, 2012

@author: reza
'''
from common import FILE_CONDOR_PLAN, FILE_PLOT_PLAN
from params import NUM_TRIALS
import domain_proxy

def queue_job(f, args):
    args_no_space = args.replace('app_', '').replace('.py', '').\
                replace(' ', '-').replace('--', '-').replace('--', '-')
    f.write('arguments = %s\n' % args) 
    f.write('stdout = ../log/%s\n' % args_no_space)
    f.write('stderr = ../log/%s\n' % args_no_space)
    f.write('queue\n')

def plot_them(f, plot_items):
    plot_name = plot_items[0]
    if plot_name.rfind('-') >= 0:
        plot_name = plot_name[:plot_name.rfind('-')] # remove last token
    
    f.write('set output "./plots/%s.eps"\n' % plot_name)
    for i in range(len(plot_items)):
        segments = plot_items[i].split('-')
        item_title = segments[len(segments) - 2] + ' ' + segments[len(segments) - 1]
        if i == 0:
            f.write('plot ')
        else:
            f.write('     ')
        f.write('"../data/avg/%s.txt" using 1:2 with lines title "%s"' %
                (plot_items[i], item_title))
        if i == len(plot_items) - 1:
            f.write('\n\n')
        else:
            f.write(', \\\n')

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

    fp = open(FILE_PLOT_PLAN, 'w')
    fp.write('set terminal postscript eps color\n')
    fp.write('')

    
    for app in ['app_sarsa', 'app_ntd', 'app_hc']:
        for domain in ['minigammon', 'nannon', 'midgammon', 'nohitgammon']:
            state_class = domain_proxy.DomainProxy.load_domain_state_class_by_name(domain)
            domain_full = state_class.get_domain_signature()
            
            plot_items = []
            for offset in [0, 1, 2, 3]:
                plot_item = '%s-%s-offset-%d' % (app.replace('app_', ''), domain_full, offset)
                plot_items.append(plot_item)
                for trial in range(NUM_TRIALS):
                    args = '%s.py --domain %s --offset %d --trial %d' % (app, domain, offset, trial)
                    queue_job(f, args)
            plot_them(fp, plot_items)

            plot_items = []
            for chooseroll in ['0.0', '0.1', '0.5', '0.9', '1.0']:
                plot_item = '%s-%s-chooseroll-%s' % (app.replace('app_', ''), domain_full, chooseroll)
                plot_items.append(plot_item)
                for trial in range(NUM_TRIALS):
                    args = '%s.py --domain %s --chooseroll %s --trial %d' % (app, domain, chooseroll, trial)
                    queue_job(f, args)
            plot_them(fp, plot_items)

    f.close()
    fp.close()