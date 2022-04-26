from cmath import pi
import xml.etree.ElementTree as ET
import os
from glob import glob
import math as m
import sys

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

def calc_pixel_dist(p1, p2):
    return p1-p2

def calc_mean_pixel_dist(distances, N):
    return distances / N

def calc_per_single_image_example():
    return 0

def calc_per_multiple_image_examples():
    return 0

def get_cam_poses_rsg(rsg_path):
    # get adjusted poses from XML
    all_par_paths = get_par_paths(rsg_path)
    if not len(all_par_paths):
        print('Error: No par-files found in directory (%s)' % rsg_path)
        sys.exit(1)

    adjusted_cam_poses = []
    for par_path in all_par_paths:
        root = ET.parse(par_path).getroot()
        # --- some examples
        # print(root.tag) outputs 'PhysicalEntity'
        # get all attributes of PhysicalEntity:
        #   print(root.attrib) outputs '{relpath="." prefix="unknown" size="0" type="RSGimagemodel" version="3.1" state="----------"}'

        for attributes in root.findall('Attributes'): # iterate over all the nodes with tag name 'Attributes'
            if attributes.get('Set') == 'AdjustedGeometry': # extract the attribute 'Set' of 'Attributes'-Tag; compare with desired Set name 'AdjustedGeometry'
                adjusted_cam_pose = {}
                for tag in attributes.findall('Tag'): # iterate over all the nodes with tag name 'Tag'
                    if tag.get('id') == 'ORBX': adjusted_cam_pose['X'] = round(float(tag.text), 4) # get text of 'Tag' with desired 'id'
                    if tag.get('id') == 'ORBY': adjusted_cam_pose['Y'] = round(float(tag.text), 4)
                    if tag.get('id') == 'ORBZ': adjusted_cam_pose['Z'] = round(float(tag.text), 4)
                    if tag.get('id') == 'OMEGA': adjusted_cam_pose['OMEGA'] = round(float(tag.text) * 180/pi, 4)
                    if tag.get('id') == 'PHI': adjusted_cam_pose['PHI'] = round(float(tag.text) * 180/pi, 4)
                    if tag.get('id') == 'KAPPA': adjusted_cam_pose['KAPPA'] = round(float(tag.text) * 180/pi, 4)
                adjusted_cam_poses.append(adjusted_cam_pose)

    return adjusted_cam_poses

def get_cam_poses_txt(ground_truth_cam_poses_fpath):
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

    return sorted(ground_truth_cam_poses, key=lambda d: d['ID'])


if __name__ == '__main__':
    ground_truth_cam_poses_fpath = './testdata/_rsg_combined_COCODF-tools_output/custom_CPOSs.txt'
    rsg_path = './testdata/RSG_perfect_2D_marker_proj/RSG'
    cl_path = ''

    try:
        if not os.path.isfile(ground_truth_cam_poses_fpath):
            raise FileExistsError('Cam pose file does not exist.')
        if not os.path.isdir(rsg_path):
            raise ValueError('Directory for RSG does not exist.')
    except Exception as e:
                print('Exception: {}'.format(str(e)), file=sys.stderr)
                sys.exit(1)

    ground_truth_cam_poses = get_cam_poses_txt(ground_truth_cam_poses_fpath)
    adjusted_cam_poses = get_cam_poses_rsg(rsg_path)