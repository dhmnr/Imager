#!/usr/bin/env python3
from PIL import Image
from math import ceil,sqrt
from hashlib import sha256
import binascii
import argparse

def pad_hex(string):
	length=len(string)
	if(length%6==0):
		return string
	else:
		padding='0'*(6-(length%6))
		return padding+string

def pad_image(tuple_list):
	length=len(tuple_list)
	n=sqrt(length)
	padding=[(0,0,0)]*((ceil(n)**2)-length)
	return padding+tuple_list

def hex2tuple(hex_color):
	r,g,b=[int(hex_color[i:i+2],16) for i in range(0,len(hex_color),2)]
	return (r,g,b)

def tuple2hex(pixel):
	hex_rgb=[hex(i)[2:] for i in pixel]
	hex_rgb=[('0'*(2-len(i)))+i for i in hex_rgb]
	return ''.join(hex_rgb)
	
def encode(src_fp,dest_fp,out):
	print("Reading from file...")
	file_data=src_fp.read()
	sha256_hash=sha256(file_data).hexdigest()
	hex_str=pad_hex(sha256_hash+binascii.hexlify(file_data).decode('utf-8'))
	hex_colors=pad_image([hex2tuple(hex_str[i:i+6]) for i in range(0,len(hex_str),6)])
	length=int(sqrt(len(hex_colors)))
	src_fp.close()
	resolution=(length,length)
	print("Resolution of image is {}x{}".format(length,length))
	img=Image.new('RGB',resolution,'white')
	img.putdata(hex_colors)
	try:
		img.save(dest_fp)
	except ValueError:
		print("{} is not a valid filename. Defaulting to PNG.\nSupported formats are BMP,PNG,TIFF".format(out))
		dest_fp.close()
		fp2=open(out+'.png','wb')
		img.save(dest_fp)
	print("Done!")

def decode(src_fp,dest_fp):
	i=0
	print("Reading from Image...")
	img=Image.open(src_fp)
	color_list=list(img.getdata())
	while(color_list[i]==(0,0,0)):
		i=i+1
	color_list=color_list[i:]
	hex_list=[tuple2hex(pixel) for pixel in color_list]
	offset,rest=hex_list[0],hex_list[1:]
	hex_list=hex(int(offset,16))[2:]+''.join(rest)
	found_hash=hex_list[:64]
	hex_list=hex_list[64:]
	file_data=binascii.unhexlify(hex_list)
	actual_hash=sha256(file_data).hexdigest()
	if (found_hash==actual_hash):
		print("Hash check succeeded.")
		print("Writing to binary file...")
	else:
		print("Hash check failed.\nWriting to file ,Data might be corrupt")
	dest_fp.write(file_data)
	dest_fp.close
	src_fp.close
	print("Done!")

def main(In,out,d):
	
	try:
		fp1=open(In,'rb')
	except FileNotFoundError:
		print("No such file is found.\nExiting...")
		return
	
	try:
		fp2=open(out,'wb')
	except FileNotFoundError:
		print("Destination not found.\nExiting...")
		return
	if(d):
		decode(fp1,fp2)
	else:
		encode(fp1,fp2,out)
	
if __name__=="__main__":
	parser = argparse.ArgumentParser(description = "Encode any file to an image and decode .\n Supported Image formats are BMP,JPEG,JPG,PNG,TIFF")
	parser.add_argument('-f','--file' ,required=True ,help="Input binary file or Image file in case of decoding")
	parser.add_argument('-o','--out' ,required=True,help="Output Image/binary file destination with file extension.")
	parser.add_argument('-d','--decode',action="store_true",default=False,help="Use this to decode the image into a binary file")
	args = parser.parse_args()
	main(args.file,args.out,args.decode)
	

