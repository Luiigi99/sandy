"""
This module contains only two public functions:

    * `read_mf2`
    * `write_mf2`

Function `read` reads a MF2/MT section from a string and produces a content
object with a dictionary-like structure.
The content object can be accessed using most of the keywords specified in
the ENDF6 manual for this specific MF section.

Function `write_mf2` writes a content object for a MF2/MT section into a
string.
MAT, MF, MT and line numbers are also added (each line ends with a `\n`).
"""

import sandy

import numpy as np 

__author__ = "Rayan HADDAD"
__all__ = [
        "read_mf2",
        "write_mf2"
        ]


mf = 2
mt = 151

def read_mf2(tape, mat):
        

    df = tape._get_section_df(mat, mf, mt)
    out = {
            "MAT": mat,         
            "MF": mf,
            "MT": mt,
            }
    i = 0
    I = {}
    C, i = sandy.read_cont(df, i)
    add = {
            "ZA": C.C1,             
            "AWR": C.C2,            #AWR is defines as the ratio of the mass of the material to that of the neutron
            "NIS": C.N1,            #NIS is the number of isotopes in the material
            }
    NIS = int(C.N1)
    I.update(add)
    
    
    C, i = sandy.read_cont(df, i)
    add = {
            "ZAI": C.C1,
            "ABN": C.C2,           #Abundance of an isotope in the material 
            "LFW": C.L2,           #indication whether average fission wifths are given in the unresolbed resonance region
            "NER": C.N1,           #Number of resonance energy ranges for this isotope. 
            }   
    NER = int(C.N1)
    LFW = int(C.L2) 
    
    I.update(add)
    out.update({"Intro": I})
   
    
    P = {}
    for l in range(NIS): 
        M = {}
        for j in range (NER):
            info = {}
            
            C, i = sandy.read_cont(df, i)
            add = {
                    "EL": C.C1,             #Lower limit for an energy range
                    "EH": C.C2,             #Upper limit for an energy range
                    "LRU": C.L1,            #Flag indicating whether this energy range contains data for resolved or unresolved resonance parameters:
                    "LRF": C.L2,            #Flag indicating which representation has been used for the energy range. 
                    "NRO": C.N1,            #Flag designating possible energy dependence of the scattering radiu
                    "NAPS":C.N2,            #Flag controlling the use of the two radii
                    }
            LRU = int(C.L1)
            LRF = int(C.L2)
            NRO = int(C.N1)
            print (LRU, LRF,NRO)
            info.update({f"header {j}": add})
            M.update({f"NER {j}": info})
            
            
            
            if LRU == 0:
                LRU0 = {}
                C, i = sandy.read_cont(df, i)
                add = {
                        "SPI": C.C1,        #Spin, I, of the target nucleus.
                        "AP": C.C2,         #Scattering radius in units of 10e-12cm.
                        "NLS": C.N1,        #Number of l-values (neutron orbital angular momentum) in this energy region.
                        }
                LRU0.update(add)
                info.update({"LRU = 0":LRU0})
                M.update({f"NER {j}": info})
            
            if LRU == 1:
               
                if LRF == 1 or LRF == 2 :
                    
                    if NRO == 0 :
                        LRU1_LRF1_2_NRO0 = {}
                        C, i = sandy.read_cont(df, i)
                        add = {
                                "SPI": C.C1,
                                "AP": C.C2,
                                "NLS": C.N1,
                                }
                        NLS = int (C.N1)
                        LRU1_LRF1_2_NRO0.update(add)
                        
                        
                        for k in range(NLS) :
                            L, i = sandy.read_list(df, i)
                            NRS= int(L.N2)
                            add_2 = {
                                    "AWRI": L.C1,       #Ratio of the mass of a particular isotope to that of a neutron
                                    "QX": L.C2,         #Q-value to be added to the incident particle’s center-of-mass energy to determine the channel energy for use in the penetrability factor.
                                    "L": L.L1,          #Value of l.
                                    "LRX": L.L2,        #Flag indicating whether this energy range contains a competitive width
                                    "6*NRS": L.NPL,     
                                    "NRS": L.N2,        #Number of resolved resonances for a given l-value.
                                    "List" : np.array(L.B),
                                    }
                            LRU1_LRF1_2_NRO0.update({k: add_2})
                        info.update({"LRU = 1 LRF = 1 or 2 NRO = 0" : LRU1_LRF1_2_NRO0})
                        M.update({f"NER {j}": info})
                            
                    
                    else :   
                        
                        LRU1_LRF1_2_NRO1 = {}
                        T, i = sandy.read_tab1(df, i)
                        add = {
                                "NR": T.NBT,    
                                "NP": T.INT,
                                "E_int": T.x,
                                "AP": T.y,
                                }
                        LRU1_LRF1_2_NRO1.update(add)
                        out.update({"LRU = 1 LRF = 1 or 2": LRU1_LRF1_2_NRO1})
                        M.update({f"NER {j}": info})
    
                if LRF == 3 :
                        
                        if NRO == 0 :
                            LRU1_LRF3_NRO0={}
                            C, i = sandy.read_cont(df, i)
                            add = {
                                    "SPI": C.C1,
                                    "AP": C.C2,
                                    "LAD": C.L1,     #Flag indicating whether these parameters can be used to compute angular distributions
                                    "NLS": C.N1,     
                                    "NLSC": C.N2,    #Number of l-values
                                    }
                            NLS = int(C.N1)
                            LRU1_LRF3_NRO0.update(add)
                            
                            for k in range(NLS) :
                                L, i = sandy.read_list(df, i)
                                add = {
                                         "AWRI": L.C1,
                                         "QX": L.C2,
                                         "L": L.L1,
                                         "LRX": L.L2,
                                         "6*NRS": L.NPL,
                                         "NRS": L.N2,
                                         "List": np.array(L.B),
                                         }
                                LRU1_LRF3_NRO0.update({k: add})
                                
                            info.update({"LRU = 1 LRF = 3 NRO = 0": LRU1_LRF3_NRO0 })
                            M.update({f"NER {j}": info}) 
                                
                        else :
                            LRU1_LRF3_NRO1={}
                            T, i = sandy.read_tab1(df, i)
                            add = {
                                    "NR": T.NBT,    
                                    "NP": T.INT,
                                    "E_int": T.x,
                                    "AP": T.y,
                                    }
                            LRU1_LRF3_NRO1.update(add)
                            out.update({"LRU = 1 LRF = 3": LRU1_LRF3_NRO1})
                            M.update({f"NER {j}": info})
                            
                            
                            
                if LRF == 4 :
                    
                  raise ValueError("LRF = 4 is not supported in SANDY")
                  
                  
                if LRF == 7 :
                    LRU1_LRF7={}
                    
                    C, i = sandy.read_cont(df, i)
                    add = {
                            "IFG": C.L1,
                            "KRM": C.L2,
                            "NJS": C.N1,
                            "KRL": C.N2,
                            }
                    NJS = int(C.N1)
                    LRU1_LRF7.update(add)
                    
                    L, i = sandy.read_list(df, i)
                    NPP= int(L.N2)
                    add = { 
                            "NPP": L.L1,
                            "12*NPP": L.NPL,
                            "2*NPP": L.N2,                  #Total number of particle-pairs.
                            "List": np.array(L.B),
                            }
                    LRU1_LRF7.update(add)
                    
                    for k in range(NJS):
                        
                        L, i = sandy.read_list(df, i)
                        NCH = int(L.N2)
                        add = {
                                "AJ": L.C1,             #Floating point value of J (spin); sign indicates parity
                                "PJ": L.C2,             #Parity (used only if AJ = 0.0).
                                "KBK": L.L1,            #Non-zero if background R-matrix exists
                                "KPS": L.L2,            #Non-zero if non-hard-sphere phase shift are to be specified.
                                "6*NCH": L.NPL,
                                "NCH": L.N2,            #Number of channels for the given J pi.   
                                "List_1":np.array(L.B),
                                }
                        
                        L, i = sandy.read_list(df, i)
                        add2 = {
                                "NRS": L.L2,            #Number of resonances for the given J pi 
                                "6*NX": L.NPL,
                                "NX": L.N2,
                                "List_2": np.array(L.B),
                                }
                        add.update(add2) 
                        LRU1_LRF7.update({k :add})  
                        
                    info.update({"LRU = 1 LRF = 7": LRU1_LRF7}) 
                    M.update({f"NER {j}": info})
                    
                    
                    
                    
            if LRU == 2 :
                if LFW == 0 and LRF == 1 : 
                    
                    LRU2_LFW0_LRF1 ={}
                    C, i = sandy.read_cont(df, i)
                    add = {
                            "SPI": C.C1,
                            "AP": C.C2,
                            "LSSF": C.L1,                   #Flag governing the interpretation of the File 3 cross sections
                            "NLS": C.N1,                    #Number of l-values.
                            }
                    
                    NLS = int(C.N1)
                    LRU2_LFW0_LRF1.update(add)
                    
                    for k in range (NLS):
                        L, i = sandy.read_list(df, i)
                        NJS= int(L.N2)
                        add = {
                                "AWRI": L.C1,
                                "L": L.L1,
                                "6*NJS": L.NPL,
                                "NJS": L.N2,                    #Number of J-states for a particular l-state
                                "List" : np.array(L.B),
                                    }
                        LRU2_LFW0_LRF1.update({k : add})
                    info.update({"LRU = 2 LWF = 0 LRF = 1" : LRU2_LFW0_LRF1})
                    M.update({f"NER {j}": info})
                        
                if LFW == 1 and LRF == 1 :
                    
                    raise ValueError("LRF = 4 is not supported in SANDY")
                    
                        
                if LRF == 2 : 
                    
                    LRU2_LRF2 = {}
                    C, i = sandy.read_cont(df, i)
                    add = {
                            "SPI": C.C1,
                            "AP": C.C2,
                            "LSSF": C.L1,
                            "NLS": C.N1,
                            }
                    NLS = int (C.N1)
                    
                    LRU2_LRF2.update(add)
                    for m in range (NLS) :
                        C, i = sandy.read_cont(df, i)
                        add = {
                                "AWRI": C.C1,
                                "L": C.L1,
                                "NJS": C.N1,
                                }
                        LRU2_LRF2.update(add)
                        
                        NJS = int(C.N1)
                        
                        LRU2_LRF2_NJS = {}
                        for k in range (NJS):
                            L, i = sandy.read_list(df, i)
                            NE= int(L.N2)
                            add_2 = {
                                    "AJ": L.C1,
                                    "INT": L.L2,                #Interpolation scheme to be used for interpolating between the cross sections obtained from average resonance parameters.
                                    "6*NE+6": L.NPL,
                                    "NE": L.N2,
                                    "AMUX": L.B[2],             #Number of degrees of freedom used in the competitive width distribution.
                                    "AMUN": L.B[3],             #Number of degrees of freedom in the neutron width distribution.
                                    "AMUG": L.B[4],             #Number of degrees of freedom in the radiation width distribution.
                                    "AMUF": L.B[5],             #Integer value of the number of degrees of freedom for fission widths.
                                    "List" : np.array(L.B[6::]),
                                    }
                            LRU2_LRF2_NJS.update({k : add_2})
                        LRU2_LRF2.update({m: LRU2_LRF2_NJS})
                    info.update({"LRU = 2 LRF = 2": LRU2_LRF2})
                    
                    M.update({f"NER {j}": info})
        
    P.update({l : M})
    out.update({f"NIS {l}": P})
                   
    return out
        
