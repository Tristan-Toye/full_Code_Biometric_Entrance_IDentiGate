

"""
# this code is based on https://youtu.be/16s3Pi1InPU and https://www.hackster.io/ibrahimirfan/low-cost-palm-vein-authentication-system-74e917

"""
from matplotlib import pyplot as plt
from picamera import PiCamera
import time
from skimage.metrics import structural_similarity
import numpy as np
import cv2
import os
from flask_info_ui import q_vein_messaging, q_vein_messaging_add
from PIL import Image
TRESHHOLD_ORB_COMPARING=0.05

AANTAL_FOTO=5
DEBUG=False
CHECK_TIME=False
TEST="final_database"
time.sleep(2)
database_path='/home/pi/Desktop/vein/'+TEST
def make_vein_database():
    try:
        os.makedirs("/home/pi/Desktop/vein/known/normal")
        os.makedirs("/home/pi/Desktop/vein/known/croped")
        os.makedirs("/home/pi/Desktop/vein/known/optimized")
    except:
        pass
    with PiCamera() as cam:
        cam.brightness = 20
        cam.contrast=100
        cam.exposure_mode="verylong"
        time.sleep(1)
        
        for i in range(1,AANTAL_FOTO+1):
            cam.exposure_mode="verylong"
            p="/home/pi/Desktop/vein/known/normal/"+str(i)+".jpg"
            cam.capture(p)
            img=cv2.imread(p)
            if DEBUG:
                cv2.imshow("t",img)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            
            h=img.shape[0]
            w=img.shape[1]
            crop=img[int(h*0.31):int(h*0.57),int(0.29*w):int(0.52*w)]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            if DEBUG:
                cv2.imshow("t",crop)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            
            print("image croped")
            cv2.imwrite("/home/pi/Desktop/vein/known/croped/croped"+str(i)+".jpg",crop)
            image = optimize_image_vein_data("/home/pi/Desktop/vein/known/croped/croped"+str(i)+".jpg",i)
            print(i)
            image = Image.fromarray(image)
            print(image)
            
            send_dict = {'i': i, 'image': image}
           
            q_vein_messaging_add.put(send_dict,block=True)
    

def vein_recognition_datacolection():
    try:
        os.makedirs("/home/pi/Desktop/vein/unknown/normal")
        os.makedirs("/home/pi/Desktop/vein/unknown/croped")
        os.makedirs("/home/pi/Desktop/vein/unknown/optimized")
    except:
        pass
    with PiCamera() as cam:
        cam.brightness = 20
        cam.contrast=100
        time.sleep(0.5)
        cam.exposure_mode="verylong"
        time.sleep(0.5)
        
        for i in range(1,AANTAL_FOTO+1):
            p="/home/pi/Desktop/vein/unknown/normal"+str(i)+".jpg"
            cam.exposure_mode="verylong"
            cam.capture(p)
            img=cv2.imread(p)
            if DEBUG:
                cv2.imshow("t",img)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            
            #print(img.shape)
            h=img.shape[0]
            w=img.shape[1]
            crop=img[int(h*0.31):int(h*0.57),int(0.29*w):int(0.52*w)]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            if DEBUG:
                cv2.imshow("t",crop)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            
            print(crop.size)
            cv2.imwrite("/home/pi/Desktop/vein/unknown/croped/croped"+str(i)+".jpg",crop)
            image = optimize_image_vein_rec("/home/pi/Desktop/vein/unknown/croped/croped"+str(i)+".jpg",i)
            print(i)
            image = Image.fromarray(image)
            print(image)
            
            send_dict = {'i': i, 'image': image}
            q_vein_messaging.put(send_dict,block=True)
            
# https://youtu.be/16s3Pi1InPU +


def optimize_image_vein_data(image,i):
    print("hey")
    start_time = time.time()
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    noise = cv2.fastNlMeansDenoising(gray)
    noise = cv2.cvtColor(noise, cv2.COLOR_GRAY2BGR)
    # equalist hist
    
    kernel = np.ones((7, 7), np.uint8)
    img = cv2.morphologyEx(noise, cv2.MORPH_OPEN, kernel)
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    # invert
    inv = cv2.bitwise_not(img_output)
    # erode
    gray = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
    erosion = cv2.erode(gray, kernel, iterations=1)
    # skel
    
    img = gray.copy()
    skel = img.copy()
    skel[:, :] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    iterations = 0
    while True:
        eroded = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
        temp = cv2.morphologyEx(eroded, cv2.MORPH_DILATE, kernel)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img[:, :] = eroded[:, :]
        if cv2.countNonZero(img) <= 0:
            break
        if DEBUG:
            print(cv2.countNonZero(img))
    if CHECK_TIME:
        print("skelitonize time", "--- %s seconds ---" % (time.time() - start_time))
    ret, thr = cv2.threshold(skel, 5, 255, cv2.THRESH_BINARY);
    if CHECK_TIME:
        print("Optimisation time", "--- %s seconds ---" % (time.time() - start_time))
    if DEBUG:
        cv2.imshow("thr.jpg", thr)
        cv2.waitKey(2000)
        cv2.destroyWindow("thr.jpg")
    cv2.imwrite("/home/pi/Desktop/vein/known/optimized/optimized"+str(i)+".jpg",thr)
    #cv2.imwrite("/home/pi/Desktop/matisse/thrmatisse"+str(i)+".jpg",thr)
    return thr
