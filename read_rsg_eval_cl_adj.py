from cmath import pi
import xml.etree.ElementTree as ET
import os
from glob import glob
import math as m
import sys
from pathlib import Path
import shutil

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

def init_output_path(output_path):
    # initialize output_path and clean existing output folder
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

def calc_pixel_dist(p1, p2):
    return abs(p1-p2)

def calc_mean_pixel_dist(summed_distances, N):
    return summed_distances / N

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

def calc_cl_centers_pixel_dist_mean(uv_set_one: list, uv_set_two: list, img_ids: list = None):
    # param 'set'
    # [{},{},{}, ... {}] = uv_set_one[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, ... ] 
    # U, V = float; CAT_ID = int

    # the number of center coordinates must be equal
    for i, img_id_coordinates_set_one in enumerate(uv_set_one):
        img_id_coordinates_set_two = uv_set_two[i] 
        if not len(img_id_coordinates_set_one) == len(img_id_coordinates_set_two):
                print('Error: cl centers not aligned for image id (' + str(i+1) + '). \
                    Got sets with different length (%s, %s)' % (len(img_id_coordinates_set_one), len(img_id_coordinates_set_two)))
                sys.exit(1) 

    # if no image_ids given, calculate for all image examples
    if img_ids is None:
        img_ids = [i+1 for i, j in enumerate(uv_set_one)]
    
    u_pxl_distance = 0
    v_pxl_distance = 0
    N = 0
    for img_id in img_ids:
        img_id_coordinates_set_one = uv_set_one[img_id-1]
        img_id_coordinates_set_two = uv_set_two[img_id-1]
        N += len(img_id_coordinates_set_one)
        
        for i, img_id_coordinate_set_one in enumerate(img_id_coordinates_set_one):
            img_id_coordinate_set_two = img_id_coordinates_set_two[i]
            cat_id_one = img_id_coordinate_set_one['CAT_ID']
            cat_id_two = img_id_coordinate_set_two['CAT_ID']

            if cat_id_one == cat_id_two:
                u_pxl_distance += calc_pixel_dist(img_id_coordinate_set_one['U'], img_id_coordinate_set_two['U'])
                v_pxl_distance += calc_pixel_dist(img_id_coordinate_set_one['V'], img_id_coordinate_set_two['V'])
            else:
                print('Error: Category ID does not match. Not calculating the pixel distance (CAT_ID %s vs. %s)' % (cat_id_one, cat_id_two))
                sys.exit(1)  
            

    return  {'U_PXL_DIST_MEAN': round(u_pxl_distance, 2), 'V_PXL_DIST_MEAN': round(v_pxl_distance, 2), 'IMG_IDS': img_ids}

def centers_pxl_dist_mean_per_img_id(uv_set_one, uv_set_two):

    # the number of center coordinates must be equal
    for i, img_id_coordinates_set_one in enumerate(uv_set_one):
        img_id_coordinates_set_two = uv_set_two[i] 
        if not len(img_id_coordinates_set_one) == len(img_id_coordinates_set_two):
                print('Error: cl centers not aligned for image id (' + str(i+1) + '). \
                    Got sets with different length (%s, %s)' % (len(img_id_coordinates_set_one), len(img_id_coordinates_set_two)))
                sys.exit(1) 

    centers_pxl_dist_mean_per_img_id = []

    for i, _ in enumerate(uv_set_one):
        img_id = i+1
        pxl_mean_img_id = calc_cl_centers_pixel_dist_mean(uv_set_one, uv_set_two, [img_id])
        centers_pxl_dist_mean_per_img_id.append(pxl_mean_img_id)
    
    return centers_pxl_dist_mean_per_img_id

def find_missing_gtruth_cv_centers(gruth_uv_coordinates: list, det_uv_coordinates: list):
    # param 'uv_coordinates'
    # [{},{},{}, ... {}] = uv_set_one[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, ... ]

    for i, det_coordinates_img_id in enumerate(det_uv_coordinates):
        img_id_gtruth_coordinates = gruth_uv_coordinates[i]
        for det_coord in det_coordinates_img_id:
            found_cat_id = False

            for gtruth_coord in img_id_gtruth_coordinates:
                #print(det_coord['CAT_ID'])
                if det_coord['CAT_ID'] in gtruth_coord.values():
                    found_cat_id = True

            if found_cat_id is True:
                continue
            else:
                print('category ID (' + str(det_coord['CAT_ID']) + ') missing for image ID (%i)' % (i+1))
    print('INFO: No missing cl centers in manually projected gtruth centers found (every category ID detected is found in gtruth data).')

def align_gtruth_to_det_projections(gruth_uv_coordinates: list, det_uv_coordinates: list):
    # param 'uv_coordinates'
    # [{},{},{}, ... {}] = uv_set_one[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, ... ]

    aligned_gruth_uv_coordinates = []
    for i, det_coordinates_img_id in enumerate(det_uv_coordinates):
        img_id_gtruth_coordinates = gruth_uv_coordinates[i]
        img_id_aligned_gruth_uv_coordinates = []

        for det_coord in det_coordinates_img_id:
            found_cat_id = False

            for gtruth_coord in img_id_gtruth_coordinates:
                #print(det_coord['CAT_ID'])
                if det_coord['CAT_ID'] in gtruth_coord.values():
                    img_id_aligned_gruth_uv_coordinates.append(gtruth_coord)
                    found_cat_id = True

            if found_cat_id is True:
                continue
            else:
                print('Error: Missing coordinate for category ID (' + str(det_coord['CAT_ID']) + ') \
                        in ground truth image data (img_id %s)' % (i+1))
                sys.exit(1)
        # append found category ID's to aligend gtruth data
        aligned_gruth_uv_coordinates.append(img_id_aligned_gruth_uv_coordinates)

    return aligned_gruth_uv_coordinates

