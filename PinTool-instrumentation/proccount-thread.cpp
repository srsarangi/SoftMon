/*
 * Copyright 2002-2019 Intel Corporation.
 * 
 * This software is provided to you as Sample Source Code as defined in the accompanying
 * End User License Agreement for the Intel(R) Software Development Products ("Agreement")
 * section 1.L.
 * 
 * This software and the related documents are provided as is, with no express or implied
 * warranties, other than those that are expressly stated in the License.
 */

//
// This tool counts the number of times a routine is executed and 
// the number of instructions executed in a routine
// along with the sequence of calls and ret for a function 

#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
#include <vector> 
#include "pin.H"
using std::vector;
using std::ofstream;
using std::string;
using std::hex;
using std::setw;
using std::cerr;
using std::dec;
using std::endl;

ofstream outFile;
ofstream outFile1;
PIN_LOCK lock;

// Holds instruction count for a single procedure
typedef struct RtnCount
{
    string _name;
    string _image;
    string _images;
    ADDRINT _address;
    RTN _rtn;
    UINT64 _rtnCount;
    UINT64 _icount;
    struct RtnCount * _next;
} RTN_COUNT;

typedef struct FnEntry
{
    string _name;
    string _image;
    int ret;
    struct FnEntry * _next;
} FN_ENTRY;

// Linked list of instruction counts for each routine
RTN_COUNT * RtnList = 0;

// FN_ENTRY * FnList = 0;
// Linked list to store the sequence of function calls and ret
vector<FN_ENTRY *> FnList;
vector<FN_ENTRY *> FnHead;

VOID docount(UINT64 * counter)
{
    (*counter)++;
}

const char * StripPath(const char * path)
{
    const char * file = strrchr(path,'/');
    if (file)
        return file+1;
    else
        return path;
}

// This function is called before every instruction is executed
VOID docount1(RTN_COUNT * rc, THREADID threadid)
{
    FN_ENTRY * fn = new FN_ENTRY;
    fn -> _name = rc -> _name;
    fn -> _image = rc -> _image;
    fn -> ret = 0;

    FnList[threadid]->_next = fn;
    FnList[threadid] = fn;

    (rc->_rtnCount)++;
}

VOID docount2(RTN_COUNT * rc, THREADID threadid)
{
    FN_ENTRY * fn = new FN_ENTRY;
    fn -> _name = rc -> _name;
    fn -> _image = rc -> _image;
    fn -> ret = 1;

    FnList[threadid]->_next = fn;
    FnList[threadid] = fn;

}

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    
    // Allocate a counter for this routine
    RTN_COUNT * rc = new RTN_COUNT;

    // The RTN goes away when the image is unloaded, so save it now
    // because we need it in the fini
    rc->_name = RTN_Name(rtn);
    rc->_images = StripPath(IMG_Name(SEC_Img(RTN_Sec(rtn))).c_str());
    rc->_image = IMG_Name(SEC_Img(RTN_Sec(rtn))).c_str();
    rc->_address = RTN_Address(rtn);
    rc->_icount = 0;
    rc->_rtnCount = 0;

    // Add to list of routines
    rc->_next = RtnList;
    RtnList = rc;
            
    RTN_Open(rtn);
    
    // outFile << setw(23) << rc->_name << " "<< setw(15) << rc->_image << endl;
    // Insert a call at the entry point of a routine to increment the call count
    RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)docount1, IARG_PTR, rc, IARG_THREAD_ID, IARG_END);
    
    // For each instruction of the routine
    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
    {
        // Insert a call to docount to increment the instruction counter for this rtn
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_PTR, &(rc->_icount), IARG_END);
        // Insert a call to docount2 to append a "ret" to the sequence
        if (INS_IsRet(ins)){
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount2, IARG_PTR, rc, IARG_THREAD_ID, IARG_END);
        }
    }

    
    RTN_Close(rtn);
}

// This function is called when the application exits
// It prints the name and count for each procedure
VOID Fini(INT32 code, VOID *v)
{
    outFile1 << setw(23) << "Procedure" << " "
          << setw(15) << "Image" << " "
          << setw(18) << "Address" << " "
          << setw(12) << "Calls" << " "
          << setw(12) << "Instructions" << endl;

    for (RTN_COUNT * rc = RtnList; rc; rc = rc->_next)
    {
        if (rc->_rtnCount > 0)
            outFile1 << setw(23) << rc->_name << " "
                  << setw(15) << rc->_image << " "
                  << setw(18) << hex << rc->_address << dec <<" "
                  << setw(12) << rc->_rtnCount << " "
                  << setw(12) << rc->_icount << endl;
    }

    // Write to a file once the tracing is completed
    for(int i=0; i<32; i++){
        for (FN_ENTRY * fn = FnHead[i]; fn; fn = fn->_next)
        {
            if(fn->ret==1){
                outFile << "TID:" << i << " " << fn->_image << " "<< fn->_name << " ret" << endl;
            }
            else if (fn->ret==0){
                outFile << "TID:" << i << " " << fn->_image << " "<< fn->_name << endl;    
            }
        }    
    }

}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This Pintool counts the number of times a routine is executed" << endl;
    cerr << "and the number of instructions executed in a routine" << endl;
    cerr << "along with the sequence of calls and ret for a function " << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char * argv[])
{
    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();

    outFile.open("proccount1.out");
    outFile1.open("proccount2.out");

    for(int i=0; i<32; i++){
        FN_ENTRY * fn = new FN_ENTRY;
        fn -> _name = "";
        fn -> _image = "";
        fn -> ret = -1;        
        FnList.push_back(fn);
        FnHead.push_back(fn);
    }

    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
