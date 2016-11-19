import sys, yaml
from ROOT import *

TMVA.Tools.Instance()

if (len(sys.argv) < 2): print "Usage: ./tool.py <config>"; sys.exit()

cfgfile = sys.argv[1]
with open(cfgfile, 'r') as ymlfile:
  cfg = yaml.load(ymlfile)



modelname = cfg['options']['modelname'] + "_"

fout    = TFile( cfg['options']['outputfile'], "RECREATE" )
factory = TMVA.Factory( modelname+"Classification", fout, ":".join(cfg['factory']))


# Prepare Trees
SigTree = TChain( cfg['options']['treename'] )
BkgTree = TChain( cfg['options']['treename'] )

if 'signal' in cfg['samples']:
  for fname in cfg['samples']['signal']:      SigTree.Add( fname )

if 'background' in cfg['samples']:
  for fname in cfg['samples']['background']:  BkgTree.Add( fname )


SigTree_Train = TChain( cfg['options']['treename'] )
SigTree_Test  = TChain( cfg['options']['treename'] )

BkgTree_Test  = TChain( cfg['options']['treename'] )
BkgTree_Train = TChain( cfg['options']['treename'] )

if 'testing' in cfg['samples']:
  for fname in cfg['samples']['testing']['signal']:      SigTree_Test.Add( fname )
  for fname in cfg['samples']['testing']['background']:  BkgTree_Test.Add( fname )

if 'training' in cfg['samples']:
  for fname in cfg['samples']['training']['signal']:      SigTree_Train.Add( fname )
  for fname in cfg['samples']['training']['background']:  BkgTree_Train.Add( fname )


# Add spectators
if 'spectators' in cfg['variables']:
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


if ( SigTree.GetEntries()       ): factory.AddSignalTree( SigTree )
if ( SigTree_Test.GetEntries()  ): factory.AddSignalTree( SigTree_Test,  TMVA.Types.kTesting )
if ( SigTree_Train.GetEntries() ): factory.AddSignalTree( SigTree_Train, TMVA.Types.kTraining )

if ( BkgTree.GetEntries()       ): factory.AddBackgroundTree( BkgTree )
if ( BkgTree_Test.GetEntries()  ): factory.AddBackgroundTree( BkgTree_Test,  1.0, TMVA.Types.kTesting )
if ( BkgTree_Train.GetEntries() ): factory.AddBackgroundTree( BkgTree_Train, 1.0, TMVA.Types.kTraining )


if ('SigWeight' in cfg['options']): factory.SetSignalWeightExpression( cfg['options']['SigWeight'] )
if ('BkgWeight' in cfg['options']): factory.SetBackgroundWeightExpression( cfg['options']['BkgWeight'] )


# cuts defining the signal and background sample
SigCut, BkgCut = "", ""
if ('SigCuts' in cfg['options']): SigCut = cfg['options']['SigCuts']
if ('BkgCuts' in cfg['options']): BkgCut = cfg['options']['BkgCuts']

factory.PrepareTrainingAndTestTree( TCut(SigCut), TCut(BkgCut), ":".join(cfg['training']) )
method  = factory.BookMethod( TMVA.Types.kBDT, modelname+"BDT", ":".join(cfg['classifier']) )

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()

