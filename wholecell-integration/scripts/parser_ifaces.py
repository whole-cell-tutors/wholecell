import csv
import os
from collections import defaultdict

class Model:

    def __init__(self, name, ronly, readwrite, req):
        self.name = name
        self.ronly = ronly
        self.readwrite = readwrite
        self.req = req
        self.all_vars = set.union(ronly, readwrite, req)


class Entry:

    def __init__(self, vid, proc_perms):
        self.vid = vid
        self.proc_perms = proc_perms


class ProcPerms:

    def __init__(self, pid, perm):
        self.pid = pid
        self.perm = perm

        
def build_model(fns, proc_name):
    ronly = []
    readwrite = []
    require = []

    for fn in fns:
        with open(fn) as fin:
            iface_reader = csv.reader(fin, delimiter="\t")
            for entry in iface_reader:
                vid, name, ro, rw, req = entry
                if req=='x':
                    require.append(vid)
                elif rw=='x':
                    readwrite.append(vid)
                elif ro=='x':
                    ronly.append(vid)

                    
    return Model(proc_name, set(ronly), set(readwrite), set(require))


def get_process_name(fn):
    f = os.path.basename(fn).split(".")[0]
    return f.split('_')[-1]

def is_process_file(fn):
    return (len(fn.split('_')) > 3)

def build_all_models(directory):
    models = []
    
    proc_files = defaultdict(list)
    for fn in os.listdir(directory):
        if os.path.basename(fn).endswith(".csv") and is_process_file(fn):
            pname = get_process_name(fn)
            proc_files[pname].append(fn)

    for proc_name, proc_fns in proc_files.iteritems():
        models.append(build_model(proc_fns, proc_name))
                
    return models


def get_uniq_ids(models):
    ids = [m.all_vars for m in models]
    return set.union(*ids)


def get_proc_perms(uid, models):
    proc_perms = []
    for m in models:
        if uid in m.req:
            proc_perms.append(ProcPerms(m.name, "req"))
        elif uid in m.readwrite:
            proc_perms.append(ProcPerms(m.name, "rw"))
        elif uid in m.ronly:
            proc_perms.append(ProcPerms(m.name, "ro"))

    return proc_perms
        

def build_entries(models):
    entries = []
    all_ids = get_uniq_ids(models)

    for uid in all_ids:
        proc_perms = get_proc_perms(uid, models)
        entries.append(Entry(uid, proc_perms))

    return entries


def main_test():
    return build_model(["Molecules_names_Metabolite_Metabolism.csv"], "Metabolism")
    
