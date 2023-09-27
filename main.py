import numpy as np
import cv2
import random
import argparse
from numpy.linalg import svd

def make_parser():
    parser = argparse.ArgumentParser("Image to World Demo")
    parser.add_argument("--img_path", type=str, default="image/sample.jpg", help="demo image path")
    parser.add_argument("--sample", type=bool, default=False)
    parser.add_argument("--trial_number", type=int, default=1, help='number of trials to run')
    parser.add_argument("--remove_number", type=int, default=0, help='number of remove sample for each trial')
    parser.add_argument("--verbose", type=bool, default=True, help='print homography matrix')
    parser.add_argument("--save_path", type=str, default=None, help='output image path')

    return parser

def i2w(image_coord, homography_matrix):

    '''
    transform image coorinate (x_image, y_image, 1) into world coordinate (x_world, y_world)
    '''

    inv_homography_matrix = np.linalg.inv(homography_matrix)
    img_vector = np.array(image_coord).reshape(3, 1)
    world_vector = np.dot(inv_homography_matrix, img_vector)
    world_vector /= world_vector[2, 0]

    return world_vector[:2]

def w2i(world_coords, homography_matrix):

    '''
    transform world coorinate (x_world, y_world) into image coordinate (x_image, y_image)
    '''

    world_coords_homogeneous = np.array([world_coords[0], world_coords[1], 1])
    image_coords_homogeneous = np.dot(homography_matrix, world_coords_homogeneous)
    image_coords_2d = image_coords_homogeneous / image_coords_homogeneous[2]
    x_2d, y_2d, _ = image_coords_2d

    return [int(x_2d), int(y_2d)]

def calculate_homography_matrix(image_coordinates, world_coordinates):
    if len(image_coordinates) != len(world_coordinates):
        raise ValueError("Input coordinate lists must have the same length")

    num_points = len(image_coordinates)
    
    A = []
    
    for i in range(num_points):
        x, y, _ = image_coordinates[i]
        X, Y, _ = world_coordinates[i]
        A.append([-X, -Y, -1, 0, 0, 0, x*X, x*Y, x])
        A.append([0, 0, 0, -X, -Y, -1, y*X, y*Y, y])

    A = np.array(A)
    
    _, _, Vt = svd(A)

    H = Vt[-1].reshape(3, 3)

    return H

def get_middle_pts(pt1,pt2,n):
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    ddx,ddy = dx/(n-1),dy/(n-1)
    pts = [(pt1[0]+i*ddx,pt1[1]+i*ddy,1) for i in range(n)]
    return pts


def draw_ground_plane_on_image(image, ground_coords):
    cv2.polylines(image, [np.array(ground_coords)], isClosed=True, color=(0, 255, 0), thickness=2)
    return image

def draw_ground_line_on_image(image, ground_coords, homo):
    
    lower_l, lower_r, upper_r, upper_l = ground_coords
    left_pts = get_middle_pts(lower_l,upper_l,10)
    right_pts = get_middle_pts(lower_r,upper_r,10)
    lower_pts = get_middle_pts(lower_r,lower_l,10)
    upper_pts = get_middle_pts(upper_r,upper_l,10)

    for left_pt,right_pt in zip(left_pts,right_pts):
        image = cv2.line(image,w2i(left_pt,homo),w2i(right_pt,homo),(0,255,0),2)

    for lower_pt,upper_pt in zip(lower_pts,upper_pts):
        image = cv2.line(image,w2i(lower_pt,homo),w2i(upper_pt,homo),(0,255,0),2)
    
    return image

if __name__ == "__main__":

    args = make_parser().parse_args()

    image_coordinates_all = np.loadtxt('coords/image_coordinate.txt',delimiter=',')
    world_coordinates_all = np.loadtxt('coords/world_coordinate.txt',delimiter=',')
    ground_corners = np.loadtxt('coords/ground_corners.txt',delimiter=',')

    assert len(image_coordinates_all) == len(world_coordinates_all), 'the length of image and world coordinate does not match.'
    assert len(ground_corners) == 4, f'length of ground corners should be four, instead got {len(ground_corners)}.'
    assert cv2.imread(args.img_path) is not None, f'image path {args.img_path} does not exists.'
    assert len(image_coordinates_all) - args.remove_number >= 4, 'number of image coordinates - number of remove sample should be bigger then 4'

    n = args.trial_number

    for trial_idx in range(n): 

        image = cv2.imread(args.img_path)

        image_coordinates, world_coordinates = zip(*random.sample(list(zip(image_coordinates_all, world_coordinates_all)), len(image_coordinates_all) - args.remove_number))

        homography_matrix = calculate_homography_matrix(image_coordinates, world_coordinates)

        if args.verbose:
            print(homography_matrix)

        # Calculate the ground plane coordinates in the image
        ground_coords = [w2i(ground_corner,homography_matrix) for ground_corner in ground_corners]

        # Draw the ground plane on the image
        image = draw_ground_plane_on_image(image, ground_coords)
        image = draw_ground_line_on_image(image, ground_corners, homography_matrix)

        # Display the image with the ground plane
        cv2.imshow(f'trial {trial_idx}. Ground Plane', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if args.save_path:
            cv2.imwrite(args.save_path,image)