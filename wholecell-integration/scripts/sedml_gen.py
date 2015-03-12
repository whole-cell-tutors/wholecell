#!/usr/bin/env python
# coding=utf-8

# Python script for generating the master SED-ML file for the wholecell model
import libsbml, libsedml
import parser_ifaces as ifaces

# Required inputs
model_files = ['toymodel1.xml', 'toymodel2.xml', 'toymodel3.xml']
io_location = '.'
out_sed = 'scheduler.xml'
out_ini = 'init.xml'

# write initialization SBML file
sbml_doc = libsbml.SBMLDocument(3, 1)
sb_mod = sbml_doc.createModel('global')
# read interfaces
mods = ifaces.build_all_models(io_location)
for i in ifaces.get_uniq_ids(mods):
  par = sb_mod.createParameter()
  par.setId(str(i))
  par.setValue(0.0)
sbml_writer = libsbml.SBMLWriter()
sbml_writer.writeSBMLToFile(sbml_doc, out_ini)

# write SED-ML scheduler file
sed_doc = libsedml.SedDocument(1, 2)

# create stepper simulation
sim = libsedml.SedOneStep(1, 2)
sim.setId('stepper')
sim.setStep(1.0)
alg = libsedml.SedAlgorithm(1, 2)
alg.setKisaoID('KISAO:0000032')
sim.setAlgorithm(alg)
sed_doc.addSimulation(sim)

# add initialization model
ini = libsedml.SedModel(1, 2)
ini_id = out_ini.rstrip('.xml')
ini.setId(ini_id)
ini.setLanguage('urn:sedml:language:sbml')
ini.setSource(out_ini)
sed_doc.addModel(ini)
# create its associated task
# should be scheduled at the beginning of the main loop, after setValues happen
ini_tsk = libsedml.SedTask(1, 2)
ini_tsk.setId('task_' + ini_id)
ini_tsk.setSimulationReference('stepper')
ini_tsk.setModelReference(ini_id)
sed_doc.addTask(ini_tsk)

tsk_lst = [] # keeping track of the tasks
# populate list of models & tasks
for m in model_files:
  mod = libsedml.SedModel(1, 2)
  m_id = m.rstrip('.xml')
  mod.setId(m_id)
  mod.setLanguage('urn:sedml:language:sbml')
  mod.setSource(str(m))
  sed_doc.addModel(mod)
  # one task per model
  tsk = libsedml.SedTask(1, 2)
  tsk.setId('task_' + m_id)
  tsk.setSimulationReference('stepper')
  tsk.setModelReference(m_id)
  tsk_lst.append(tsk.getId())
  sed_doc.addTask(tsk)

# building main loop
rpt = libsedml.SedRepeatedTask(1, 2)
rpt.setId('main_loop')
rpt.setResetModel(False)
# range
rng = libsedml.SedUniformRange(1, 2)
rng.setId('schedule')
rng.setStart(0.0)
rng.setEnd(1000.0)
rng.setNumberOfPoints(999)
rng.setType('linear')
rpt.setRangeId(rng.getId())
rpt.addRange(rng)
# subtasks
for t in tsk_lst:
  sub = libsedml.SedSubTask(1, 2)
  sub.setTask(t)
  rpt.addSubTask(sub)
sed_doc.addTask(rpt)

# writing generated file
sed_writer = libsedml.SedWriter()
sed_writer.writeSedMLToFile(sed_doc, out_sed)
