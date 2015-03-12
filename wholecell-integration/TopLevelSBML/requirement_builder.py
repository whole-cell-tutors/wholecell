from libsbml import *

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
#-------------------------------------------------------------------------------

def createSpecies(model,wid):
	s = model.createSpecies()
	check(s)
	check(s.setId(wid))
	check(s.setCompartment('c'))
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

def createEvent(model,wid):
	e = model.createEvent()
	check(e)
	check(e.setId(wid))
	check(e.setUseValuesFromTriggerTime(False))
	check(e.setSBOTerm('SBO:0000591'))
	return e

def createTrigger(event):
	t = event.createTrigger()
	check(t)
	check(t.setPersistent(False))
	check(t.setInitialValue(False))
	return t

#Creating SBML ----------------------------------------------------------------
def createRequirementSBML(n):

	print 'Starting SBML module...'
	try:
		sbmlns = SBMLNamespaces(3,1,"comp",1);
		document = SBMLDocument(sbmlns)
		document.enablePackage("http://www.sbml.org/sbml/level3/version1/comp/version1", "comp", True)
		document.setPackageRequired('comp',True)
	except ValueError:
		print('Error - Could not create SBMLDocumention object')
		sys.exit(1)

	model = document.createModel("Requirement"+str(n))
	check(model, 'Creating model')
	check(model.enablePackage("http://www.sbml.org/sbml/level3/version1/comp/version1", "comp", True))

	compartment = model.createCompartment()
	compartment.setId("c")
	compartment.setConstant(True)
	compartment.setSize(1)

	#Creating species, parameters and ports
	for i in range(n):
		createSpecies(model,'Metabolite_'+str(i+1))
		createParameter(model,'Req_'+str(i+1))
		createPort(model,'Metabolite_'+str(i+1),'output')
		createPort(model,'Req_'+str(i+1),'input')
	createParameter(model,'p0',value=1,SBO='SBO:0000593')
	createParameter(model,'p1',SBO='SBO:0000593')
	createSpecies(model,'Metabolite')
	createPort(modelRef,'Metabolite','output')
	createPort(model,'c','input')

	#Creating events

	#t0
	t0 = createEvent(model,'t0')
	trig = createTrigger(t0)
	math = parseFormula('and(true,eq(p0,1))')
	trig.setMath(math)
	
	met_sum = '(Metabolite_1'
	for i in range(2,n+1):
		met_sum+='+Metabolite_'+str(i)
	met_sum+=')'
	req_sum = '(Req_1'
	for i in range(2,n+1):
		req_sum+='+Req_'+str(i)
	req_sum+=')'
	for i in range(n):
		evAss = t0.createEventAssignment()
		evAss.setVariable('Metabolite_'+str(i+1))
		math ='floor('
		math += met_sum
		math += '*('
		math += 'Req_'+str(i+1)+'/'
		math += req_sum
		math += '))'
		math = parseFormula(math)
		evAss.setMath(math)
	
	evAss = t0.createEventAssignment()
	evAss.setVariable('Metabolite')
	evAss.setMath(parseFormula(met_sum))

	evAss = t0.createEventAssignment()
	evAss.setVariable('p0')
	evAss.setMath(parseFormula('0'))

	evAss = t0.createEventAssignment()
	evAss.setVariable('p1')
	evAss.setMath(parseFormula('1'))

	#t1
	t1 = createEvent(model,'t1')
	trig = createTrigger(t1)
	math = parseFormula('eq(p1,1)')
	trig.setMath(math)

	delay = t1.createDelay()
	delay.setMath(parseFormula('0'))

	evAss = t1.createEventAssignment()
	evAss.setVariable('p1')
	evAss.setMath(parseFormula('0'))

	evAss = t1.createEventAssignment()
	evAss.setVariable('p0')
	evAss.setMath(parseFormula('1'))

		
		
	

	#Writing SMBL to file ---------------------------------------------------------

	print "Writing requirement model to file requirement_" +str(n)+ ".xml ..."
	try:
		writeSBMLToFile(document,'requirement_'+str(n)+'.xml')
	except ValueError:
		print "Error - Can\'t write SBML document to the file requirement_" +str(n)+ ".xml ."
		sys.exit(1)



#MAIN ---------------------------------------------------------------------------------
 
def main(argv):

	for i in range(2,27):
		createRequirementSBML(i)	
	
if __name__ == '__main__':
	main(sys.argv[1:])
	

