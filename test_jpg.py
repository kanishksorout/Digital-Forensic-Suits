#This program is in testing condition used to extract out the JPG files from the raw disk file
#drive = r"D:\new2\entire_disk.dd"     # Open drive as raw bytes
drive = "\\\\.\\F:"
fileD = open(drive, "rb")
size = 512              # Size of bytes to read
byte = fileD.read(size) # Read 'size' bytes
offs = 0                # Offset location
drec = False            # Recovery mode
rcvd = 0                # Recovered file ID
while byte:
    found = byte.find(b'\xff\xd8\xff\xe0\x00\x10\x4a\x46')
    #print(f"BYTEs read: {byte} Bytes  ", end="\r")
    if found >= 0:
        drec = True
        print('==== Found JPG at location: ' + str(hex(found+(size*offs))) + ' ====')
        # Now lets create recovered file and search for ending signature
        fileN = open( str(rcvd) + '.jpg', "wb")
        fileN.write(byte[found:])
        while drec:
            byte = fileD.read(size)
            bfind = byte.find(b'\xff\xd9')
            if bfind >= 0:
                fileN.write(byte[:bfind+2])
                fileD.seek((offs+1)*size)
                print('==== Wrote JPG to location: ' + str(rcvd) + '.jpg ====\n')
                drec = False
                rcvd += 1
                fileN.close()
            else: fileN.write(byte)
    byte = fileD.read(size)
    offs += 1
fileD.close()