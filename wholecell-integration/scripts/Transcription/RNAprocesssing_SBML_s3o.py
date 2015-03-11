import pandas as pd
import libsbml
import re


def add_species_by_id(species_id, species_type, model, species_name=" ", compartment='c'):
    if species_id not in SBML_SPECIES:
        species = model.createSpecies()
        species.setId( species_id)
        species.setName( species_name)
        SBML_SPECIES.append(species_id)
        species.setCompartment(compartment)
        if species_type in ENTITY_TO_SBO_MAPPING.keys():
            species.setSBOTerm( ENTITY_TO_SBO_MAPPING[species_type])

def create_compartment(name_of_compartment, model):
    if name_of_compartment:
        if not model.getCompartment(name_of_compartment):
            NEW_COMPARTMENT = model.createCompartment()
            NEW_COMPARTMENT.setId(name_of_compartment)
            NEW_COMPARTMENT.setConstant(True)
            NEW_COMPARTMENT.setSize(1)
            NEW_COMPARTMENT.setUnits('volume')


reactionFile_data = pd.read_csv('Reactions.txt', delimiter='\t')
relevantReactions = reactionFile_data[reactionFile_data['Process'].isin(['Process_RNAModification','Process_RNADecay','Process_RNAProcessing','Process_Transcription' ])]

SBML_SPECIES = []


ENTITY_TO_SBO_MAPPING = {
    "macromolecule" : "SBO:0000245", 
    "nucleicacid" : "SBO:0000354", 
    "simplemolecule" : "SBO:0000247"
}

DOCUMENT = libsbml.SBMLDocument( 2, 4)
MODEL = DOCUMENT.createModel()

create_compartment("c", MODEL)

Process_RNAProcessing_reactions = reactionFile_data[reactionFile_data['Process'].isin(['Process_RNAProcessing'])]

for index, row in Process_RNAProcessing_reactions.iterrows():
	reactants_reaction={}
	products_reaction={}
	modifier_enzyme = row['Enzyme'] 
	reaction_stoich = row['Stoichiometry'].rpartition(':')[-1].strip()
	if "<==>" in reaction_stoich:
		LHS_reaction = reaction_stoich.split('<==>')[0].strip()
		RHS_reaction = reaction_stoich.split('<==>')[1].strip()
	elif "==>" in reaction_stoich:
		reversible = False
		LHS_reaction = reaction_stoich.split('==>')[0].strip()
		RHS_reaction = reaction_stoich.split('==>')[1].strip()
	reactants = [i.strip() for i in LHS_reaction.split('+')]
	products = [i.strip() for i in RHS_reaction.split('+')]
	for i in reactants:
		stoichiometry = 1
		add_reac = i
		if re.search(r"\((.*?)\)",i):
			m = re.search(r"\((.*?)\)",i)
			stoichiometry = int(m.group(1))
			add_reac = re.sub(r'\(.*?\)', '', i).strip()
		if not add_reac in reactants_reaction.keys():
			reactants_reaction[add_reac] = stoichiometry
		else:
			reactants_reaction[add_reac] = reactants_reaction[add_reac] + stoichiometry
	for i in products:
		stoichiometry = 1
		add_prod = i
		if re.search(r"\((.*?)\)",i):
			m = re.search(r"\((.*?)\)",i)
			stoichiometry = int(m.group(1))
			add_prod = re.sub(r'\(.*?\)', '', i).strip()
		if not add_prod in products_reaction.keys():
			products_reaction[add_prod] = stoichiometry
		else:
			products_reaction[add_prod] = products_reaction[add_prod] + stoichiometry

	reaction = MODEL.createReaction()
	reaction.setId(row['ID'])
	reaction.setReversible(False)

	for i in reactants_reaction.keys():
				reactant_ref = reaction.createReactant()
				add_species_by_id(i,'simplemolecule',MODEL,i, 'c')
				reactant_ref.setSpecies(i)
				reactant_ref.setStoichiometry(reactants_reaction[i])

	for i in products_reaction.keys():
				product_ref = reaction.createProduct()
				add_species_by_id(i,'simplemolecule',MODEL,i, 'c')
				product_ref.setSpecies(i)
				product_ref.setStoichiometry(products_reaction[i])	

	mod_ref = reaction.createModifier()
	add_species_by_id(modifier_enzyme,'macromolecule',MODEL,modifier_enzyme, 'c')
	mod_ref.setSpecies(modifier_enzyme)

libsbml.writeSBMLToFile( DOCUMENT, "RNAProcessing_s3o.xml")




	
	

	
	

	
























