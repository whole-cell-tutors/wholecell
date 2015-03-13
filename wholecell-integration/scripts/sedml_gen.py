#!/usr/bin/env python
# coding=utf-8

# Python script for generating the master SED-ML file for the wholecell model
import libsbml, libsedml
import os.path
import parser_ifaces as ifaces

# Required inputs
model_files = ['test_case_1/toymodel1.xml',
               'test_case_1/toymodel2.xml',
               'test_case_1/toymodel3.xml']
io_location = 'test_case_1'
delimiter = ','
out_sed = 'test_case_1/scheduler.xml'
out_ini = 'test_case_1/init.xml'

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
def add_init_model(doc, init_file, out_dir):
  ini = libsedml.SedModel(1, 2)
  ini_id = os.path.split(init_file)[1].rstrip('.xml')
  ini.setId(ini_id)
  ini.setLanguage('urn:sedml:language:sbml')
  ini.setSource(os.path.relpath(init_file, out_dir))
  doc.addModel(ini)
  # create associated task
  ini_tsk = libsedml.SedTask(1, 2)
  ini_tsk.setId('task_' + ini_id)
  ini_tsk.setSimulationReference('stepper')
  ini_tsk.setModelReference(ini_id)
  doc.addTask(ini_tsk)

# populate list of models & tasks
def add_models(doc, files, out_dir):
  for m in files:
    mod = libsedml.SedModel(1, 2)
    m_id = os.path.split(m)[1].rstrip('.xml')
    mod.setId(m_id)
    mod.setLanguage('urn:sedml:language:sbml')
    mod.setSource(os.path.relpath(m, out_dir))
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
def write_scheduler_file(init_file, loc, out_dir, files, entries):
  sed_doc = libsedml.SedDocument(1, 2)
  add_sim(sed_doc)
  add_init_model(sed_doc, init_file, out_dir)
  add_models(sed_doc, files, out_dir)
  build_loop(sed_doc, entries)
  # writing generated file
  sed_writer = libsedml.SedWriter()
  sed_writer.writeSedMLToFile(sed_doc, loc)

mods = ifaces.build_all_models(io_location, delimiter)
write_init_file(mods, out_ini)
entries = ifaces.build_entries(mods)
sed_dir = os.path.dirname(os.path.abspath(out_sed))
write_scheduler_file(out_ini, out_sed, sed_dir, model_files, entries)
