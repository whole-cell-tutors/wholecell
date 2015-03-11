#!/usr/bin/env python
# coding=utf-8

# Python script for generating the master SED-ML file for the wholecell model
import libsbml, libsedml

# Required inputs
model_files = ['toymodel1.xml', 'toymodel2.xml', 'toymodel3.xml']
io_files = []
loc = 'toy_scheduler.xml'

doc = libsedml.SedDocument(1, 2)

# create stepper simulation
sim = libsedml.SedOneStep(1, 2)
sim.setId('stepper')
sim.setStep(1.0)
alg = libsedml.SedAlgorithm(1, 2)
alg.setKisaoID('KISAO:0000032')
sim.setAlgorithm(alg)
doc.addSimulation(sim)

tsk_lst = [] # keeping track of the tasks

# populate list of models & tasks
for m in model_files:
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
  tsk_lst.append(tsk.getId())
  doc.addTask(tsk)

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
doc.addTask(rpt)

# writing generated file
writer = libsedml.SedWriter()
writer.writeSedMLToFile(doc, loc)
