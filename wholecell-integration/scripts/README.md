## SED-ML generation script
This folder contains files required for generating a top level scheduler for
the whole-cell model. This scheduler consists in a SED-ML file synchronizing
submodels together and a SBML file keeping track of the global variables.

To execute the script, open a command prompt and type:
```python
python sedml_gen.py
```

The script both [libSBML](http://sbml.org/Software/libSBML) and
[libSEDML](https://github.com/fbergmann/libSEDML) Python wrappers to be
installed.

Inputs can be changed by editing the following variables in the script:
* 'model_files': a list of paths to SBML files (here, those files are
  'toymodel1.xml', 'toymodel2.xml' and 'toymodel3.xml')
* 'io_location': path to a folder containing interface files (here, those files
  'Molecules_names_Metabolites_toymodel1.csv',
  'Molecules_names_Metabolites_toymodel2.csv' and
  'Molecules_names_Metabolites_toymodel3.csv')
* 'out_sed': where to write the resulting SED-ML file (here, 'scheduler.xml')
* 'out_ini': where to write the resulting SBML initialization file (here,
  'init.xml')

### What remains to be done
The resulting SED-ML file synchronizes the subprocesses with the top-level
initialization file by using ```setValue``` nodes in the main loop; at the
beginning of each iteration, variables are updated as follows:
- [x] global variables are updated after the requirement ('req') variables
- [x] global variables are updated after the read-write ('rw') variables
- [ ] local read-only variables ('ro') are updated
- [ ] local read-write variables ('rw') are updated
- [ ] local requirement variables ('req') are updated
