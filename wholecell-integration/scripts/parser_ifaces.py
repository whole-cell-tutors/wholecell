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

    def __init__(self, vid, proc_perms, vtype, comp):
        self.vid = vid
        self.proc_perms = proc_perms
        self.vtype = vtype
        self.comp = comp
        

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
            print fn
            iface_reader = csv.reader(fin, delimiter=";")
            next(iface_reader, None)
            for entry in iface_reader:
                print entry
                vid, name, ro, rw, req = 5*[""]
                if "Metabolites" in fn:
                    vid, rw, ro, rw, req = entry
                else:
                    vid, name, ro, rw = entry

                if req=='x':
                    require.append(vid)
                elif rw=='x':
                    readwrite.append(vid)
                    
                if ro=='x':
                    ronly.append(vid)

    return Model(proc_name, set(ronly), set(readwrite), set(require))


def get_process_name(fn):
    f = os.path.basename(fn).split(".")[0]
    return f.split('_')[-1]


def build_all_models(directory):
    models = []
    
    proc_files = defaultdict(list)
    pnames = os.listdir(directory)
    for pn in pnames:
        pf = os.path.join(directory, pn)
        for fn in os.listdir(pf):
            if fn.endswith(".csv"):
                proc_files[pn].append(os.path.join(pf, fn))

    for proc_name, proc_fns in proc_files.iteritems():
        models.append(build_model(proc_fns, proc_name))
                    
                
    return models


def build_all_models1(directory):
    models = []
    
    proc_files = defaultdict(list)
    for fn in os.listdir(directory):
        f = os.path.join(directory, fn)
        if f.endswith(".csv"):
            pname = get_process_name(fn)
            proc_files[pname].append(f)

    for proc_name, proc_fns in proc_files.iteritems():
        models.append(build_model(proc_fns, proc_name))
                
    return models


def get_uniq_ids(models):
    ids = [m.all_vars for m in models]
    return set.union(*ids)


def get_proc_perms(uid, models):
    proc_perms = []
    for m in models:
        if uid in set.intersection(m.req, m.ronly):
            proc_perms.append(ProcPerms(m.name, "roreq"))
        elif uid in m.req:
            proc_perms.append(ProcPerms(m.name, "req"))
        elif uid in m.readwrite:
            proc_perms.append(ProcPerms(m.name, "rw"))
        elif uid in m.ronly:
            proc_perms.append(ProcPerms(m.name, "ro"))

    return proc_perms


def get_type(uid, species, params):
    typ = ""
    if uid in species:
        typ = "species"
    elif uid in params:
        typ = "param"

    return typ


def get_vars_types(d):
    species = []
    params = []
    
    for fn in os.listdir(d):
        full_fn = os.path.join(d, fn)
        print full_fn
        fin = open(full_fn)
        fin.readline()
        
        if "Parameters" in  fn:
            reader = csv.reader(open(full_fn), delimiter=";")
            next(reader, None)
            for entry in reader:
                if len(entry) > 0: params.append(entry[0])
        elif fn.startswith("Molecules"):
            reader = csv.reader(open(full_fn), delimiter=";")
            next(reader, None)
            for entry in reader:
                if len(entry) > 0: species.append(entry[0])
        

    return set(species), set(params)


def get_comp(uid):
    parts = uid.split("__")
    if len(parts) > 1:
        return uid.split("__")[1]

    return ''


def get_compartment(uid):
    comp = "Cytosol"

    if get_comp(uid) == "e":
        comp = "Extracellular"
    elif get_comp(uid) == "m":
        comp = "Membrane"

    return comp


def build_entries(models, species, params):
    entries = []
    all_ids = get_uniq_ids(models)

    for uid in all_ids:
        proc_perms = get_proc_perms(uid, models)
        vtype = get_type(uid, species, params)
        comp = get_compartment(uid)
        entries.append(Entry(uid, proc_perms, vtype, comp))
        
    return entries


def write_entries(entries, fn):
    with open(fn, "w") as fout:
        for entry in entries:
            e = []
            e.append(entry.vtype)
            e.append(entry.vid)
            for proc_perm in entry.proc_perms:
                e.append(proc_perm.pid + "(" + proc_perm.perm + ")")

            fout.write(",".join(e))
            fout.write("\n")

            
def main_test():
    return build_model(["Molecules_names_Metabolite_Metabolism.csv"],
        "Metabolism", ",")
    
