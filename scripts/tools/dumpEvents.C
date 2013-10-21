#include <iomanip>
#include "../interface/TRootMuon.h"
#include "../interface/TRootElectron.h"
#include "../interface/TRootJet.h"
#include "../interface/TRootCaloJet.h"
#include "../interface/TRootPFJet.h"
#include "../interface/TRootMET.h"
#include "../interface/TRootGenEvent.h"
#include "../interface/TRootSignalEvent.h"
#include "../interface/TRootEvent.h"
#include "../interface/TRootRun.h"
#include "../interface/TRootParticle.h"
#include "../interface/TRootMCParticle.h"
#include "../interface/TRootVertex.h"

#include <TFile.h>
#include <TH1.h>
#include <TH2.h>
#include <TCanvas.h>
#include <TBranch.h>
#include <TTree.h>
#include <string>
#include <algorithm>
#include <vector>


using namespace TopTree;
using namespace std;

void Tokenize(const string& str,
                      vector<string>& tokens,
                      const string& delimiters = " ")
{
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);
    // Find first "non-delimiter".
    string::size_type pos     = str.find_first_of(delimiters, lastPos);

    while (string::npos != pos || string::npos != lastPos)
    {
        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));
        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
}


int main(int argc, char** argv){

  // RETRIEVING LIST OF FILENAMES TO CHECK

  if (argc != 3) {

    cout << "Usage: ./TopTreeContentDump --inputfiles file1;file2;fileN\n\n" << endl;

    exit(0);

  } else if (argc == 3 && !strstr(argv[1],"--inputfiles")) {

    cout << "Usage: ./TopTreeContentDump --inputfiles file1;file2;fileN\n\n" << endl;

    exit(0);

  }

  vector<string> fileNames;
  
  Tokenize(argv[2], fileNames, ";");


  // CHECKING THE FILECONTENT FOR FILE 0 AND COUNT EVENTS FOR ALL FILES

  unsigned int nEvents = 0; 

  for (int fileID=0; fileID < fileNames.size(); fileID++) {
  
    //cout << fileNames.at(fileID) << endl;

    TFile* f = TFile::Open(fileNames.at(fileID).c_str());
    
    TTree* runTree = (TTree*) f->Get("runTree");
    TTree* eventTree = (TTree*) f->Get("eventTree");
    
    TBranch* run_br = (TBranch *) runTree->GetBranch("runInfos");
    TRootRun* runInfos = 0;
    run_br->SetAddress(&runInfos);
    
    TBranch* event_br = (TBranch *) eventTree->GetBranch("Event");
    TRootEvent* event = 0;
    event_br->SetAddress(&event);
    
    nEvents += eventTree->GetEntriesFast();

    cout << fileNames.at(fileID) << " " << nEvents << endl;


  }

  //cout << "\n* The TopTree file contains " << nEvents << " events\n" << endl;


}
  
