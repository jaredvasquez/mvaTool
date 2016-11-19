from ROOT import *

def plotVars( h1, h2, title=None ):

  if (title):
    h1.SetTitle(title)
    h2.SetTitle(title)

  h1.SetLineColor(kRed)
  h2.SetLineColor(kBlack)

  N1 = h1.Integral(0,h1.GetNbinsX()+1)
  N2 = h2.Integral(0,h2.GetNbinsX()+1)

  if not (N1==0.): h1.Scale( 1.0/N1 )
  if not (N2==0.): h2.Scale( 1.0/N2 )

  maxi = h1.GetMaximum()
  if ( h2.GetMaximum() > maxi ):
    maxi = h2.GetMaximum()

  h1.SetMaximum( 1.4*maxi )

  h1.Draw("HIST")
  h2.Draw("HIST SAME")

  tl = TLatex()
  tl.SetTextColor(kRed)
  tl.DrawLatexNDC( 0.6, 0.9, "#bf{ ttH lep, BDT > 0.13 }" )
  tl.SetTextColor(kBlack)
  tl.DrawLatexNDC( 0.6, 0.85, "#bf{ ttH lep, BDT < 0.0 }" )

  return h1, h2



tf = TFile("ntuples_BDT/ttH_test.root")
nt = tf.Get("physics")

savefile = "results_lep.pdf"

can = TCanvas()
can.cd()

can.SetTopMargin(0.05)
can.SetRightMargin(0.05)
can.SetBottomMargin(0.10)
can.SetLeftMargin(0.10)

gStyle.SetOptStat(0)

can.Print(savefile+"[")

sel1 = "(N_lep >= 1)*(isPassed)*(BDTlep > 0.13)*weightTotal"
sel2 = "(N_lep >= 1)*(isPassed)*(BDTlep < 0.00)*weightTotal"

## Draw Continuous Variables

fltVars = { "pT_j1":     "(100,0,800)",
            "pT_lv":     "(100,0,800)",
            "met_TST":   "(100,0,400)",
            "sumet_TST": "(100,0,2000)",
            "METsig":    "(100,0,15)",
            }

for var in fltVars:
  nt.Draw( "%s >> hist1_%s%s" % (var,var,fltVars[var]), sel1, "HIST" )
  nt.Draw( "%s >> hist2_%s%s" % (var,var,fltVars[var]), sel2, "HIST" )

  h1 = gROOT.FindObject("hist1_%s" % var)
  h2 = gROOT.FindObject("hist2_%s" % var)

  h1, h2 = plotVars( h1, h2, "; %s; Fraction Of Events" % var)
  can.Print(savefile)


### Draw Discrete Variables

intVars = ["njets_25","njetsCen_30","ntags_25_77"]

for var in intVars:
  nt.Draw( "%s >> histi1(10,0,10)" % var, sel1, "HIST" )
  nt.Draw( "%s >> histi2(10,0,10)" % var, sel2, "HIST" )

  h1 = gROOT.FindObject("histi1")
  h2 = gROOT.FindObject("histi2")

  h1, h2 = plotVars( h1, h2, "; %s; Fraction Of Events" % var)
  can.Print(savefile)


can.Print(savefile+"]")
