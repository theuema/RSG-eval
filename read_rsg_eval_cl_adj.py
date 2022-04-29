from cmath import pi
from re import I
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
    # param p1, p2 = float/int pixel values
    return abs(p1-p2)


def calc_mean_distances(distances):
    # param distances
    # dist = distances[img_id - 1]
    return sum(distances)/len(distances)


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


def get_cam_poses_txt(cam_poses_txt_fpath):
    # returns a list of dicts containing camera
    # poses from a file
    # where the index is the img_id - 1
    # {'ID': 1, 'X': -1.2461, 'Y': 0.3497, 'Z': 1.2641, 'OMEGA': -91.9631, 'PHI': -3.2676, 'KAPPA': 306.7033}

    # Get ground truth camera poses
    f = open(cam_poses_txt_fpath, 'r')
    cam_poses = []
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
        cam_poses.append(ground_truth_cam_pose)

    return cam_poses # sorted(cam_poses, key=lambda d: d['ID'])


def get_UV_coordinates_cl(cl_path):
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
    for cl_fpath in cl_fpaths:
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


def calc_cam_poses_dist(ground_truth_cam_poses: list, adjusted_cam_poses: list):
    # param 'cam poses'
    # {} = cam_poses[img_id - 1] 
    # {'ID': 1, 'X': -1.2461, 'Y': 0.3497, 'Z': 1.2641, 'OMEGA': -91.9631, 'PHI': -3.2676, 'KAPPA': 306.7033} 

    distances = []
    for i, ground_truth_cam_pose in enumerate(ground_truth_cam_poses):
        adjusted_cam_pose = adjusted_cam_poses[i] 
        
        ground_truth_coord = (ground_truth_cam_pose['X'], ground_truth_cam_pose['Y'], ground_truth_cam_pose['Z'])
        adjusted_coord = (adjusted_cam_pose['X'], adjusted_cam_pose['Y'], adjusted_cam_pose['Z'])
        distances.append(m.dist(ground_truth_coord, adjusted_coord))

    return distances


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
            

    return  {'U_PXL_DIST_MEAN': round(u_pxl_distance/N, 2), 'V_PXL_DIST_MEAN': round(v_pxl_distance/N, 2), 'IMG_IDS': img_ids}


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
    print('[INFO]: No missing cl centers in manually projected gtruth centers found (every category ID detected is found in gtruth data).')


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


def write_RSG_cl_files(aligned_gruth_uv_coordinates: list, out_path: str, folder_name: str):
    out_path = out_path + folder_name 
    write_cl_files(aligned_gruth_uv_coordinates, out_path)


def write_cl_files(aligned_gruth_uv_coordinates: list, out_path: str):
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


def print_cam_pos_distances(cam_poses_set_one, cam_poses_set_two, s: str):
    m_distances = calc_cam_poses_dist(cam_poses_set_one, cam_poses_set_two)
    cm_distances = [round(d * 100, 4) for d in m_distances]
    cm_mean_distance = round(calc_mean_distances(cm_distances), 4)
    print(s)
    print('distances per camera pos (cm): %s' % cm_distances)  
    print('mean distance: %scm' % cm_mean_distance)


def print_pxl_distances(UV_coordinates_set_one, UV_coordinates_set_two):
    pxl_mean_distances_per_img_id_dicts = centers_pxl_dist_mean_per_img_id(UV_coordinates_set_one, UV_coordinates_set_two)
    pxl_mean_distances_U_per_img_id_list = [mean_distances_per_img_id['U_PXL_DIST_MEAN'] for mean_distances_per_img_id in pxl_mean_distances_per_img_id_dicts]
    pxl_mean_distances_V_per_img_id_list = [mean_distances_per_img_id['V_PXL_DIST_MEAN'] for mean_distances_per_img_id in pxl_mean_distances_per_img_id_dicts]
    pxl_mean_distance_U = calc_mean_distances(pxl_mean_distances_U_per_img_id_list)
    pxl_mean_distance_V = calc_mean_distances(pxl_mean_distances_V_per_img_id_list)

    print('mean pixel distances U per image_id: %s' % pxl_mean_distances_U_per_img_id_list)
    print('mean pixel distances V per image_id: %s' % pxl_mean_distances_V_per_img_id_list)
    print('mean pixel distance U over image_ids: %s' % round(pxl_mean_distance_U, 2))
    print('mean pixel distance V over image_ids: %s' % round(pxl_mean_distance_V, 2))