def write_aligned_gtruth_cl_file(aligned_gruth_uv_coordinates: list, out_path: str):
    out_path = out_path + '/cl_det-aligned_manual_gtruth'
    write_cl_file(aligned_gruth_uv_coordinates, out_path)

def write_det_cl_file(aligned_gruth_uv_coordinates: list, out_path: str):
    out_path = out_path + '/cl_det'
    write_cl_file(aligned_gruth_uv_coordinates, out_path)

def write_cl_file(aligned_gruth_uv_coordinates: list, out_path: str):
    # param 'aligned_gruth_uv_coordinates'
    # [{},{},{}, ... {}] = uv_set_one[img_id - 1]
    # [{'CAT_ID': 17, 'U': 1311.0, 'V': 866.0}, ... ]
   
    cl_enc = 'Id;C;L;Status;SigImg\n' 
    init_output_path(out_path)

    for i, img_id_aligned_gruth_uv_coordinates in enumerate(aligned_gruth_uv_coordinates):
        # conc fname.cl
        img_id = '%03i' % (i+1)
        out_cl_fpath = os.path.join(out_path, 'IMG' + str(img_id) + ('_IMG_') + str(img_id) + '.cl')
        for gtruth_uv_coordinates in img_id_aligned_gruth_uv_coordinates:
            # write first line encoding
            write_enc = True if not os.path.isfile(out_cl_fpath) else False
            with open(out_cl_fpath, 'a') as f:
                if write_enc:
                    f.write(cl_enc)
                f.write('%i; ' % gtruth_uv_coordinates['CAT_ID'])
                f.write(('%.2f; %.2f; ') % (gtruth_uv_coordinates['U'], gtruth_uv_coordinates['V']))
                # write RSG comments
                f.write('UM-; 1.000000\n')

if __name__ == '__main__':
    ground_truth_cam_poses_fpath = './testdata/_rsg_combined_COCODF-tools_output/CPOSs.txt'
    # adjustment perfect marker projection paths
    gtruth_rsg_par_path = './testdata/RSG_manual_gtruth_2D_marker_proj/RSG' # Filenames must be split with '_' and have the number at last: e.g., IMG001_IMG_001.PAR
    gruth_cl_path = './testdata/RSG_manual_gtruth_2D_marker_proj/POINT_DATA/CL'
    # adjustment detection 2D centers paths
    # TODO: det_rsg_par_path = './testdata/RSG_detection_2D_centers/RSG'
    det_cl_path = './testdata/_rsg_combined_COCODF-tools_output/cl_det_multrec'
    # general output path (can contain subfolder)
    out_path = './out'

    try:
        if not os.path.isfile(ground_truth_cam_poses_fpath):
            raise FileExistsError('Cam pose file does not exist.')
        if not os.path.isdir(gtruth_rsg_par_path) \
            or not os.path.isdir(gruth_cl_path) \
                or not os.path.isdir(det_cl_path): # TODO: or not os.path.isdir(det_rsg_par_path)
            raise ValueError('Some directory for evaluation does not exist.')
    except Exception as e:
                print('Exception: {}'.format(str(e)), file=sys.stderr)
                sys.exit(1)

    # get adjustment data
    ground_truth_cam_poses = get_cam_poses(ground_truth_cam_poses_fpath)
    # gtruth marker projection adjustment
    gtruth_uv_adjusted_cam_poses = get_cam_poses_rsg(gtruth_rsg_par_path)
    gruth_uv_coordinates = get_uv_coordinates_cl(gruth_cl_path)
    # detection centers adjustment
    # TODO: det_uv_adjusted_cam_poses = get_cam_poses_rsg(det_rsg_par_path)
    det_uv_coordinates = get_uv_coordinates_cl(det_cl_path)

    # align
    find_missing_gtruth_cv_centers(gruth_uv_coordinates, det_uv_coordinates)
    aligned_gruth_uv_coordinates = align_gtruth_to_det_projections(gruth_uv_coordinates, det_uv_coordinates)
    
    # write aligned gtruth and detection data for adjustment 
    # with RSG compatible filenames (see .PAR files)
    write_aligned_gtruth_cl_file(aligned_gruth_uv_coordinates, out_path)
    write_det_cl_file(det_uv_coordinates, out_path)

    # eval
    #pxl_mean_img007 = calc_cl_centers_pixel_dist_mean(aligned_gruth_uv_coordinates, det_uv_coordinates, [7]) 
    pxl_mean_distances = centers_pxl_dist_mean_per_img_id(aligned_gruth_uv_coordinates, det_uv_coordinates)

    eval_cam_poses_mean(ground_truth_cam_poses, gtruth_uv_adjusted_cam_poses)

    # print 'good.'
    print('good.')  