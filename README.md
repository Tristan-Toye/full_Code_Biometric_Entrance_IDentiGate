# full Code Biometric Entrance IDentiGate
This repository has the complete code of our second bachelor P&O3 project at the KU Leuven. 
In this project me aim to make a high-security entrance with biometric authentication linked to an sql database and an online website using heroku.
*** ***
# overview
*** ***
This project will include a dual authentication procedure using face recognition as well as vein authentication. 
The authentication will happen on a computer serving as a local server. The data to authenticate will be gathered by an raspberry pi. This database for authentication wil be located on local server beause of reliablity and safety reasons. 
The connection between the local server and the pi will be done by WiFi using a local mqtt message broker. The local server serves as a central hub for data exchange. 
Logs and other usefull data as well as the necessary login data for the online application will be stored in a online database provided by heroku. For both our online website and local UI we use Flask as our framework. 
The authentication for admin users on the website will consist out of a password, scanning of the ID and facial recognition.
Admin users have the authority to see all the data and will have the power to add new, delete or promote users in the system.
Security user have the authority to see all the data, but cannot change anything.
Recruiting sees only a part of the data, but have the authority to add the basic staff role.
Staff can only see there own data.