def write_mf2(sec): 
    
    lines = sandy.write_cont(
        sec["Intro"]["ZA"],
        sec["Intro"]["AWR"],
        0,
        0,
        sec["Intro"]["NIS"],
        0,
        )
    NIS = int(sec["Intro"]["NIS"])
    lines += sandy.write_cont(
        sec["Intro"]["ZAI"],
        sec["Intro"]["ABN"],
        0,
        sec["Intro"]["LFW"],
        sec["Intro"]["NER"],
        0,
        )
    NER = int(sec["Intro"]["NER"])
    LFW = int(sec["Intro"]["LFW"])
    for l in range(NIS): 
        for j in range (NER):
            
            lines += sandy.write_cont(
                sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["EL"],
                sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["EH"],
                sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["LRU"],
                sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["LRF"],
                sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["NRO"],
                sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["NAPS"],
                )
            LRU = int(sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["LRU"])
            LRF = int(sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["LRF"])
            NRO = int(sec[f"NIS {l}"][l][f"NER {j}"][f"header {j}"]["NRO"])
            
            
            if LRU == 0:
                
                lines += sandy.write_cont(
                    sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 0"]["SPI"],
                    sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 0"]["AP"],
                    0,
                    0,
                    sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 0"]["NLS"],
                    0,
                    )
            if LRU == 1:
            
                if LRF == 1 or LRF == 2 :
                    
                    if NRO == 0 :
                        
                        lines += sandy.write_cont(
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"]["SPI"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"]["AP"],
                            0,
                            0,
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"]["NLS"],
                            0,
                            )
                        NLS = int(sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"]["NLS"])
                        for k in range(NLS): 
                            lines +=sandy.write_list(
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"][k]["AWRI"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"][k]["QX"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"][k]["L"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"][k]["LRX"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"][k]["NRS"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2 NRO = 0"][k]["List"],
                                )
                            
                    else :
                        
                        lines += sandy.write_tab1(
                                0,
                                0,
                                0,
                                0,
                                0,
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2"]["NR"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2"]["NP"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2"]["E_int"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 1 or 2"]["AP"],
                                )
                        
                if LRF == 3:
                    
                    if NRO == 0: 
                        
                        lines += sandy.write_cont(
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"]["SPI"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"]["AP"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"]["LAD"],
                            0,
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"]["NLS"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"]["NLSC"],
                            )
                        NLS = int(sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"]["NLS"])
                        for k in range(NLS): 
                            lines +=sandy.write_list(
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"][k]["AWRI"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"][k]["QX"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"][k]["L"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"][k]["LRX"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"][k]["NRS"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3 NRO = 0"][k]["List"],
                                )
                    else :
                        
                        lines += sandy.write_tab1(
                                0,
                                0,
                                0,
                                0,
                                0,
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3"]["NR"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3"]["NP"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3"]["E_int"],
                                sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 3"]["AP"],
                                )
                if LRF == 7:
                    
                    lines += sandy.write_cont(
                        0,
                        0,
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["IFG"],
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["KRM"],
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["NJS"],
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["KRL"],
                        )
                    NJS = int(sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["NJS"])    
                    lines += sandy.write_list(
                        0,
                        0,
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["NPP"],
                        0,
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["2*NPP"],
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"]["List"],
                        )
                    
                    
                    for k in range(NJS):
                        lines += sandy.write_list(
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["AJ"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["PJ"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["KBK"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["KPS"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["NCH"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["List_1"],
                            )
                            
                        lines += sandy.write_list(
                            0,
                            0,
                            0,
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["NRS"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["NX"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 1 LRF = 7"][k]["List_2"],
                            )
                    
            if LRU == 2:
                
                if LFW == 0 and LRF == 1 :
                    
                    
                    lines += sandy.write_cont(
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"]["SPI"],
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"]["AP"],
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"]["LSSF"],
                        0,
                        sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"]["NLS"],
                        0,
                        )
                    
                    for k in range (NLS):
                        lines += sandy.write_list(
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"][k]["AWRI"],
                            0,
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"][k]["LSSF"],
                            0,
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"][k]["NLS"],
                            sec[f"NIS {l}"][l][f"NER {j}"]["LRU = 2 LWF = 0 LRF = 1"][k]["List"],
                            )
                     
                    
               
                    
                    
    
    
    return "\n".join(sandy.write_eol(lines, sec["MAT"], 2, 151))
