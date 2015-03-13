from libsbml import *
import sys


def check(value, message):
   """If 'value' is None, prints an error message constructed using
   'message' and then exits with status code 1.  If 'value' is an integer,
   it assumes it is a libSBML return status code.  If the code value is
   LIBSBML_OPERATION_SUCCESS, returns without further action; if it is not,
   prints an error message constructed using 'message' along with text from
   libSBML explaining the meaning of the code, and exits with status code 1.
   """
   if value == None:
     raise SystemExit('LibSBML returned a null value trying to ' + message + '.')
   elif type(value) is int:
     if value == LIBSBML_OPERATION_SUCCESS:
       return
     else:
       err_msg = 'Error encountered trying to ' + message + '.' \
                 + 'LibSBML returned error code ' + str(value) + ': "' \
                 + OperationReturnValue_toString(value).strip() + '"'
       raise SystemExit(err_msg)
   else:
     return

  
def create_port(model, vid, direction):
    mcomp = model.getPlugin("comp")
    p = mcomp.createPort()
    p.setId(direction + "__" + vid)
    p.setIdRef(vid)

    
def create_param(models, entry):
    for proc_perm in entry.proc_perms:
       print entry.comp
       model = models[proc_perm.pid]
       p = model.createParameter()
       p.setId(entry.vid)
       p.setConstant(True)
       p.setValue(0)
       create_port(model, entry.vid, "output")

        
def create_species(models, entry):
    for proc_perm in entry.proc_perms:
        model = models[proc_perm.pid]
        s = model.createSpecies()
        s.setId(entry.vid)
        s.setConstant(False)
        s.setInitialAmount(0)
        s.setBoundaryCondition(False)
        s.setHasOnlySubstanceUnits(False)
        s.setCompartment(entry.comp)
        if proc_perm.perm == "roreq":
           param = model.createParameter()
           param.setId(entry.vid + "_global")
           param.setConstant(True)
           param.setValue(0)
           create_port(model, entry.vid, "input")
           
           param1 = model.createParameter()
           param1.setId(entry.vid + "_requirement")
           param1.setConstant(False)
           param1.setValue(0)
           create_port(model, entry.vid + "_requirement", "output")
        elif proc_perm.perm == "req":
           create_port(model, entry.vid, "output")
           param1 = model.createParameter()
           param1.setId(entry.vid + "_requirement")
           param1.setConstant(False)
           param1.setValue(0)
           create_port(model, entry.vid + "_requirement", "output")
        elif proc_perm.perm == "rw":
           create_port(model, entry.vid, "output")
        elif proc_perm.perm == "ro":
           create_port(model, entry.vid, "input")

           
def create_compartment(model, comp_name):
    comp = model.createCompartment()
    comp.setId(comp_name)
    comp.setSize(1)
    comp.setSpatialDimensions(3)
    comp.setConstant(True)
   

def create_models():
    proc_names = ['Process1', 'Process2', 'Process3', 'Process4']

    models = {}
    docs = {}
    
    for pname in proc_names:
        try:
            sbmlns = SBMLNamespaces(3,1,"comp",1)
            document = SBMLDocument(sbmlns)
            document.enablePackage("http://www.sbml.org/sbml/level3/version1/comp/version1",
                                   "comp", True)
            document.setPackageRequired('comp',True)
        except ValueError:
            raise SystemExit('Could not create SBMLDocumention object')

        model = document.createModel()
        check(model,                              'create model')
        check(model.enablePackage("http://www.sbml.org/sbml/level3/version1/comp/version1",
                                  "comp", True), "enable package")

        comps = ["Cytosol", "Extracellular", "Membrane"]
        for comp in comps:
           create_compartment(model, comp)
           create_port(model, comp, "output")
        
        models[pname] = model
        docs[pname] = document

    return models, docs

 
def write_docs(docs):
   for pname, doc in docs.iteritems():
      writeSBMLToFile(doc, pname+".xml")
      

def build_model(entries):
    models, docs = create_models()
    
    for entry in entries:
        if entry.vtype == "species":
            create_species(models, entry)
        elif entry.vtype == "param":
            create_param(models, entry)
        elif entry.vtype == "state":
            create_param(models, entry)

    write_docs(docs)

            
    



