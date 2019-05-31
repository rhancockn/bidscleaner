#!/usr/bin/env python
import glob
import os
import json
import datetime
import warnings

def match_times(target_info, fmaps, fmap_info):
    """
    Match a target series to the temporally closest fieldmap

    :param dict target_info: Target metadata, must include AcquisitionTime
    :param list fmaps: List of possible fieldmap keys to check
    :param dict fmap_info: Metadata for candidate fieldmaps
    :return: the key of the best matched fieldmap
    :rtype: str
    """

    target_t = datetime.datetime.strptime(target_info['AcquisitionTime'], '%H:%M:%S.%f')

    best_fmap = None
    best_delta = float('inf')
    for fmap in fmaps:
        fmap_t = datetime.datetime.strptime(fmap_info[fmap]['AcquisitionTime'], '%H:%M:%S.%f')

        d = abs((fmap_t - target_t).seconds)
        if d < best_delta:
            best_delta = d
            best_fmap = fmap
    return best_fmap


def match_maps(prefix):
    """
    Scan a folder and match each target scan to the best fieldmap.

    The possible targets are discovered from IntendedFor lists. If a scan is a
    target for multiple fieldmaps, the best fieldmap is identified.
    
    For anat types, the fieldmap with the nearest AcquisitionTime to the anat
    series is selected.
    
    For other types, the following candidates are tested:

    #. the fieldmap with the nearest AcquisitionTime of fieldmaps that match
            the target position and shim setting
    #. the fieldmap with the nearest AcquisitionTime of fieldmaps that match
            the target position
    #. the fieldmap with the nearest AcquisitionTime

    :param str prefix: The folder to search
    :return: fieldmap metadata
    :rtype: dict
    """
    targets = list()
    target_info = dict()
    fmap_info = dict()

    # parse all the fieldmaps
    for fmap_json in glob.glob(f'{prefix}/fmap/*.json'):
        with open(fmap_json, 'r') as fp:
            sidecar = json.load(fp)
            targets = targets + sidecar['IntendedFor']
            fmap_info[fmap_json] = sidecar
            fmap_info[fmap_json]['NewIntendedFor'] = []
            for target in sidecar['IntendedFor']:
                if target in target_info.keys():
                    target_info[target]['fmaps'].append(fmap_json)
                else:
                    target_info[target] = dict(fmaps=[fmap_json])


    # match fieldmaps and targets
    processed_targets = []
    for target in targets:
        fmaps = target_info[target]['fmaps']
        if targets.count(target) == 1:
            # do nothing if a target only appears once
            fmap_info[fmaps[0]]['NewIntendedFor'].append(target)
            continue
        
        if target in processed_targets:
            continue

        processed_targets.append(target)

        with open(os.path.join(prefix,target.replace('.nii.gz', '.json')), 'r') as fp:
            sidecar = json.load(fp)
            target_info[target]['AcquisitionTime'] = sidecar['AcquisitionTime']
            target_info[target]['ShimSetting'] = sidecar['ShimSetting']
            target_info[target]['ImageOrientationPatientDICOM'] = sidecar['ImageOrientationPatientDICOM']

        if target.startswith('anat'):
            # match anatomicals on start time
            fmap = match_times(target_info[target], fmaps, fmap_info)
            fmap_info[fmap]['NewIntendedFor'].append(target)
        else:
            # match dwi, func on position and shim setting
            new_fmap_info = dict()
            for fmap in fmaps:
                if (fmap_info[fmap]['ShimSetting'] == target_info[target]['ShimSetting']) and (fmap_info[fmap]['ImageOrientationPatientDICOM'] == target_info[target]['ImageOrientationPatientDICOM']):
                    new_fmap_info[fmap] = fmap_info[fmap].copy()
                    new_fmap_info[fmap]['NewIntendedFor'].append(target)

            if len(new_fmap_info) == 0:
                # try matching only position
                for fmap in fmaps:
                    if fmap_info[fmap]['ImageOrientationPatientDICOM'] == target_info[target]['ImageOrientationPatientDICOM']:
                        new_fmap_info[fmap] = fmap_info[fmap].copy()
                        new_fmap_info[fmap]['NewIntendedFor'].append(target)
            
            if len(new_fmap_info) == 0:
                # fallback to time based match
                warnings.warn(f'WARNING: No fieldmap is aligned with {target}. Matching by AcquisitionTime.')
                fmap = match_times(target_info[target], fmaps, fmap_info)
                fmap_info[fmap]['NewIntendedFor'].append(target)
            
            elif len(new_fmap_info) > 1:
                # multiple possilbe matches-choose nearest in time
                fmap = match_times(target_info[target], new_fmap_info.keys(), new_fmap_info)
                fmap_info[fmap]['NewIntendedFor'].append(target)
            else:
                k = list(new_fmap_info.keys())[0]
                fmap_info[k]['NewIntendedFor'] = new_fmap_info[k]['NewIntendedFor']


    return fmap_info


def write_maps(fmap_info):
    """
    Overwrite the fieldmap JSON files.

    :param dict fmap_info: Fieldmap metadata, from :func:`match_maps`
    """
    for fmap, info in fmap_info.items():
        with open(fmap, 'w+') as fp:
            info['IntendedFor'] = info.pop('NewIntendedFor')
            json.dump(info, fp, indent='\t')


if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('bids_dir', help="BIDS directory path")
    argparser.add_argument('sub', help='subject id')
    args = argparser.parse_args()

    sub_dir = '{bids_dir}/sub-{sub}'.format(**vars(args))

    sessions = glob.glob(f'{sub_dir}/ses-*')

    if len(sessions) == 0:
        sessions = ['']

    for ses in sessions:
        prefix = f'{sub_dir}/{ses}'
        fmap_info = match_maps(prefix)
        write_maps(fmap_info)


