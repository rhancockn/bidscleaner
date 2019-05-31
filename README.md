# bidscleaner
A Python module for heuristically cleaning BIDS datasets

# Install

```
git clone https://github.com/rhancockn/bidscleaner.git && \
cd bidscleaner && \
python setup.py install
```

# CLI Features

## Modify fieldmap associations

```
prune_fmap.py bids_dir subject_id
```


Scan a folder and match each target scan to the best fieldmap.

The possible targets are discovered from IntendedFor lists. If a scan is a
target for multiple fieldmaps, the best fieldmap is identified.

For anat types, the fieldmap with the nearest AcquisitionTime to the anat
series is selected.

For other types, the following candidates are tested:

1. the fieldmap with the nearest AcquisitionTime of fieldmaps that match
        the target position and shim setting
1. the fieldmap with the nearest AcquisitionTime of fieldmaps that match
        the target position
1. the fieldmap with the nearest AcquisitionTime