def optimize_image_vein_rec(image,i):
    print("optimize_image_vein_rec")
    start_time = time.time()
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    noise = cv2.fastNlMeansDenoising(gray)
    noise = cv2.cvtColor(noise, cv2.COLOR_GRAY2BGR)
    # equalist hist
    
    kernel = np.ones((7, 7), np.uint8)
    img = cv2.morphologyEx(noise, cv2.MORPH_OPEN, kernel)
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    # invert
    inv = cv2.bitwise_not(img_output)
    # erode
    gray = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
    erosion = cv2.erode(gray, kernel, iterations=1)
    # skel
    
    img = gray.copy()
    skel = img.copy()
    skel[:, :] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    iterations = 0
    while True:
        eroded = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
        temp = cv2.morphologyEx(eroded, cv2.MORPH_DILATE, kernel)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img[:, :] = eroded[:, :]
        if cv2.countNonZero(img) <= 0:
            break
        if DEBUG:
            print(cv2.countNonZero(img))
    if CHECK_TIME:
        print("skelitonize time", "--- %s seconds ---" % (time.time() - start_time))
    ret, thr = cv2.threshold(skel, 5, 255, cv2.THRESH_BINARY);
    if CHECK_TIME:
        print("Optimisation time", "--- %s seconds ---" % (time.time() - start_time))
    if DEBUG:
        cv2.imshow("thr.jpg", thr)
        cv2.waitKey(2000)
        cv2.destroyWindow("thr.jpg")
    cv2.imwrite("/home/pi/Desktop/vein/unknown/optimized/optimized"+str(i)+".jpg",thr)
    #cv2.imwrite("/home/pi/Desktop/matisse/thrmatisse"+str(i)+".jpg",thr)
    return thr
# Works well with images of different dimensions
def compare_image_vein_ORB(lijst, img2):
    start_time = time.time()
    # SIFT is no longer available in cv2 so using ORB
    orb = cv2.ORB_create()

    # detect keypoints and descriptors
    kp_b, desc_b = orb.detectAndCompute(img2, None)

    # define the bruteforce matcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # perform matches.
   
        
    matches = bf.match(lijst[0], desc_b)
    matches2=[]
    kp_a=lijst[1]
    for i in matches:
        img1_idx=i.queryIdx
        img2_idx=i.trainIdx
        (x1,y1)=kp_a[img1_idx]
        (x2,y2)=kp_b[img2_idx].pt
        distance=((x1-x2)**2+(y1-y2)**2)**(1/2)
        if distance < 30:
            matches2.append(i)
    """
    result=cv2.drawMatches(img1,kp_a,img2,kp_b,matches2,img2,flags=2)
    plt.rcParams['figure.figsize']=[4.0,7.0]
    plt.title('best match')
    plt.imshow(result)
    plt.show()
    """
    # Look for similar regions with distance < 50. Goes from 0 to 100 so pick a number between.
    similar_regions = [i for i in matches2 if i.distance < 70]
    return len(similar_regions) / len(matches)
    if len(matches) == 0:
        print(0)
        
        #print("Comparing time", "--- %s seconds ---" % (time.time() - start_time))
        return False
    elif len(similar_regions) / len(matches) >= TRESHHOLD_ORB_COMPARING:
        #print("Comparing time", "--- %s seconds ---" % (time.time() - start_time))
        return True
    else:
        #print("Comparing time", "--- %s seconds ---" % (time.time() - start_time))
        return False


# Needs images to be same dimensions
def compare_image_vein_struct_sim(img1, img2):
    sim, diff = structural_similarity(img1, img2, full=True)
    return sim
def compare_2(des1,img2):
    # Initiate SIFT detector
    orb = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp2, des2 = orb.detectAndCompute(img2,None)
    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(des1,des2,k=2)

    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]
    good=0
    # ratio test as per Lowe's paper
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.9*n.distance:
            matchesMask[i]=[1,0]
            good+=1
    return good/len(matches)
"""
for i in range(1,6):
    img=optimize_image_vein('/home/pi/Downloads/crop'+str(i)+'.jpg',i)
"""

'''
list=[]
#img=optimize_image_vein('/home/pi/Downloads/crop1.jpg',1)
for i in range(1,6):
    for j in range(1,6):
        img00=cv2.imread('/home/pi/Desktop/vein/11LED+U-vorm-50ohm/matisse_L15.2/optimized/matisse_Loptimized'+str(j)+'.jpg',0)
        img01=cv2.imread('/home/pi/Desktop/vein/11LED+U-vorm-50ohm/niels15.1/optimized/nielsoptimized'+str(i)+'.jpg',0)
        orb=compare_image_vein_ORB(img01,img00)
        list.append(orb)
        ssim= compare_image_vein_struct_sim(img01,img00)
print(list)
print(sum(list)/len(list))
img00 = cv2.imread('/home/pi/Desktop/thrmatisse2.jpg', 0)
img01 = cv2.imread('/home/pi/Desktop/thrmatisse3.jpg', 0)
'''
def check_with(vein_list):
    
    
    list=[]
    for vein_pair in vein_list:
        for j in range(1,AANTAL_FOTO +1):
            img0=cv2.imread("/home/pi/Desktop/vein/unknown/optimized/optimized"+str(j)+".jpg",0)
            
        #print(img_path+'/'+name_folder[:-4]+'optimized'+str(i)+'.jpg',0)
            
        
            orb=compare_image_vein_ORB(vein_pair,img0)
            list.append(orb)
            
    print(list)        
    print(sum(list)/len(list))
  
    if sum(list)/len(list) <0.1:
        return False
    else:
        return True
'''
#KIJKEN WELKE BESTE PAST WSS ORB MA HOUDEN STRUCT_SIM VOOR ZEKERHEID
orb=compare_image_vein_ORB(img01,img00)
ssim= compare_image_vein_struct_sim(img01,img00)
print("Similarity using ORB is: ", orb)
print("Similarity using SSIM is: ", ssim)
'''
"""
print(vein_recognition('arnev'))
"""
"""
make_vein_database("tristan")

"""