#!/usr/bin/env python
# coding=utf-8

# Python script for generating the master SED-ML file for the wholecell model
# @author Bertrand Moreau, Argyris Zardilis, Chris J. Myers, Paulo Burke, Thawfeek Varusai, Tobias Czauderna
import libsbml, libsedml
import parser_ifaces as ifaces

# Required inputs
model_files = ['toymodel1.xml', 'toymodel2.xml', 'toymodel3.xml']
io_location = '.'
out_sed = 'scheduler.xml'
out_ini = 'init.xml'

# write initialization SBML file
def write_init_file(mods, loc):
  sbml_doc = libsbml.SBMLDocument(3, 1)
  sb_mod = sbml_doc.createModel('global')
  # read interfaces
  for i in ifaces.get_uniq_ids(mods):
    par = sb_mod.createParameter()
    par.setId(str(i))
    par.setValue(0.0)
  sbml_writer = libsbml.SBMLWriter()
  sbml_writer.writeSBMLToFile(sbml_doc, loc)

# create stepper simulation
def add_sim(doc):
  sim = libsedml.SedOneStep(1, 2)
  sim.setId('stepper')
  sim.setStep(1.0)
  alg = libsedml.SedAlgorithm(1, 2)
  alg.setKisaoID('KISAO:0000032')
  sim.setAlgorithm(alg)
  doc.addSimulation(sim)

# add initialization model and its associated task
def add_init_model(doc, init_file):
  ini = libsedml.SedModel(1, 2)
  ini_id = init_file.rstrip('.xml')
  ini.setId(ini_id)
  ini.setLanguage('urn:sedml:language:sbml')
  ini.setSource(init_file)
  doc.addModel(ini)
  # create its associated task
  ini_tsk = libsedml.SedTask(1, 2)
  ini_tsk.setId('task_' + ini_id)
  ini_tsk.setSimulationReference('stepper')
  ini_tsk.setModelReference(ini_id)
  doc.addTask(ini_tsk)

# populate list of models & tasks
def add_models(doc, files):
  for m in files:
    mod = libsedml.SedModel(1, 2)
    m_id = m.rstrip('.xml')
    mod.setId(m_id)
    mod.setLanguage('urn:sedml:language:sbml')
    mod.setSource(str(m))
    doc.addModel(mod)
    # one task per model
    tsk = libsedml.SedTask(1, 2)
    tsk.setId('task_' + m_id)
    tsk.setSimulationReference('stepper')
    tsk.setModelReference(m_id)
    doc.addTask(tsk)

# build the main repeatedTask node
def build_loop(doc, entries):
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
  for t in doc.getListOfTasks():
    sub = libsedml.SedSubTask(1, 2)
    sub.setTask(t.getId())
    rpt.addSubTask(sub)
  # changes
  # updating the global state
  # 'req' case first
  for e in entries:
    req_lst = []
    for p in e.proc_perms:
      if p.perm == 'req':
        # create a SedVariable pointing to the entry id in the current process
        var = libsedml.SedVariable(1, 2)
        var.setId(str(e.vid) + '_' + str(p.pid) + '_req')
        tgt = "/sbml:sbml/sbml:model[@id='"  + str(p.pid) + "']/sbml:listOfSpecies/sbml:species[@id='" + str(e.vid) + "']"
        var.setTarget(str(tgt))
        var.setModelReference(str(p.pid))
        req_lst.append(var)
    if len(req_lst) > 0:
      sv = libsedml.SedSetValue(1, 2)
      sv.setModelReference('init')
      sv.setTarget("/sbml:sbml/sbml:model[@id='init']/sbml:listOfParameters/sbml:parameter[@id='" + str(e.vid) + "']/@value")
      # build mathML expression
      math = str()
      for v in req_lst:
        sv.addVariable(v)
        math += str(v.getId()) + "+"
      sv.setMath(libsbml.parseL3Formula(math.rstrip("+")))
      rpt.addTaskChange(sv)
  # 'rw' case second
  for e in entries:
    rw_lst = []
    for p in e.proc_perms:
      if p.perm == 'req':
        # create a SedVariable pointing to the entry id in the current process
        var = libsedml.SedVariable(1, 2)
        var.setId(str(e.vid) + '_' + str(p.pid) + '_rw')
        tgt = str("/sbml:sbml/sbml:model[@id='"  + str(p.pid) + "']/sbml:listOfSpecies/sbml:species[@id='" + str(e.vid) + "']")
        var.setTarget(str(tgt))
        var.setModelReference(str(p.pid))
        rw_lst.append(var)
    if len(rw_lst) > 0:
      # create setValue node
      sv = libsedml.SedSetValue(1, 2)
      sv.setModelReference('init')
      sv.setTarget(str("/sbml:sbml/sbml:model[@id='init']/sbml:listOfParameters/sbml:parameter[@id='" + str(e.vid) + "']/@value"))
      # original value of the target is a variable too
      var = libsedml.SedVariable(1, 2)
      tgt_id = str(e.vid) + '_init_global'
      var.setId(tgt_id)
      tgt = str("/sbml:sbml/sbml:model[@id='init']/sbml:listOfParameters/sbml:parameter[@id='" + str(e.vid) + "']/@value")
      var.setTarget(str(tgt))
      var.setModelReference('init')
      sv.addVariable(var)
      # build mathML expression
      math = tgt_id + '+'
      for v in rw_lst:
        sv.addVariable(v)
        math += '(' + str(v.getId()) + '-' + tgt_id + ')+'
      sv.setMath(libsbml.parseL3Formula(math.rstrip('+')))
      rpt.addTaskChange(sv)
  # assigning the local variables
  doc.addTask(rpt)

# write SED-ML scheduler file
def write_scheduler_file(init_file, loc, files, entries):
  sed_doc = libsedml.SedDocument(1, 2)
  add_sim(sed_doc)
  add_init_model(sed_doc, init_file)
  add_models(sed_doc, files)
  build_loop(sed_doc, entries)
  # writing generated file
  sed_writer = libsedml.SedWriter()
  sed_writer.writeSedMLToFile(sed_doc, loc)

mods = ifaces.build_all_models(io_location)
write_init_file(mods, out_ini)
entries = ifaces.build_entries(mods)
write_scheduler_file(out_ini, out_sed, model_files, entries)
