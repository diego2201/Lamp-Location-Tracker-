import subprocess
import serial
import time 
import io
from PIL import Image

# File to store the location flag read in from the Raspberry Pi Pico
inputFile = "/home/capstone/Desktop/Capstone_Lamp/GUI/input.txt"
locationFlag = ''

# Defines a dictionary of some major cities & the path to their images
imagePath = {
    "New York City, USA": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/NYC.jpeg',
    "San Francisco, USA": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/SanFran.jpeg',
    "Norman, Oklahoma, USA": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/OU.jpeg',
    "Los Angeles, USA": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/LA.jpeg',
    "Chicago, USA": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/Chicago.jpeg',    
    "London, United Kingdom": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/London.jpeg',
    "Tokyo, Japan": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/Tokyo.jpeg',
    "Dubai, United Arab Emirates": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/Dubai.jpeg',
    "Paris, France": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/Pari.jpeg',
    "Sydney, Australia": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/Syn.jpeg',
    "Devon": '/home/capstone/Desktop/Capstone_Lamp/GUI/Images/devon'
}

# Defines a dictionary to correlate cities with their corresponding flags
locationDict = {
    'a': "New York City, USA",
    'b': "San Francisco, USA",
    'c': "Norman, Oklahoma, USA",
    'd': "Los Angeles, USA",
    'e': "Chicago, USA",
    'f': "London, United Kingdom",
    'g': "Tokyo, Japan",
    'h': "Dubai, United Arab Emirates",
    'i': "Paris, France",
    'j': "Sydney, Australia",
    'k': "University of Oklahoma, USA",
    '!': 'GPS Error', #Flag bit to denote that there has been an error reading from GPS
    'y': "Devon", #Pres mode 
    'z': 'z' #Flag bit to denote no user input
}

"""
Function to get the dictionary key based off of the read in value
"""
def getKey(target):
    for key, value in locationDict.items():
        if value == target:
            return key
    return None

"""
Function to open an image based on the passed in selected location
"""
def openImage(location, result):
    # Gets the image path for the selected location from the imagePath dict
    path = imagePath.get(location)

    # Checks if there is a valid image path returned from the dict
    if path:
        try:
            # If there is, initialize it as a new Image object
            img = Image.open(path)
            
            # Resizes the image to a specified size (400x400) using Antialiasing for better quality
            img = img.resize((400, 400), Image.ANTIALIAS)
            
            # Converts the image to bytes and stores it in memory using BytesIO
            imgByte = io.BytesIO()
            img.save(imgByte, format='JPEG') # Reformats the image 
            imgByte.seek(0)

            # Calls the 'feh' image viewer subprocess and displays the image using its standard input
            subprocess.run(['feh', '-'], input=imgByte.read(), check=True)
        except subprocess.CalledProcessError as e:
            # If an error occurs during subprocess execution, display an error message
            result.config(text=f"Error opening image: {e}")
    else:
        # Display an error message if the image path is not found in the dictionary
        result.config(text='Image not found.')
"""
Function to read in the input.txt file
"""
def readFile():
    # Opens the file in read bit mode 
    with open(inputFile, 'rb') as file:
        # Decodes the read in character to help avoid datatype conflicts
        data = file.read().decode('utf-8', errors='ignore')

    # Parses the data and stores it 
    parsedData = ''.join(char for char in data if char.isprintable())
    #print(locationDict.get(parsedData)) #Debug statement

    # Returns the read in lecture based off of the location dictonary
    return locationDict.get(parsedData)

"""
Function to establish serial communication with Pi Pico and reads in the 
location flag generated by the Pico
"""
def getFlag():
    global locationFlag # Calls in the locationFlag as a global variable 

    # Configures the serial communication
    port = "/dev/ttyACM0" # Sets the port of the Pico 
    baudrate = 115200   # Sets the baud rate 
    serialCon = serial.Serial(port, baudrate) # Initializes the serial connection

    # Opens the input.txt file to write the received data
    deskFile = open(inputFile, "wb")

    # Reads and write data until the transfer is complete
    data = serialCon.read(3) # Reads in all bits from the serial port 
    locationFlag = serialCon.read(1) # Reads in just the char 

    #print("locflag:", data) # Debug statement

    deskFile.seek(0) # Overwrites the loction flag on the first line
    deskFile.write(data) # Writes the data to the file 

    # Close the files/serial connection
    deskFile.close()
    serialCon.close()

"""
Function to set establish serial communication with Pi Pico and writes/sets
the location flag as generated by the GUI 
"""
def setFlag(loc, clear):
    port = "/dev/ttyACM0"
    baudrate = 115200
    serialCon = serial.Serial(port, baudrate)

    # If the passed in flag is 0 we set the flag based off GUI input 
    if clear == 0:
        flag = getKey(loc) #Gets the key based off of the value 
        #print(flag) #Debug statement
        serialCon.write((flag + ',').encode()) # Writes to the file 

        # Closes the seriual connection 
        serialCon.close()
        time.sleep(1)
        serialCon.close()
    elif clear == 1:
        # Sets the flag to 'z' denoting that we should display data based off
        # of read in GPS data 
        serialCon.write((locationDict.get('z') + ',').encode())

        # Closes the serial connection
        serialCon.close()
        time.sleep(1)
        serialCon.close()    
