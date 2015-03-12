#!/usr/bin/python

from libsbml import *
import sys, getopt, subprocess, os


def check(value, message=None):
	"""If 'value' is None, prints an error message constructed using
	'message' and then exits with status code 1. If 'value' is an integer,
	it assumes it is a libSBML return status code. If the code value is
	LIBSBML_OPERATION_SUCCESS, returns without further action; if it is not,
	prints an error message constructed using 'message' along with text from
	libSBML explaining the meaning of the code, and exits with status code 1.
	"""
	if value == None:
		print('LibSBML returned a null value trying to ' + str(message) + '.')
		print('Exiting.')
		sys.exit(1)
	elif type(value) is int:
		if value == LIBSBML_OPERATION_SUCCESS:
			if message:
				print message + '...'
		else:
			print('Error encountered at ' + str(message) + '.')
			print('LibSBML returned error code ' + str(value) + ': "' \
			+ OperationReturnValue_toString(value).strip() + '"')
			print('Exiting.')
			sys.exit(1)
	else:
		if message:
			print message

def createSpecies(model,wid,com):
	s = model.createSpecies()
	check(s)
	check(s.setId(wid))
	check(s.setCompartment(com))
	check(s.setConstant(False))
	check(s.setInitialAmount(0))
	check(s.setSubstanceUnits('mole'))
	check(s.setBoundaryCondition(False))
	check(s.setHasOnlySubstanceUnits(False))
	return s

def createParameter(model,wid,value=0,SBO=''):
	p = model.createParameter()
	check(p)
	check(p.setId(wid))
	check(p.setConstant(False))
	check(p.setValue(value))
	if SBO != '':
		check(p.setSBOTerm(SBO))
	return p

def createPort(model,wid,direction):
	mcomp = model.getPlugin("comp")
	p = mcomp.createPort()
	check(p)
	check(p.setId(direction+'__'+wid))
	check(p.setIdRef(wid))
	if direction == 'input':
		check(p.setSBOTerm('SBO:0000600'))
	else:
		check(p.setSBOTerm('SBO:0000601'))
	return p

def createReplacedElement(obj,portRef,modelRef):
	oplugin = obj.getPlugin("comp")
	re = oplugin.createReplacedElement()
	check(re)
	check(re.setSubmodelRef(modelRef))
	check(re.setPortRef(portRef))
	return re

def createEvent(model,wid):
	e = model.createEvent()
	check(e)
	check(e.setId(wid))
	check(e.setUseValuesFromTriggerTime(False))
	check(e.setSBOTerm('SBO:0000591'))
	return e

def createSubmodel(mplugin,wid,ref,name):
	submodel = mplugin.createSubmodel()
	check(submodel.setId(wid))
	check(submodel.setName(name))
	check(submodel.setModelRef(ref))
	return submodel

#MAIN ---------------------------------------------------------------------------------
 
def main(argv):

	submodels_file = ''
	interface_file = ''
	outputfile = ''
	usestring = 'Usage: ./top_model_generator.py -s <list of submodels files> -i <interface> -o <outputfile>'

#Options treatment --------------------------------------------------------------------

	try:
		opts, args = getopt.getopt(argv,"hs:i:o:",["submodels=","interface=","output="])
	except getopt.GetoptError:
		print usestring
	for opt, arg in opts:
		if opt == '-h':
			print usestring
			sys.exit()
		elif opt in ("-s","--submodels"):
			submodels_file = arg
		elif opt in ("-i","--interface"):
			interface_file = arg
		elif opt in ("-o","--output"):
			outputfile = arg
	if submodels_file=='' or interface_file=='' or outputfile=='':
		print 'Error - Check if all the parameters were set'
		print usestring
		sys.exit()

	
#Creating SBML ----------------------------------------------------------------

	print 'Starting SBML module...'
	try:
		sbmlns = SBMLNamespaces(3,1,"comp",1);
		document = SBMLDocument(sbmlns)
		document.enablePackage("http://www.sbml.org/sbml/level3/version1/comp/version1", "comp", True)
		document.setPackageRequired('comp',True)
	except ValueError:
		print('Error - Could not create SBMLDocumention object')
		sys.exit(1)

	model = document.createModel("TopModel")
	check(model, 'Creating model')
	check(model.enablePackage("http://www.sbml.org/sbml/level3/version1/comp/version1", "comp", True))
	
	compartments = ['c','d','e','m','tc','tm']
	for com in compartments:
		compartment = model.createCompartment()
		compartment.setId(com)
		compartment.setConstant(True)
		compartment.setSize(1)
	
	
#Read input files -------------------------------------------------------------
	
	print "Reading input files..."
	interfaces_id = {}
	f_interface = open(interface_file)
	for line in f_interface.readlines():
		line = line.replace('\n','').split(',')
		interfaces_id[line[0]] = {}
		for i in range(1,len(line)):
			proc_txt = line[i].split('(')
			interfaces_id[line[0]][proc_txt[0]] = proc_txt[1].replace(')','')
	f_interface.close()


	sub_models_id = []
	f_submodels = open(submodels_file)
	for line in f_submodels.readlines():
		sub_models_id.append(line.replace('\n',''))
	f_submodels.close()
	
