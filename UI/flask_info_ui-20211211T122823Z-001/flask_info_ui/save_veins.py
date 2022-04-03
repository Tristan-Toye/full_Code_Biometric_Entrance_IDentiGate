import cv2
import os



def image_to_matrix(name):
    known_veins = []

    list = [file for file in os.listdir('/home/pi/Desktop/vein/known/optimized') if file != '.DS_Store']
    for filename in list:
        # Load an image
        image = f'/home/pi/Desktop/vein/known/optimized/{filename}'
        print(image)
        #optimize
        optimized_image = cv2.imread(image,0)
        orb = cv2.ORB_create()
        keypoint_optimized_image, descriptor_optimized_image = orb.detectAndCompute(optimized_image, None)
        list_pt=[i.pt for i in keypoint_optimized_image]
        known_veins.append([descriptor_optimized_image,list_pt])
    return [known_veins,name]


