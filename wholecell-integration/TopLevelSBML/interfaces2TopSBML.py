Sfrom libsbml import *
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
#-------------------------------------------------------------------------------

def createSpecies(model,wid,name,compartment):
	s = model.createSpecies()
	check(s)
	check(s.setId(wid))
	check(s.setName(name))
	check(s.setCompartment(compartment))
	check(s.setConstant(False))
	check(s.setInitialAmount(0))
	check(s.setSubstanceUnits('mole'))
	check(s.setBoundaryCondition(False))
	check(s.setHasOnlySubstanceUnits(False))
	return s

#MAIN ---------------------------------------------------------------------------------
 
def main(argv):

	submodels_file = ''
	molecules_file = ''
	outputfile = ''
	usestring = 'Usage: ./top_model_generator.py -s <list of submodels files> -m <list of molecules> -o <outputfile>'

#Options treatment --------------------------------------------------------------------

	try:
		opts, args = getopt.getopt(argv,"hs:m:o:",["submodels=","molecules=","output="])
	except getopt.GetoptError:
		print usestring
	for opt, arg in opts:
		if opt == '-h':
			print usestring
			sys.exit()
		elif opt in ("-s","--submodels"):
			submodels_file = arg
		elif opt in ("-m","--molecules"):
			molecules_file = arg
		elif opt in ("-o","--output"):
			outputfile = arg
	if submodels_file=='' or molecules_file=='' or outputfile=='':
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




#Writing SMBL to file ---------------------------------------------------------

	print "Writing top-level model to file " +outputfile+ "..."
	try:
		writeSBMLToFile(document,outputfile)
	except ValueError:
		print "Error - Can\'t write SBML document to the file " +outputfile+"."
		sys.exit(1)
	
	
	
if __name__ == '__main__':
	main(sys.argv[1:])
	

