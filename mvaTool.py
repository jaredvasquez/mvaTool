import sys, yaml
from ROOT import *

TMVA.Tools.Instance()

if (len(sys.argv) < 2): print "Usage: ./tool.py <config>"; sys.exit()

cfgfile = sys.argv[1]
with open(cfgfile, 'r') as ymlfile:
  cfg = yaml.load(ymlfile)

for section in cfg:
  print(section)
  print cfg[section]
  print ""


fout    = TFile( cfg['options']['outputfile'], "RECREATE" )
factory = TMVA.Factory("ttHClassification", fout, ":".join(cfg['factory']))


# Prepare Trees
SigTree = TChain( cfg['options']['treename'] )
BkgTree = TChain( cfg['options']['treename'] )
for fname in cfg['samples']['signal']:      SigTree.Add( fname )
for fname in cfg['samples']['background']:  BkgTree.Add( fname )


# Add spectators
for varname in cfg['variables']['spectators']:
  factory.AddSpectator( varname )


# Add discriminants
for varname in cfg['variables']['discriminants']:
  if (hasattr(SigTree, varname)):
    vartype = type( getattr(SigTree, varname) )

    typeIndex = ''
    if   (vartype == type(float())): typeIndex = "F"
    elif (vartype == type(  int())): typeIndex = "I"
    else:  print "COULD NOT FIND TYPE"

  else: typeIndex = "F" # assume user function is float

  factory.AddVariable( varname, typeIndex )


factory.AddSignalTree( SigTree )
factory.AddBackgroundTree( BkgTree )


# cuts defining the signal and background sample
SigCut, BkgCut = "", ""
if ('SigCuts' in cfg['options']): SigCut = cfg['options']['SigCuts']
if ('BkgCuts' in cfg['options']): BkgCut = cfg['options']['BkgCuts']

factory.PrepareTrainingAndTestTree( TCut(SigCut), TCut(BkgCut), ":".join(cfg['training']) )
method  = factory.BookMethod( TMVA.Types.kBDT, "BDT", ":".join(cfg['classifier']) )

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

