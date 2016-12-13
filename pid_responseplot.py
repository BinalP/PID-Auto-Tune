import time;

safety_flag=1
stability_flag=1
t1=0.0
t2=0.0
stable_read="0.0"
stime=0.0
etime=0.0
jerk_counter=0

def jerk_check(readings):
	global jerk_counter
	if (cur_read[0]<cur_read[1] and cur_read[2]<cur_read[1]):
		jerk_counter+=1
	print(str(jerk_counter))

def slow_response(start_time):
	if (time.time()-start_time>8):
		print("Slow response\n")
		return 1
	else:
		return 0


def unstable_system(readings):
	if (abs(float(readings[1])-float(readings[2]))>=18):
		print("System highly unstable\n\n Dangerous\n")
		return 1
	else:
		return 0


def data_write(p_,d_,slp,ovrsht):
	data_file=open("pd.txt",'a')
	if (slp==-1 and ovrsht==1000):
		data_file.write(str(p_)+";"+str(d_)+";i;i\n")
	elif (ovrsht==1000 and slp!=-1):
		data_file.write(str(p_)+";"+str(d_)+";"+str(slp)+";i\n")
	else:
		data_file.write(str(p_)+";"+str(d_)+";"+str(slp)+";"+str(ovrsht)+"\n")
	data_file.close()
	
	
def data_read():
	text_file=open("imu_data.txt",'r')
	l=sum(1 for _ in text_file)
	text_file.close()
	text_file=open("imu_data.txt",'r')
	readings=text_file.read().splitlines()[l-3:l]
	text_file.close()
	return readings




for p in range(0,3):
	for d in range(0,2):
		while 1:
			stability_flag=1
			safety_flag=1
			print(str(p)+";"+str(d)+"\n")
			cur_read=data_read()
			for i in range(0,3):
				if (abs(float(cur_read[i])-float(stable_read)))<=1:
					continue
				else:
					stability_flag=0
					break
			stbl_file=open("stability.txt",'w')
                        stbl_file.write(str(stability_flag)+"\n")
                        stbl_file.close()
			if stability_flag:
				while safety_flag:
					stbl_file=open("stability.txt",'w')
                        		stbl_file.write(str(stability_flag)+"\n")
                        		stbl_file.close()
					print(str(p)+";"+str(d)+"\n")
					print("Waiting for disturbance\n")
					cur_read=data_read()
					if (float(cur_read[2])-float(cur_read[1]))>=1.5:
						change_flag=1
						break
					if (float(cur_read[1])-float(cur_read[2]))>=1.5:
						change_flag=-1
						break
				stime=time.time()
				while safety_flag:
					stbl_file=open("stability.txt",'w')
		                        stbl_file.write("0\n")
		                        stbl_file.close()
					print(str(p)+";"+str(d)+"\n")
					print("Waiting for stabilisation to start\n")
					cur_read=data_read()
					if (unstable_system(cur_read)):
						safety_flag=0
						data_write(p,d,-1,1000)
						break
					if (float(cur_read[2])-float(cur_read[1]))>=1.5 and change_flag==-1:
						y=abs(float(cur_read[1])-float(stable_read))
						t1=time.time()
						change_flag=1
						break
					if (float(cur_read[1])-float(cur_read[2]))>=1.5 and change_flag==1:
						y=abs(float(cur_read[1])-float(stable_read))
						t1=time.time()
						change_flag=-1
						break
					etime=time.time()
					if(slow_response(stime)):
						safety_flag=0
						data_write(p,d,-1,1000)
						break
				stime=time.time()
				while safety_flag:
					print(str(p)+";"+str(d)+"\n")
					print("Waiting for stableReading\n")
					cur_read=data_read()
					if (unstable_system(cur_read)):
						safety_flag=0
						jerk_counter=0
						data_write(p,d,-1,1000)
						break
					if (abs(float(cur_read[2])-float(stable_read))<=1) or (float(cur_read[2])>float(stable_read) and change_flag==1) or (float(cur_read[2])<float(stable_read) and change_flag==-1):
						t2=time.time()
						x=t2-t1
						slope=y/x
						jerk_counter=0
						break
					jerk_check(cur_read)
					if(jerk_counter>=8):
						safety_flag=0
						jerk_counter=0
						data_write(p,d,-1,1000)
						print("Jerky response\n")
						break						
					if(slow_response(stime)):
						safety_flag=0
						jerk_counter=0
						data_write(p,d,-1,1000)
						break
				stime=time.time()
				while safety_flag:
					print(str(p)+";"+str(d)+"\n")
					print("Waiting for overshoot\n")
					cur_read=data_read()
					if (unstable_system(cur_read)):
						safety_flag=0
						jerk_counter=0
						data_write(p,d,slope,1000)
						break
					if ((float(cur_read[1])>float(cur_read[2])) and change_flag==1) or ((float(cur_read[1])<float(cur_read[2])) and change_flag==-1):
						ovrshoot=cur_read[1]
						jerk_counter=0
						break
					jerk_check(cur_read)
					print(str(jerk_counter))
					if(jerk_counter>=8):
						safety_flag=0
						jerk_counter=0
						data_write(p,d,slope,1000)
						print("Jerky response\n")
						break
					if(slow_response(stime)):
						safety_flag=0
						jerk_counter=0
						data_write(p,d,slope,1000)
						break
				if safety_flag:
					data_write(p,d,slope,ovrshoot)
				break
			else:
				continue
