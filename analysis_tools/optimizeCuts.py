from ROOT import *
from math import sqrt, log

def Z(S,B): return 0.0 if (B<=0.) else sqrt( 2*( (S+B)*log( 1 + S/B ) - S ) )
def combZ(Zs):
  Ztot = 0.0
  for Z in Zs: Ztot += Z**2
  return sqrt(Ztot)

useTI = False
useTI = True

useICHEP = False
#useICHEP = True

Ztots   = []
signals = [ "ttH_test" ] #, "tHjb", "tWH" ]
samples = [ "ttH_test", "ggH", "VBF", "WH", "ZH", "tHjb", "tWH", "bbH", "data_test" ]

bdtVars = {
    "BDTlep": (2, "(N_lep >= 1)"),
    "BDThad": (2, "(N_lep == 0)"),
}


for bdtVar in bdtVars:
  print bdtVar
  alpha, xmin = 0.02, 0.30

  cutVals = [1.0]
  ZVals = []

  nCats, presel = bdtVars[bdtVar]

  if (useICHEP): nCats = 1

  for icat in xrange(nCats):
    xmax = min(cutVals)
    nPoints = int( (xmax-xmin)/alpha )
    if (useICHEP): nPoints = 1

    bestCut, bestZ = xmin, -999.
    #for cutVal in [ xmin + alpha*i for i in xrange(nPoints) ]:
    for i in xrange(nPoints):
      if (i > 0) and useICHEP: break
      cutVal = xmin + alpha*i

      yields = {}
      for proc in signals + ["background"]: yields[proc] = 0.0

      for proc in samples:
        tf = TFile("ntuples_BDT/%s.root" % proc)
        nt = tf.Get("physics")

        cuts = [ presel ]

        if "data" in proc:
          cuts.append( "(abs(m_yy*0.001-125)>5)" )
          cuts.append( "1.14*(10/45.)" )
          if (useTI): cuts.append( "isPassed" )
          else:       cuts.append( "isPassedRII" )
          if not (useTI):
            if   "BDTlep" in bdtVar: cuts.append( "0.118" )
            elif "BDThad" in bdtVar: cuts.append( "0.0439" )
        else:
          cuts.append( "36.5*isPassed*weightTotal" )

        if useICHEP:
          if   "BDTlep" in bdtVar: cuts.append( "(catCoup_dev == 13)" )
          elif "BDThad" in bdtVar: cuts.append( "(catCoup_dev == 12)" )
        else:
          cuts.append( "(%s < %f)" % (bdtVar, xmax) )
          cuts.append( "(%s > %f)" % (bdtVar, cutVal) )
          if "BDThad" in bdtVar:
            cuts.append( "(ntags_25_77 > 0)" )
            cuts.append( "(njets_25 > 2)" )

        if ("_test" in proc) or ("_train" in proc):
          cuts.append( "2.0" )

        sel = "*".join(cuts)
        #print sel

        nt.Draw( "isPassed >> hist(2,0,2)", sel, "HIST" )
        h = gROOT.FindObject("hist")
        N = h.Integral(0,999)

        if proc in yields: yields[proc] += N
        else: yields['background'] += N


      #print ""
      #print "CutVal = %6.2f" % cutVal
      for proc in signals:
        B, S = 0., yields[proc]
        for key in yields:
          if proc == key: continue
          B += yields[key]
        Zval = Z(S,B)
        #print "%15s :  %6.2f  %6.2f  %6.2f" % ( proc, S, B, Zval )
        if (Zval > bestZ ):
          bestCut = cutVal
          bestZ   = Zval
          bestS   = S
          bestB   = B

    ZVals.append( bestZ )
    cutVals.append( bestCut )
    print "Cat %d  xmin = %6.2f  xmax = %6.2f  S = %6.2f  B = %6.2f  Z = %6.2f" \
        % (icat, bestCut, xmax, bestS, bestB, bestZ )

  Zcomb = combZ(ZVals)
  Ztots.append( Zcomb )
  print "  ttHlep Combined = %6.2f" % (Zcomb)
  print ""

Ztot = combZ(Ztots)
print "  Combined Significance = %6.2f" % (Ztot)
print ""
