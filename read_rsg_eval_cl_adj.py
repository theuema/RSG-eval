from cmath import pi
import xml.etree.ElementTree as ET
import os
from glob import glob
import math as m
import sys
from pathlib import Path

def GetOPK(RMat):
    phi = m.asin(RMat[2][0])

    sin_o = -RMat[2][1]/m.cos(phi)
    omega = m.acos(RMat[2][2]/m.cos(phi))
    if sin_o < 0.0:
        omega = -omega

    sin_k = -RMat[1][0]/m.cos(phi)
    kappa = m.acos(RMat[0][0]/m.cos(phi))
    if sin_k < 0.0:
        kappa = -kappa
    if kappa < 0.0:
        kappa = kappa + 2.0*pi

    return omega, phi, kappa


def GetOPK_transposed(RMat):
    if((RMat[2][0] < -1.0) or (RMat[2][0] > 1.0)):
        omega = -1
        phi = -1
        kappa = -1
    else:
        phi   = m.asin(RMat[2][0])
        omega = m.atan2( (-RMat[2][1]/m.cos(phi)), RMat[2][2]/m.cos(phi) )
        kappa = m.atan2( (-RMat[1][0]/m.cos(phi)), RMat[0][0]/m.cos(phi) )
    return omega, phi, kappa

def get_par_paths(dir):
    # return a list of all image paths in a given directory
    return sorted(glob(os.path.join(dir, '*.PAR')))

def get_cl_paths(dir):
    # return a list of all image paths in a given directory
    return sorted(glob(os.path.join(dir, '*.cl')))

def calc_pixel_dist(p1, p2):
    return p1-p2

def calc_mean_pixel_dist(distances, N):
    return distances / N

def eval_per_single_image_example(ground_truth_cam_pose, adjusted_cam_pose):
    return 0

def eval_per_multiple_image_examples_mean(img_ids, ground_truth_cam_poses, adjusted_cam_poses):
    return 0

def eval_all_examples_mean(ground_truth_cam_poses, adjusted_cam_poses):
    return 0

def get_cam_poses_rsg(rsg_path):
    # returns a list of dicts containing camera poses from par files in /RSG folder
    # where the index is the img_id - 1
    # {'X': -1.2386, 'Y': 0.3558, 'Z': 1.2618, 'OMEGA': -92.589, 'PHI': -2.9511, 'KAPPA': 306.9729}

    # get adjusted poses from XML
    par_fpaths = get_par_paths(rsg_path)
    if not len(par_fpaths):
        print('Error: No par-files found in directory (%s)' % rsg_path)
        sys.exit(1)

    adjusted_cam_poses = []
    for par_fpath in par_fpaths:
        root = ET.parse(par_fpath).getroot()
        # --- some examples
        # print(root.tag) outputs 'PhysicalEntity'
        # get all attributes of PhysicalEntity:
        #   print(root.attrib) outputs '{relpath="." prefix="unknown" size="0" type="RSGimagemodel" version="3.1" state="----------"}'

        
        for attributes in root.findall('Attributes'): # iterate over all the nodes with tag name 'Attributes'
            if attributes.get('Set') == 'AdjustedGeometry': # extract the attribute 'Set' of 'Attributes'-Tag; compare with desired Set name 'AdjustedGeometry'
                adjusted_cam_pose = {}
                # include img_id to dict
                img_id = int(str(Path(par_fpath).stem).split('_')[-1])
                adjusted_cam_pose['ID'] = img_id 
                for tag in attributes.findall('Tag'): # iterate over all the nodes with tag name 'Tag'
                    if tag.get('id') == 'ORBX': adjusted_cam_pose['X'] = round(float(tag.text), 4) # get text of 'Tag' with desired 'id'
                    if tag.get('id') == 'ORBY': adjusted_cam_pose['Y'] = round(float(tag.text), 4)
                    if tag.get('id') == 'ORBZ': adjusted_cam_pose['Z'] = round(float(tag.text), 4)
                    if tag.get('id') == 'OMEGA': adjusted_cam_pose['OMEGA'] = round(float(tag.text) * 180/pi, 4)
                    if tag.get('id') == 'PHI': adjusted_cam_pose['PHI'] = round(float(tag.text) * 180/pi, 4)
                    if tag.get('id') == 'KAPPA': adjusted_cam_pose['KAPPA'] = round(float(tag.text) * 180/pi, 4)
                adjusted_cam_poses.append(adjusted_cam_pose)

    return adjusted_cam_poses

def get_cam_poses(ground_truth_cam_poses_fpath):
    # returns a list of dicts containing camera
    #  poses from a file
    # where the index is the img_id - 1
    # {'ID': 1, 'X': -1.2461, 'Y': 0.3497, 'Z': 1.2641, 'OMEGA': -91.9631, 'PHI': -3.2676, 'KAPPA': 306.7033}

    # Get ground truth camera poses
    f = open(ground_truth_cam_poses_fpath, 'r')
    ground_truth_cam_poses = []
    for line in f.readlines()[1:]:
        pos = line.rstrip().split(';')
        ground_truth_cam_pose = {}

        ground_truth_cam_pose['ID'] = int(pos[0])
        ground_truth_cam_pose['X'] = float(pos[1])
        ground_truth_cam_pose['Y'] = float(pos[2])
        ground_truth_cam_pose['Z'] = float(pos[3])
        RMat = [[float(pos[4]), float(pos[5]), float(pos[6])], 
                [float(pos[7]), float(pos[8]), float(pos[9])], 
                [float(pos[10]), float(pos[11]), float(pos[12])]]
        
        # get OPK
        omega, phi, kappa = GetOPK(RMat)
        omega *= 180/pi
        phi *= 180/pi
        kappa *= 180/pi

        ground_truth_cam_pose['OMEGA'] = round(omega, 4)
        ground_truth_cam_pose['PHI'] = round(phi, 4)
        ground_truth_cam_pose['KAPPA'] = round(kappa, 4)
        ground_truth_cam_poses.append(ground_truth_cam_pose)

    return ground_truth_cam_poses # sorted(ground_truth_cam_poses, key=lambda d: d['ID'])

