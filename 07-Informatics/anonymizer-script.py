import pydicom
from pydicom.uid import generate_uid
import os, sys

def anonymize(in_path, out_path):
    ds = pydicom.dcmread(in_path)
    # Minimal tag removal/replace (extend as needed)
    for tag in [(0x0010,0x0010),(0x0010,0x0020),(0x0010,0x0030),(0x0010,0x0040)]:
        if tag in ds:
            ds[tag].value = ""
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ds.save_as(out_path)

if __name__ == '__main__':
    anonymize(sys.argv[1], sys.argv[2])