#Create external Models References ----------------------------------------
	
	print "Creating external model definitions of submodels..."
	requirement_con = 'requirement'
	sharedVar_con = 'sharedVariables'
	connection_submodels_names=[requirement_con,sharedVar_con]
	n_of_submodels=26
	sbmlplugin = document.getPlugin("comp")

	for sub_file in sub_models_id:
		#Create External Model
		ext_model = sbmlplugin.createExternalModelDefinition()
		check(ext_model.setSource(sub_file))
		check(ext_model.setId(sub_file.replace('.xml','')))

	print "Creating external model definitions of connection submodels..."
	for cname in connection_submodels_names:
		for i in range(2,n_of_submodels):
			#Create External Model
			ext_model = sbmlplugin.createExternalModelDefinition()
			check(ext_model.setSource(cname+'_'+str(i)+'.xml'))
			check(ext_model.setId(cname+'_'+str(i)))


#Instantiate submodels ---------------------------------------------------

	print "Instantiating submodels..."
	mplugin = model.getPlugin("comp")
	subModelcount = 1
	modelRef = {}
	for sub_file in sub_models_id:
		#Create Submodel
		submodel = mplugin.createSubmodel()
		createSubmodel(mplugin,'subModel'+str(subModelcount),sub_file.replace('.xml',''),sub_file.replace('.xml',''))
		compartments = ['c','d','e','m','tc','tm']
		for com in compartments:
			compartment = model.getCompartment(com)
			createReplacedElement(compartment,'output__'+com,'subModel'+str(subModelcount))
		modelRef[sub_file.replace('.xml','')] = 'subModel'+str(subModelcount)
		subModelcount+=1	

		
#Create interface ------------------------------------------------------------
	print "Creating interfaces..."
	for key in interfaces_id:
		sp_compartment = 'c'
		for com in compartments:
			if '__'+com+'__' in key:
				sp_compartment = com
				break
		s = createSpecies(model,key,sp_compartment)
		conCounts={}
		conCounts['ro'] = 0
		conCounts['rw'] = 0
		conCounts['req'] = 0
		conCounts['roreq'] = 0
		for key2 in interfaces_id[key]:
			conCounts[interfaces_id[key][key2]]+=1

		checkFlag = 0
		#Create requirements
		if conCounts['req']+conCounts['roreq'] > 1:
			checkFlag += 1
			req_con_name = requirement_con+'_'+str(conCounts['req']+conCounts['roreq'])
			createSubmodel(mplugin,'subModel'+str(subModelcount),req_con_name,req_con_name)
			compartment = model.getCompartment(sp_compartment)
			createReplacedElement(compartment,'output__'+sp_compartment,'subModel'+str(subModelcount))
			reqPort = createReplacedElement(s,'output__Metabolite','subModel'+str(subModelcount))
			compartment = model.getCompartment(com)
			createReplacedElement(compartment,'output__'+com,'subModel'+str(subModelcount))
			subModelcount+=1
			req_count = 1
			for key2 in interfaces_id[key]:
				if interfaces_id[key][key2]=='req' or interfaces_id[key][key2]=='roreq':
					sr = createSpecies(model,key+'_for_'+key2,sp_compartment)
					reqPort = createReplacedElement(sr,'output__Metabolite_'+str(req_count),'subModel'+str(subModelcount-1))
					reqPort = createReplacedElement(sr,'output__'+key,modelRef[key2])
					pr = createParameter(model,key+'_req_'+key2)
					reqPort = createReplacedElement(pr,'input__Req_'+str(req_count),'subModel'+str(subModelcount-1))
					reqPort = createReplacedElement(pr,'output__'+key+'_requirement',modelRef[key2])
					req_count+=1
					

		#Create variable share
		if conCounts['req']+conCounts['roreq'] <= 1 and conCounts['req']+conCounts['roreq']+conCounts['rw']>=2:
			checkFlag += 1
			share_con_name = sharedVar_con+'_'+str(conCounts['req']+conCounts['roreq']+conCounts['rw'])
			createSubmodel(mplugin,'subModel'+str(subModelcount),share_con_name,share_con_name)
			compartment = model.getCompartment(sp_compartment)
			createReplacedElement(compartment,'output__'+sp_compartment,'subModel'+str(subModelcount))
			reqPort = createReplacedElement(s,'output__S','subModel'+str(subModelcount))
			subModelcount+=1
			shareCount = 1
			for key2 in interfaces_id[key]:
				if interfaces_id[key][key2]=='req' or interfaces_id[key][key2]=='roreq' or interfaces_id[key][key2]=='rw':
					ss = createSpecies(model,key+'_from_'+key2,sp_compartment)
					reqPort = createReplacedElement(ss,'output__S'+str(shareCount),'subModel'+str(subModelcount-1))
					reqPort = createReplacedElement(ss,'output__'+key,modelRef[key2])
					shareCount+=1

		#Create variable read onlys
		if conCounts['ro'] or conCounts['roreq']+conCounts['rw']+conCounts['req']==1:
			checkFlag += 1
			for key2 in interfaces_id[key]:
				if interfaces_id[key][key2]=='ro' or interfaces_id[key][key2]=='roreq' or interfaces_id[key][key2]=='rw':
					reqPort = createReplacedElement(s,'output__'+key,modelRef[key2])

		if not checkFlag:
			print "Error: No ports were created for "+key+"."
			sys.exit(1)

#Writing SMBL to file ---------------------------------------------------------

	print "Writing top-level model to file " +outputfile+ "..."
	try:
		writeSBMLToFile(document,outputfile)
	except ValueError:
		print "Error - Can\'t write SBML document to the file " +outputfile+"."
		sys.exit(1)

	print "Done."
#	
#	
	
if __name__ == '__main__':
	main(sys.argv[1:])
	
	
	