def get_uv_coordinates_cl(cl_path):
    # returns a list of lists containing the uv coordinates of an image id
    # where the index is the img_id - 1
    # [{},{},{}, ... {}] = returnlist[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, {'CAT_ID': 19, 'U': 1028.49, 'V': 927.74}, {'CAT_ID': 20, 'U': 1739.0, 'V': 973.43}, {'CAT_ID': 21, 'U': 2030.97, 'V': 937.98}, {'CAT_ID': 22, 'U': 1255.0, 'V': 137.54}]

    # get cl filepath
    # s
    cl_fpaths = get_cl_paths(cl_path)
    if not len(cl_fpaths):
        print('Error: No cl-files found in directory (%s)' % cl_path)
        sys.exit(1)

    cl_img_id_coordinates = []
    for i, cl_fpath in enumerate(cl_fpaths):
        f = open(cl_fpath, 'r')
        cl_coordinates = []
        for line in f.readlines()[1:]:
            l = line.rstrip().split(';')
            # continue at manually defined 'GCP' points
            if 'GCP' in l[0]:
                continue

            coordinates = {}

            coordinates['CAT_ID'] = int(l[0])
            coordinates['U'] = round(float(l[1]), 2)
            coordinates['V'] = round(float(l[2]), 2)
            cl_coordinates.append(coordinates)
        
        # append usuing img ID of sorted cl_fpaths
        cl_img_id_coordinates.append(cl_coordinates)
    
    return cl_img_id_coordinates

def eval_cam_poses_mean(ground_truth_cam_poses: list, adjusted_cam_poses: list):
    # param 'cam poses'
    # {} = cam_poses[img_id - 1] 
    # {'ID': 1, 'X': -1.2461, 'Y': 0.3497, 'Z': 1.2641, 'OMEGA': -91.9631, 'PHI': -3.2676, 'KAPPA': 306.7033} 
    
    return

def eval_cv_centers_mean(uv_set_one: list, uv_set_two: list, uv_set_one_name: str, uv_set_two_name: str):
    # param 'set'
    # [{},{},{}, ... {}] = uv_set_one[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, ... ]

    
    
    return

def find_missing_perf_cv_centers(perf_uv_coordinates: list, det_uv_coordinates: list):
    # param 'uv_coordinates'
    # [{},{},{}, ... {}] = uv_set_one[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, ... ]

    for i, det_coordinates_img_id in enumerate(det_uv_coordinates):
        perf_coordinates_img_id = perf_uv_coordinates[i]
        for det_coord in det_coordinates_img_id:
            found_cat_id = False

            for perf_coord in perf_coordinates_img_id:
                #print(det_coord['CAT_ID'])
                val = perf_coord.values()
                if det_coord['CAT_ID'] in perf_coord.values():
                    found_cat_id = True

            if found_cat_id is True:
                continue
            else:
                print('category ID (' + str(det_coord['CAT_ID']) + ') missing for image ID (%i)' % (i+1))


    return 

if __name__ == '__main__':
    ground_truth_cam_poses_fpath = './testdata/_rsg_combined_COCODF-tools_output/CPOSs.txt'
    # adjustment perfect marker projection paths
    perf_rsg_par_path = './testdata/RSG_perfect_2D_marker_proj/RSG' # Filenames must be split with '_' and have the number at last: e.g., IMG001_IMG_001.PAR
    perf_cl_path = './testdata/RSG_perfect_2D_marker_proj/POINT_DATA/CL'
    # adjustment detection 2D centers paths
    # TODO: det_rsg_par_path = './testdata/RSG_detection_2D_centers/RSG'
    det_cl_path = './testdata/_rsg_combined_COCODF-tools_output/cl_det_multrec'

    try:
        if not os.path.isfile(ground_truth_cam_poses_fpath):
            raise FileExistsError('Cam pose file does not exist.')
        if not os.path.isdir(perf_rsg_par_path) \
            or not os.path.isdir(perf_cl_path) \
                or not os.path.isdir(det_cl_path): # TODO: or not os.path.isdir(det_rsg_par_path)
            raise ValueError('Some directory for evaluation does not exist.')
    except Exception as e:
                print('Exception: {}'.format(str(e)), file=sys.stderr)
                sys.exit(1)

    # get adjustment data
    ground_truth_cam_poses = get_cam_poses(ground_truth_cam_poses_fpath)
    # perfect marker projection adjustment
    perf_uv_adjusted_cam_poses = get_cam_poses_rsg(perf_rsg_par_path)
    perf_uv_coordinates = get_uv_coordinates_cl(perf_cl_path)
    # detection centers adjustment
    # TODO: det_uv_adjusted_cam_poses = get_cam_poses_rsg(det_rsg_par_path)
    det_uv_coordinates = get_uv_coordinates_cl(det_cl_path)

    # eval
    eval_cam_poses_mean(ground_truth_cam_poses, perf_uv_adjusted_cam_poses) 
    eval_cv_centers_mean(perf_uv_coordinates, det_uv_coordinates, \
        uv_set_one_name='Perfect marker projection image coordinates', uv_set_two_name='Object detection center image coordinates')
    find_missing_perf_cv_centers(perf_uv_coordinates, det_uv_coordinates)
    print('gooood.')