## SED-ML generation script
This folder contains files required for generating a top level scheduler for
the whole-cell model. This scheduler consists in a SED-ML file synchronizing
submodels together and a SBML file keeping track of the global variables.

To execute the script, open a command prompt and type:
```python
python sedml_gen.py
```

The produced SED-ML file synchronizes the subprocesses with the top-level
initialization file by using ```setValue``` nodes in the main loop; at the
beginning of each iteration, variables are updated following an order dictated
by the nature of each variable (read-only, read-write, and / or requirement).
The script requires both [libSBML](http://sbml.org/Software/libSBML) and
[libSEDML](https://github.com/fbergmann/libSEDML) Python wrappers to be
installed.

Inputs can be changed by editing the following variables in the script:
* 'model_files': a list of paths to SBML files
* 'io_location': path to a folder containing interface files
* 'delimiter': what delimiter should be used for parsing the interface files
* 'out_sed': where to write the resulting SED-ML file
* 'out_ini': where to write the resulting SBML initialization file

The current version of the script is set for processing the files in the
```test_case_1``` folder.

### What remains to be done
- [x] generate the SBML initialization model
- [ ] generate the SED-ML scheduler file
 - [x] schedule the subprocesses
 - [ ] synchronize the subprocesses through the initialization file
   - [x] global variables are updated after the requirement ('req') variables
   - [x] global variables are updated after the read-write ('rw') variables
   - [ ] local read-only variables ('ro') are updated
   - [ ] local read-write variables ('rw') are updated
   - [ ] local requirement variables ('req') are updated
