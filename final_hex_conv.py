#!/usr/bin/env python
def hex_conv(thrshold_inorder):
	dec_thr=0
	i=0
	hexa_thr=''
	abc = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
	length=len(thrshold_inorder)
	while ((i<length) & ((length-i)>=4)):
	    j=4
	    while(j>0):
	     if thrshold_inorder[i]=='1':
	      dec_thr+= (2)**(4-j)
	      print "dec_thr=",dec_thr
	     i=i+1
	     j=j-1
	    mul=dec_thr
	    print "mul=",mul
	    dec_thr=0
	    hexa_thr_part = ''
	    while mul >15:
	     c = abc[mul%16]
	     hexa_thr_part = c+hexa_thr_part
	     mul = mul/16  
	    hexa_thr_part= abc[mul]+hexa_thr_part 
	    hexa_thr=hexa_thr+hexa_thr_part
	    #print i
	#print dec_thr  
        #if dec_thr==0:
                #hexa_thr='0'*13
                #return hexa_thr
	
		  #print c  
	print "hexa_thr=",hexa_thr
	return hexa_thr

	   
a='0000111111111111'
hexa_conv=hex_conv(a)
print "hex_conv=",hexa_conv
	   
	   
    
