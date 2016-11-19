from math import sqrt
from array import array
from ROOT import *

def EvaluateSample( InputPath, outputDir='ntuples_BDT/' ):
#------------------------------------------------------------
  tf = TFile( InputPath )
  nt = tf.Get("physics")

  print "\n\n\n"
  print InputPath

  pT_j1       = array( 'f', [0.] )
  njets_25    = array( 'f', [0.] )
  njetsCen_30 = array( 'f', [0.] )
  ntags_25_77 = array( 'f', [0.] )
  pT_lv       = array( 'f', [0.] )
  met_TST     = array( 'f', [0.] )
  sumet_TST   = array( 'f', [0.] )
  METsig      = array( 'f', [0.] )

  BDTlep      = array( 'f', [0.] )
  BDThad      = array( 'f', [0.] )

  lepreader = TMVA.Reader( "!Color:!Silent" )
  hadreader = TMVA.Reader( "!Color:!Silent" )

  lepreader.AddVariable( "pT_j1",       pT_j1       )
  lepreader.AddVariable( "njets_25",    njets_25    )
  lepreader.AddVariable( "njetsCen_30", njetsCen_30 )
  lepreader.AddVariable( "ntags_25_77", ntags_25_77 )
  lepreader.AddVariable( "pT_lv",       pT_lv       )
  lepreader.AddVariable( "met_TST",     met_TST     )
  lepreader.AddVariable( "sumet_TST",   sumet_TST   )
  lepreader.AddVariable( "METsig",      METsig      )

  lepreader.BookMVA("BDTlep","weights/ttHlep_Classification_ttHlep_BDT.weights.xml")

  hadreader.AddVariable( "pT_j1",       pT_j1       )
  hadreader.AddVariable( "njets_25",    njets_25    )
  hadreader.AddVariable( "njetsCen_30", njetsCen_30 )
  hadreader.AddVariable( "ntags_25_77", ntags_25_77 )
  hadreader.AddVariable( "sumet_TST",   sumet_TST   )
  #hadreader.AddVariable( "met_TST",     met_TST     )
  #hadreader.AddVariable( "METsig",      METsig      )

  hadreader.BookMVA("BDThad","weights/ttHhad_Classification_ttHhad_BDT.weights.xml")


  fileName = InputPath.split('/')[-1]
  if "/" != outputDir[-1]: outputDir += "/"

  to = TFile( outputDir + fileName, "RECREATE" ); to.cd()
  tt = nt.CloneTree(0)

  tt.Branch( "BDTlep", BDTlep, "BDTlep/F" )
  tt.Branch( "BDThad", BDThad, "BDThad/F" )

  for ievt in xrange(nt.GetEntries()):
    nt.GetEntry(ievt)

    pT_j1       [0] = nt.pT_j1
    njets_25    [0] = nt.njets_25
    njetsCen_30 [0] = nt.njetsCen_30
    ntags_25_77 [0] = nt.ntags_25_77
    pT_lv       [0] = nt.pT_lv
    met_TST     [0] = nt.met_TST
    sumet_TST   [0] = nt.sumet_TST
    METsig      [0] = nt.METsig

    BDTlep      [0] = -999.999;
    BDThad      [0] = -999.999;

    if ( nt.N_lep >= 1 ):
      BDTlep    [0] = lepreader.EvaluateMVA("BDTlep")

    if ( nt.N_lep == 0 ) and ( nt.ntags_25_77 > 0 ):
      BDThad    [0] = hadreader.EvaluateMVA("BDThad")

    #print "Event %d :    pT_j1 = %7.3f    BDT = %6.3f" % ( ievt, pT_j1[0]*0.001, BDT[0] )

    tt.Fill()

  tt.Write()


if __name__ == "__main__":
  samples = [
      "ntuples_split/ttH_test.root",
      "ntuples/ggH.root",
      "ntuples/VBF.root",
      "ntuples/WH.root",
      "ntuples/ZH.root",
      "ntuples/tHjb.root",
      "ntuples/tWH.root",
      "ntuples/bbH.root",
      "ntuples_split/data_test.root",
  ]

  Tsamples = [
      "ntuples_split/ttH_train.root",
      "ntuples_split/data_train.root",
  ]

  for sample in samples: EvaluateSample( sample )

