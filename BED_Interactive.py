# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 18:14:19 2023

@author: flafauci
"""

import pydicom
import dicompylercore.dose as dc
import os
import dicompylercore
from dicompylercore import dicomparser, dvh, dvhcalc
from dicompylercore.dose import DoseGrid

from copy import deepcopy
import numpy as np
from dicompylercore import dicomparser
from pydicom.uid import generate_uid
from pydicom.datadict import dictionary_VR, keyword_dict
from dicompylercore.config import (
    dicompyler_uid_prefix_rtdose,
    mpl_available,
    scipy_available,
)
from datetime import datetime
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset
from warnings import warn

file_path = input (r"mettere il percorso della cartella che contiene CT e RTDose file") #copiare e incollare il percorso del folder dicom
file_name = input("copia e incolla il nome file dicom RTStruture e premi invio")                           #copiare e incollare il nome del file RT Structure
rt_dose = input("inserirecopia e incolla il nome file dicom RTDose e premi invio")                                        #copiare e incollare il nome del file RT Dose
file_path_completo = os.path.join(file_path, rt_dose)
dataset = pydicom.dcmread(file_path_completo)


# Access rtdose data #copiare e incollare nome del file rtdose
file_name_dose = rt_dose                           #copiare e incollare il nome del file RT Structure
file_path_dose = os.path.join(file_path, file_name_dose)
rtdose = pydicom.dcmread(file_path_dose)
rtdose1=rtdose

# Access DVH data #copiare e incollare nome del file rtstructure



# Access rt_structures_info
file_path_rtstructure=os.path.join(file_path, file_name)
rts_dataset=pydicom.dcmread(file_path_rtstructure)
dp = dicomparser.DicomParser(file_path_rtstructure)

structures=pydicom.dcmread(file_path_rtstructure)
structures_info = dp.GetStructures()

# Ottieni la lista dei nomi delle strutture (ROI)
structures = dp.GetStructures()
for structure_id, structure_info in structures.items():
    structure_name = structure_info['name']
    structure_type = structure_info['type']
    print("Nome della struttura:", structure_name)
    print("Type:", structure_type)
    try:
        structure_id = int(structure_id)  # Convert the structure ID to an integer
        rtdvh = dvh.DVH.from_dicom_dvh(rtdose.ds, structure_id)
        rtdvh.describe()
    except (AttributeError, KeyError):
        print(f"Not found structure with ID {structure_id}: {structure_name}")
# Creazione della hashtable delle ROI
roi_dict = {}

roi_list = list(structures_info.keys())
print(roi_list)

for roi in roi_list:
    dvh = dicompylercore.dvhcalc.get_dvh(rts_dataset, rtdose, roi)
    
print(dvh)    


#dose of each voxel, how to know the shape-> rtdose.pixel_array.shape
di=rtdose.pixel_array.astype(float) #matrice di dose della singola frazione
D=rtdose.pixel_array.astype(float) #ho aggiunto astype per il calcolo #matrice di dose totale
n=int(input("inserire il numero di frazioni")) #insert number of fraction
alfa_beta= float(input("inserire il rapporto alfa/beta") ) #insert alfa/beta ratio for each organ(spinal_cord)   
di_scaled=di* float(rtdose.DoseGridScaling)/n #dosegridscaling mi permette di tradurre i bytes in dose secondo uno scaling
D_scaled=D*float(rtdose.DoseGridScaling)    
                                        
# Multiply the dose grid by a factor 
factor = 1.0+(di_scaled/alfa_beta)    
#BED    
rtdose_new=D_scaled*factor #nuova array BED



rtdose_new_scaled=rtdose_new/float(rtdose.DoseGridScaling)


#update pixel array
# Update the PixelData attribute of the RT Dose file with the new scaled dose values.

rtdose.PixelData = (rtdose_new_scaled).astype(np.uint32).tobytes() 


# Save the new files
# Chiedi all'utente il nome del file di output

output_filename2 = input("Inserisci il nome del file di output per la BED (senza estensione): ")
# Estensione predefinita
file_extension = ".dcm"

# Crea il percorso completo del file di output

output_file_path2 = os.path.join(file_path, f"{output_filename2}{file_extension}" )

rtdose.save_as(output_file_path2)