if __name__ == '__main__':
    # YES: process COCODF-tools output to RSG compatible .cl files and save in out_path
    # NO: process RSG adjustment outputs
    process_COCODF_to_output = False

    # ------ INITIAL PATHS (COCODF-tools & manual marker projection)
    # define paths COCODF-tools outputs
    OptiTrack_cam_poses_txt_fpath = './testdata/_rsg_combined_COCODF-tools_output/CPOSs.txt'
    det_cl_path = './testdata/_rsg_combined_COCODF-tools_output/cl_det_multrec'
    # general output path (can contain subfolder)
    out_path = './out'

    # define paths manual adjustment of perfect marker projection (Gutjhar)
    gtruth_rsg_par_path = './testdata/RSG_manual_gtruth_2D_marker_proj/RSG' # Filenames must be split with '_' and have the number at last: e.g., IMG001_IMG_001.PAR
    gruth_cl_path = './testdata/RSG_manual_gtruth_2D_marker_proj/POINT_DATA/CL'

    # ------ PATHS (RSG RESULTS)
    det_rsg_par_path = './testdata/RSG_RESULTS/cl_det_RSG' # adjustment from files generated: 'write_RSG_det_cl_files(det_UV_coordinates, out_path)'
    alignedGtruth_rsg_par_path = './testdata/RSG_RESULTS/cl_detAlignedGtruth_RSG' # adjustment from files generated: \
                                                                                        # 'write_RSG_detAligned_gtruth_cl_files(detAligned_gtruth_UV_coordinates, out_path)' 

    try:
        if not os.path.isfile(OptiTrack_cam_poses_txt_fpath):
            raise FileExistsError('Cam pose file does not exist.')
        if not os.path.isdir(gtruth_rsg_par_path) \
            or not os.path.isdir(gruth_cl_path) \
                or not os.path.isdir(det_cl_path) \
                    or not os.path.isdir(det_rsg_par_path) \
                        or not os.path.isdir(alignedGtruth_rsg_par_path): 
            raise ValueError('Some directory for evaluation does not exist.')
    except Exception as e:
                print('Exception: {}'.format(str(e)), file=sys.stderr)
                sys.exit(1)

    # ------ INITIAL READS
    # read gtruth OptiTrack camera data (= measured/calculated pose XYZ+OPK of camera frame origin) 
    gtruth_OptiTrack_cam_poses = get_cam_poses_txt(OptiTrack_cam_poses_txt_fpath)
    
    # read gtruth cl files with centers of manually projected object markers to the image plane
    gtruth_UV_coordinates = get_UV_coordinates_cl(gruth_cl_path)

    # read detected cl files
    det_UV_coordinates = get_UV_coordinates_cl(det_cl_path)
    # align (find potential missing object centers in gtruth_UV_coordinates; align them to detection centers 
    # (result = only those centers intersecting with detected category ID's are part of detAligned_gtruth_UV_coordinates)
    find_missing_gtruth_cv_centers(gtruth_UV_coordinates, det_UV_coordinates)
    detAligned_gtruth_UV_coordinates = align_gtruth_to_det_projections(gtruth_UV_coordinates, det_UV_coordinates)

    if process_COCODF_to_output:
        # write aligned gtruth and detection data for adjustment with RSG compatible filenames (see .PAR files)
        write_RSG_cl_files(det_UV_coordinates, out_path, '/cl_det')
        write_RSG_cl_files(detAligned_gtruth_UV_coordinates, out_path, '/cl_detAlignedGtruth')
        print('det & alignedGtruth UV_coordinates written as .cl-files (%s)' % out_path) 
    else:
        # ------ ADJUSTMENT READS
        # read XYZ+OPK adjustment of det_UV_coordinates (= displaced/weaker object centers than gtruth marker projection; yields cam_poses less accurate)
        det_cam_poses = get_cam_poses_rsg(det_rsg_par_path)
        # read XYZ+OPK adjustment of aligned_gruth_UV_coordinates
        detAligned_gtruth_UV_cam_poses = get_cam_poses_rsg(alignedGtruth_rsg_par_path)

        # --- POSE ESTIMATION DISTANCES
        # read gtruth marker projection adjustment (= best possible esimation of OptiTrack_cam_poses)
        gtruth_UV_cam_poses = get_cam_poses_rsg(gtruth_rsg_par_path) 
        # gtruth_OptiTrack_cam_poses vs. gtruth_UV_cam_poses
        s = '''\n------ gtruth_OptiTrack_cam_poses vs. gtruth_UV_cam_poses
            "Best possible pose estimation compared to OptiTrack measured camera poses (used gtruth object centers (manually projected) for adjustment)"\n''' 
        print_cam_pos_distances(gtruth_OptiTrack_cam_poses, gtruth_UV_cam_poses, s)

        # gtruth_OptiTrack_cam_poses vs. detAligned_gtruth_UV_cam_poses
        s = '''\n------ gtruth_OptiTrack_cam_poses vs. detAligned_gtruth_UV_cam_poses
            "Pose estimation for object centers generated from detection-aligned gtruth"\n'''
        print_cam_pos_distances(gtruth_OptiTrack_cam_poses, detAligned_gtruth_UV_cam_poses, s)
        # calculate the PIXEL DISTANCE of the object centers used for adjustment

        # gtruth_UV_cam_poses vs. detAligned_gtruth_UV_cam_poses
        s = '''\n------ gtruth_UV_cam_poses vs. detAligned_gtruth_UV_cam_poses
            "Pose estimation diff between gtruth and detection-aligned gtruth object centers"\n'''
        print_cam_pos_distances(gtruth_UV_cam_poses, detAligned_gtruth_UV_cam_poses, s) 
        # calculate the PIXEL DISTANCE of the object centers used for adjustment

        # gtruth_OptiTrack_cam_poses vs. det_cam_poses
        s = '''\n------ gtruth_OptiTrack_cam_poses vs. det_cam_poses
            "Pose estimation for object centers generated from object detection"\n'''
        print_cam_pos_distances(gtruth_OptiTrack_cam_poses, det_cam_poses, s)

        # # det_cam_poses vs. gtruth_UV_cam_poses
        # s = '''------ det_cam_poses vs. gtruth_UV_cam_poses\n
        #             "Pose estimation diff between detected and gtruth object centers"'''
        # print_cam_pos_distances(det_cam_poses, gtruth_UV_cam_poses, s)
        # # calculate the PIXEL DISTANCE of the object centers used for adjustment

        # det_cam_poses vs. detAligned_gtruth_UV_cam_poses 
        print('''\n------ det_cam_poses vs. detAligned_gtruth_UV_cam_poses\n
            "Pose estimation diff between detected and detection-aligned gtruth object centers"''')
        s = '''(gtruth_OptiTrack_cam_poses vs. detAligned_gtruth_UV_cam_poses)'''
        print_cam_pos_distances(gtruth_OptiTrack_cam_poses, detAligned_gtruth_UV_cam_poses, s)
        s = '''(gtruth_OptiTrack_cam_poses vs. det_cam_poses)'''
        print_cam_pos_distances(gtruth_OptiTrack_cam_poses, det_cam_poses, s)
        #print_cam_pos_distances(gtruth_OptiTrack_cam_poses, detAligned_gtruth_UV_cam_poses, s)
        # calculate the PIXEL DISTANCE of the object centers used for adjustment
        print('''(Pixel distances of centers used for adjusting det_cam_poses & detAligned_gtruth_UV_cam_poses)''')
        print_pxl_distances(det_UV_coordinates, detAligned_gtruth_UV_coordinates)

    # print 'good.'
    print('''------\n
                good.''')