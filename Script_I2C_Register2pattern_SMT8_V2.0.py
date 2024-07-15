# -*- coding:utf-8 -*-
import os
import sys
import re
# import openpyxl
from xml.dom import minidom
# from openpyxl import load_workbook
import datetime

import zipfile
import shutil


def get_system_time():
	time=datetime.datetime.now()
	timeformat=time.strftime('%Y.%m.%d  %H:%M:%S')
	return timeformat

def DecData2BinData_8bit(decdata):
	bit='{:08b}'.format(decdata)
	return bit

def HexData2BinData_8bit(hexdata):
	bit='{:08b}'.format(int(hexdata,16))
	return bit

def AscData2list(string):
	if re.search(r"[0-9a-f][0-9a-f]\s+[0-9a-f][0-9a-f]",string,re.I):
		list_readline=string.split()
	else:
		list_readline=list(string)
	return list_readline

def AscData2BinData(AscData):
	if re.search(r"[0-9a-f][0-9a-f]",AscData,re.I):
		BinData=HexData2BinData_8bit(AscData)
	else:
		BinData=DecData2BinData_8bit(ord(AscData))
	return BinData

def DisplayEscapeChar(string,flag):
	if flag=="True":
		string_esc=string.replace('\r',r'\r').replace('\n',r'\n')
	elif flag=="False":
		string_esc=string.replace(r'\r','\r').replace(r'\n','\n')
	return string_esc

def DeleteCarriage(list_readline):
	for i,readline in enumerate(list_readline):
		list_readline[i]=readline.replace('\r','').replace('\n','')
	return list_readline

def Drive2CompareFormat(string):
	if int(string)==0:
		string_compare="L"
	elif int(string)==1:
		string_compare="H"
	return string_compare

def GetIndex_WR_PattternSrc(Flag_WR_PattternSrc):
	if Flag_WR_PattternSrc=="write":
		index=0
	elif Flag_WR_PattternSrc=="read":
		index=1
	return index

def GetIndex_WR_Timing(Flag_WR_Timing):
	if Flag_WR_Timing=="write":
		index=0
	elif Flag_WR_Timing=="read":
		index=1
	return index

def MerageTimesets(BaudRates,PinInfo):
	if PinInfo[len(BaudRates)-2][3]==PinInfo[len(BaudRates)-1][3]:
		TimeSets=PinInfo[len(BaudRates)-2][3]
	elif PinInfo[len(BaudRates)-2][3]!=PinInfo[len(BaudRates)-1][3]:
		TimeSets=PinInfo[len(BaudRates)-2][3]+","+PinInfo[len(BaudRates)-1][3]
	return TimeSets

def MerageTimesets_IIC(BaudRates,PinInfo):
	if PinInfo[len(BaudRates)-2][3]==PinInfo[len(BaudRates)-1][3]:
		TimeSets=PinInfo[len(BaudRates)-2][3]+","+PinInfo[len(BaudRates)-2][3]+"_Start"+","+PinInfo[len(BaudRates)-2][3]+"_Idle"+","+PinInfo[len(BaudRates)-2][3]+"_Stop"
	elif PinInfo[len(BaudRates)-2][3]!=PinInfo[len(BaudRates)-1][3]:
		TimeSets=PinInfo[len(BaudRates)-2][3]+","+PinInfo[len(BaudRates)-2][3]+"_Start"+","+PinInfo[len(BaudRates)-2][3]+"_Idle"+","+PinInfo[len(BaudRates)-2][3]+"_Stop"+","\
			+PinInfo[len(BaudRates)-1][3]+","+PinInfo[len(BaudRates)-1][3]+"_Start"+","+PinInfo[len(BaudRates)-1][3]+"_Idle"+","+PinInfo[len(BaudRates)-1][3]+"_Stop"
	return TimeSets

def MeragePinMap(BaudRates,PinInfo):
	if PinInfo[len(BaudRates)-2][0]==PinInfo[len(BaudRates)-1][0]:
		PinMap=PinInfo[len(BaudRates)-2][0]
	elif PinInfo[len(BaudRates)-2][0]!=PinInfo[len(BaudRates)-1][0]:
		PinMap=PinInfo[len(BaudRates)-2][0]+","+PinInfo[len(BaudRates)-1][0]

	for i,readdata in enumerate(PinInfo):
		if i>=len(BaudRates):
			PinMap=PinMap+","+PinInfo[i][0]
	return PinMap

def MergePattern(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,Flag_WR_PattternSrc,fp,Opcode,DataList,comment):
	Opcode=Opcode+'\t\t'*(3-int(len(Opcode)/8))
	timeset=PinInfo[GetIndex_WR_Timing(Flag_WR_Timing)][3]+"\t\t"*(1-int(len(PinInfo[GetIndex_WR_Timing(Flag_WR_Timing)][3])/8))

	if PinInfo[len(BaudRates)-2][0]==PinInfo[len(BaudRates)-1][0]:
		writedata=DataList[GetIndex_WR_PattternSrc(Flag_WR_PattternSrc)]

		for i,readdata in enumerate(DataList):
			if i>=len(BaudRates):
				writedata=writedata+" "+DataList[i]
	else:
		writedata=" ".join(DataList)

	for i,readdata in enumerate(PinInfo):
		if i>=len(Pinmap):
			writedata=writedata+" "+PinInfo[i][1]

	fp.write(Opcode+"\t\t"+timeset+""+"\t\t"+writedata+" ;"+"\t\t"+comment+"\n")

def MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,TimingName,Flag_WR_PattternSrc,fp,Opcode,DataList,comment,Flag_lineNo,lineNo):
	Opcode=Opcode+'\t\t'*(3-int(len(Opcode)/8))
	timeset=PinInfo[GetIndex_WR_Timing(Flag_WR_Timing)][3]+"\t\t"*(1-int(len(PinInfo[GetIndex_WR_Timing(Flag_WR_Timing)][3])/8))

	if PinInfo[len(BaudRates)-2][0]==PinInfo[len(BaudRates)-1][0]:
		writedata=DataList[GetIndex_WR_PattternSrc(Flag_WR_PattternSrc)]

		for i,readdata in enumerate(DataList):
			if i>=len(BaudRates):
				writedata=writedata+" "+DataList[i]
	else:
		writedata=" ".join(DataList)

	for i,readdata in enumerate(PinInfo):
		if i>=len(Pinmap):
			writedata=writedata+" "+PinInfo[i][1]

	if TimingName!="":
		timeset=timeset+"_"+TimingName

	if int(Flag_lineNo)==1:
		comment=re.sub(r"//","",comment)
		fp.write(Opcode+"\t\t"+timeset+""+"\t\t"+writedata+" ;"+"\t\t"+"//line:"+str(lineNo)+",\t\t"+comment+"\n")
	else:
		fp.write(Opcode+"\t\t"+timeset+""+"\t\t"+writedata+" ;"+"\t\t"+comment+"\n")

def BaudRateConvUnit(BaudRate):
	if re.search(r"(\d+)(\D+)",BaudRate,re.I):
		BaudRate_re=re.search(r"(\d+)(\D+)",BaudRate,re.I)
		BaudRate_Value=BaudRate_re.group(1)
		BaudRate_Unit=BaudRate_re.group(2)

		if re.search(r"K",BaudRate_Unit,re.I):
			BaudRate_Value=int(int(BaudRate_Value)*1e3)
		elif re.search(r"M",BaudRate_Unit,re.I):
			BaudRate_Value=int(int(BaudRate_Value)*1e6)
		elif re.search(r"G",BaudRate_Unit,re.I):
			BaudRate_Value=int(int(BaudRate_Value)*1e9)
	else:
		BaudRate_Value=int(BaudRate)
	return BaudRate_Value

def BaudRate2PinInfo(Pinmap,BaudRates):
	for i,Pin in enumerate(Pinmap):
		if i<len(BaudRates):
			BaudRate_Base=BaudRateConvUnit(BaudRates[i])

			if re.search(r"(\S+)/(\d+)",BaudRates[i],re.I):
				BaudRate_re=re.search(r"(\S+)/(\d+)",BaudRates[i],re.I)
				BaudRate_Base_str=BaudRate_re.group(1)
				BaudRate_Multi=BaudRate_re.group(2)

				BaudRate_value=int(int(BaudRate_Base)/int(BaudRate_Multi))
				Timeset="TS_"+BaudRate_Base_str+"Hz_"+"d"+BaudRate_Multi
				PinInfo[i]=Pinmap[i],"X",BaudRate_value,Timeset
			elif re.search(r"(\S+)x(\d+)",BaudRates[i],re.I):
				BaudRate_re=re.search(r"(\S+)x(\d+)",BaudRates[i],re.I)
				BaudRate_Base_str=BaudRate_re.group(1)
				BaudRate_Multi=BaudRate_re.group(2)

				BaudRate_value=int(int(BaudRate_Base)*int(BaudRate_Multi))
				Timeset="TS_"+BaudRate_Base_str+"Hz_"+"x"+BaudRate_Multi
				PinInfo[i]=Pinmap[i],"X",BaudRate_value,Timeset
			else:
				BaudRate_value=BaudRate_Base
				Timeset="TS_"+str(BaudRates[i])+"Hz"
				PinInfo[i]=Pinmap[i],"X",BaudRate_value,Timeset
		else:
				PinInfo[i]=Pinmap[i],"X"

	return PinInfo

def WaitTime2LoopNumbers(Flag_WR_Timing,PinInfo,waittime):
	BaudRate=PinInfo[GetIndex_WR_Timing(Flag_WR_Timing)][2]
	waittime_re=re.search(r"(\d+)(\D+)",waittime,re.I)
	waittime_value=waittime_re.group(1)
	waittime_unit=waittime_re.group(2)

	if re.search(r"ms",waittime_unit,re.I):
		waittime_value=int(waittime_value)*1e-3
	elif re.search(r"us",waittime_unit,re.I):
		waittime_value=int(waittime_value)*1e-6
	elif re.search(r"ns",waittime_unit,re.I):
		waittime_value=int(waittime_value)*1e-9
	else:
		waittime_value=int(waittime_value)

	loopnumbers=int(waittime_value*BaudRate)
	return loopnumbers

def HexTxt2StardardTxt(outputfile,list_readlines,Flag_carriage):
	fp_write=open(outputfile,'w')
	Flag_WR_PattternSrc=''

	if re.search(r"\S+_Long",list_readlines[0],re.I):	
		for i,readdata in enumerate(list_readlines):
			if re.search(r"I2C_write_Long\s+(\S+)\s+(\S+)\s+(\S+)",readdata,re.I):
				Flag_WR_PattternSrc="write"

				readdata_re=re.search(r"I2C_write_Long\s+(\S+)\s+(\S+)\s+(\S+)",readdata,re.I)
				hexdata_SlaveAddr=readdata_re.group(1)
				hexdata_RegAddr=readdata_re.group(2)
				hexdata_RegData=readdata_re.group(3)

				fp_write.write("//write:"+"sa="+hexdata_SlaveAddr+",reg="+hexdata_RegAddr+",data="+hexdata_RegData+"\n")
				fp_write.write("I2C_write"+"\t"+DisplayEscapeChar(hexdata_SlaveAddr.replace('0x',''),"True")+"\t"+DisplayEscapeChar(hexdata_RegAddr.replace('0x',''),"True")+"\t"+DisplayEscapeChar(hexdata_RegData.replace('0x',''),"True")+"\n")

			elif re.search(r"I2C_read_Long\s+(\S+)\s+(\S+)",readdata,re.I):
				Flag_WR_PattternSrc="read"

				readdata_re=re.search(r"I2C_read_Long\s+(\S+)\s+(\S+)\s+(\S+)",readdata,re.I)
				hexdata_SlaveAddr=readdata_re.group(1)
				hexdata_RegAddr=readdata_re.group(2)
				hexdata_RegData=readdata_re.group(3)

				fp_write.write("//read:"+"sa="+hexdata_SlaveAddr+",reg="+hexdata_RegAddr+",data="+hexdata_RegData+"\n")
				fp_write.write("I2C_read"+"\t"+DisplayEscapeChar(hexdata_SlaveAddr.replace('0x',''),"True")+"\t"+DisplayEscapeChar(hexdata_RegAddr.replace('0x',''),"True")+"\t"+DisplayEscapeChar(hexdata_RegData.replace('0x',''),"True")+"\n")

			elif re.search(r"//",readdata,re.I):
				fp_write.write(DisplayEscapeChar(readdata,"True")+"\n")

			elif re.search(r"Wait",readdata,re.I):
				fp_write.write("//"+DisplayEscapeChar(readdata,"True")+"\n")

	fp_write.close()

def StardardTxt2NiPattern(inputfile,PinInfo,Flag_EvenParity,Flag_readdata,list_readline,Flag_lineNo):
	fp_write=open(inputfile,'w')
	printtime=get_system_time()
	patternname=inputfile.replace('.digipatsrc','')
	Flag_WR_PattternSrc="write"
	Flag_WR_Timing="write"
	lineNo=0


	fp_write.write("file_format_version 1.1;\n\n")
	fp_write.write("timeset "+MerageTimesets_IIC(BaudRates,PinInfo)+";\n\n")
	fp_write.write("pattern "+patternname+"("+MeragePinMap(BaudRates,PinInfo)+")"+"\n")
	fp_write.write("{\n")
	fp_write.write("Label_"+patternname+":\n")
	MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"",["1","1"],"//Updata at "+printtime,Flag_lineNo,lineNo);												lineNo+=1;

	for i,readdata in enumerate(list_readline):
		if re.search(r"//write",readdata,re.I):
			Flag_WR_Timing="write"
			Flag_WR_PattternSrc="write"
			readdata=re.sub(r"//","",readdata)
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"",["1","1"],"",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"repeat(100)",["1","1"],"//String_"+DisplayEscapeChar(readdata,"True"),Flag_lineNo,lineNo);						lineNo+=1;

		elif re.search(r"//read",readdata,re.I):
			Flag_WR_Timing="read"
			Flag_WR_PattternSrc="write"
			readdata=re.sub(r"//","",readdata)
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"",["1","1"],"",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"repeat(1)",["1","1"],"//String_"+DisplayEscapeChar(readdata,"True"),Flag_lineNo,lineNo);						lineNo+=1;

		elif re.search(r"//Wait",readdata,re.I):
			loopnumbers=WaitTime2LoopNumbers(Flag_WR_Timing,PinInfo,readdata)
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"",["1","1"],"",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"repeat("+str(loopnumbers)+")",["1","1"],DisplayEscapeChar(readdata,"True"),Flag_lineNo,lineNo);					lineNo+=1;

		elif re.search(r"//",readdata,re.I):
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"",["1","1"],"",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"repeat(1)",["1","1"],""+DisplayEscapeChar(readdata,"True"),Flag_lineNo,lineNo);							lineNo+=1;

		elif re.search(r"I2C_write",readdata,re.I):
			Flag_WR_Timing="write"
			Flag_WR_PattternSrc="write"
			readdata_re=re.search(r"I2C_write\s+(\S+)\s+(\S+)\s+(\S+)",readdata,re.I)
			hexdata_SlaveAddr=readdata_re.group(1)
			hexdata_RegAddr=readdata_re.group(2)
			hexdata_RegData=readdata_re.group(3)

			#Start_bit
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Start",Flag_WR_PattternSrc,fp_write,"",["1","1"],"//Start_bit",Flag_lineNo,lineNo);											lineNo+=1;

			#SlaveAddr
			BinData_SlaveAddr=AscData2BinData(DisplayEscapeChar(hexdata_SlaveAddr,"False"))
			list_BinData_SlaveAddr=list(BinData_SlaveAddr)[1:8]

			for j,bitdata in enumerate(list_BinData_SlaveAddr):
				index=len(list_BinData_SlaveAddr)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",bitdata],"//sa"+"["+str(index)+"]="+bitdata,Flag_lineNo,lineNo);							lineNo+=1;

			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","0"],"//WR_bit=0",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","L"],"//ACK=L",Flag_lineNo,lineNo);												lineNo+=1;

			#RegAddr
			BinData_RegAddr=AscData2BinData(DisplayEscapeChar(hexdata_RegAddr,"False"))
			list_BinData_RegAddr=list(BinData_RegAddr)[0:8]

			for j,bitdata in enumerate(list_BinData_RegAddr):
				index=len(list_BinData_RegAddr)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",bitdata],"//address"+"["+str(index)+"]="+bitdata,Flag_lineNo,lineNo);							lineNo+=1;

			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","L"],"//ACK=L",Flag_lineNo,lineNo);												lineNo+=1;

			#RegData
			list_BinData_RegData=[]
			for j in range(int(len(hexdata_RegData)/2)):
				writedata=hexdata_RegData[2*j:2*(j+1)]
				BinData_RegData=AscData2BinData(DisplayEscapeChar(writedata,"False"))
				list_BinData_RegData.extend(list(BinData_RegData))

			for j,bitdata in enumerate(list_BinData_RegData):
				index=len(list_BinData_RegData)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",bitdata],"//data"+"["+str(index)+"]="+bitdata,Flag_lineNo,lineNo);							lineNo+=1;

			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","L"],"//ACK=L",Flag_lineNo,lineNo);												lineNo+=1;

			#Stop_bit
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Stop",Flag_WR_PattternSrc,fp_write,"",["1","0"],"//Stop_bit",Flag_lineNo,lineNo);											lineNo+=1;


		elif re.search(r"I2C_read",readdata,re.I) and Flag_readdata==1:
			Flag_WR_Timing="read"
			Flag_WR_PattternSrc="write"
			readdata_re=re.search(r"I2C_read\s+(\S+)\s+(\S+)\s+(\S+)",readdata,re.I)
			hexdata_SlaveAddr=readdata_re.group(1)
			hexdata_RegAddr=readdata_re.group(2)
			hexdata_RegData=readdata_re.group(3)

			#Start_bit
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Start",Flag_WR_PattternSrc,fp_write,"",["1","1"],"//Start_bit",Flag_lineNo,lineNo);											lineNo+=1;

			#SlaveAddr
			BinData_SlaveAddr=AscData2BinData(DisplayEscapeChar(hexdata_SlaveAddr,"False"))
			list_BinData_SlaveAddr=list(BinData_SlaveAddr)[1:8]

			for j,bitdata in enumerate(list_BinData_SlaveAddr):
				index=len(list_BinData_SlaveAddr)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",bitdata],"//sa"+"["+str(index)+"]="+bitdata,Flag_lineNo,lineNo);							lineNo+=1;

			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","0"],"//WR_bit=0",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","L"],"//ACK=L",Flag_lineNo,lineNo);												lineNo+=1;

			#RegAddr
			BinData_RegAddr=AscData2BinData(DisplayEscapeChar(hexdata_RegAddr,"False"))
			list_BinData_RegAddr=list(BinData_RegAddr)[0:8]

			for j,bitdata in enumerate(list_BinData_RegAddr):
				index=len(list_BinData_RegAddr)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",bitdata],"//address"+"["+str(index)+"]="+bitdata,Flag_lineNo,lineNo);							lineNo+=1;

			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","L"],"//ACK=L",Flag_lineNo,lineNo);												lineNo+=1;

			#Start_bit
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Start",Flag_WR_PattternSrc,fp_write,"",["1","1"],"//Start_bit",Flag_lineNo,lineNo);											lineNo+=1;

			#SlaveAddr
			BinData_SlaveAddr=AscData2BinData(DisplayEscapeChar(hexdata_SlaveAddr,"False"))
			list_BinData_SlaveAddr=list(BinData_SlaveAddr)[0:7]

			#SlaveAddr
			BinData_SlaveAddr=AscData2BinData(DisplayEscapeChar(hexdata_SlaveAddr,"False"))
			list_BinData_SlaveAddr=list(BinData_SlaveAddr)[1:8]

			for j,bitdata in enumerate(list_BinData_SlaveAddr):
				index=len(list_BinData_SlaveAddr)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",bitdata],"//sa"+"["+str(index)+"]="+bitdata,Flag_lineNo,lineNo);							lineNo+=1;

			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","1"],"//WR_bit=1",Flag_lineNo,lineNo);												lineNo+=1;
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","L"],"//ACK=L",Flag_lineNo,lineNo);												lineNo+=1;

			#RegData
			list_BinData_RegData=[]
			for j in range(int(len(hexdata_RegData)/2)):
				writedata=hexdata_RegData[2*j:2*(j+1)]
				BinData_RegData=AscData2BinData(DisplayEscapeChar(writedata,"False"))
				list_BinData_RegData.extend(list(BinData_RegData))

			Flag_WR_PattternSrc="read"
			for j,bitdata in enumerate(list_BinData_RegData):
				index=len(list_BinData_RegData)-j-1
				MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1",Drive2CompareFormat(bitdata)],"//data"+"["+str(index)+"]="+Drive2CompareFormat(bitdata),Flag_lineNo,lineNo);		lineNo+=1;

			Flag_WR_PattternSrc="write"
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"",Flag_WR_PattternSrc,fp_write,"",["1","H"],"//NO_ACK=H",Flag_lineNo,lineNo);												lineNo+=1;

			#Stop_bit
			MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Stop",Flag_WR_PattternSrc,fp_write,"",["1","0"],"//Stop_bit",Flag_lineNo,lineNo);											lineNo+=1;

	MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"",["1","1"],"",Flag_lineNo,lineNo);														lineNo+=1;
	MergePattern_DiffTiming(Pinmap,BaudRates,PinInfo,Flag_WR_Timing,"Idle",Flag_WR_PattternSrc,fp_write,"halt",["1","1"],"",Flag_lineNo,lineNo);														lineNo+=1;
	fp_write.write("}")
	fp_write.close()

	return(MeragePinMap(BaudRates,PinInfo),lineNo)

def CreateAsciiFile_Smart8(sprgfile,vecfile,cmtfile,asciifile):
	fp_write_sprgfile=open(sprgfile,'r')
	fp_write_vecfile=open(vecfile,'r')
	fp_write_cmtfile=open(cmtfile,'r')
	fp_write_asciifile=open(asciifile,'w')

	list_readline_sprgfile=fp_write_sprgfile.readlines()
	list_readline_vecfile=fp_write_vecfile.readlines()
	list_readline_cmtfile=fp_write_cmtfile.readlines()

	fp_write_sprgfile.close()
	fp_write_vecfile.close()
	fp_write_cmtfile.close()

	if list_readline_sprgfile:
		for i,readdata in enumerate(list_readline_sprgfile):
			if readdata.find("<?xml") != -1:
				fp_write_asciifile.write(readdata)
			elif readdata.find("<Program") != -1:
				readdata = readdata.replace("Program", "Pattern")
				fp_write_asciifile.write(readdata)
				fp_write_asciifile.write("  <Program>\n")
			else:
				fp_write_asciifile.write("  " + readdata)

	if list_readline_vecfile:
		fp_write_asciifile.write("  <Vector>\n")
		fp_write_asciifile.write("    <![CDATA[\n")

		for i,readdata in enumerate(list_readline_vecfile):
			fp_write_asciifile.write("      " + readdata)

		fp_write_asciifile.write("    ]]>\n")
		fp_write_asciifile.write("  </Vector>\n")

	if list_readline_cmtfile:
		fp_write_asciifile.write("  <Comment>\n")
		fp_write_asciifile.write("    <![CDATA[\n")

		for i,readdata in enumerate(list_readline_cmtfile):
			fp_write_asciifile.write("      " + readdata)

		fp_write_asciifile.write("    ]]>\n")
		fp_write_asciifile.write("  </Comment>\n")

	fp_write_asciifile.write("</Pattern>\n")
	fp_write_asciifile.close()

def NiPattern2Smart8Pattern(inputfile,list_readlines,PinGroup,line_numbers,Flag_zip):
	asciifile=inputfile.replace('.digipatsrc','.ascii')
	sprgfile="Program.sprg"
	vecfile="Vectors.vec"
	cmtfile="Comments.cmt"

	lineNo=0
	flag_first_Opcode=0
	lines_OpcodeInterval=0

	fp_write_sprgfile=open(sprgfile,'w')
	fp_write_vecfile=open(vecfile,'w')
	fp_write_cmtfile=open(cmtfile,'w')

	#sprgfile
	fp_write_sprgfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	fp_write_sprgfile.write("<Program xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"Program.xsd\">\n")
	fp_write_sprgfile.write("  <Instrument id=\""+str(PinGroup)+"\">\n")
	fp_write_sprgfile.write("    <Assignment id=\"xmode\" value=\"1\"/>\n")

	#vecfile&cmtfile
	for i,readdata in enumerate(list_readlines):
		if re.search(r"TS_\S+(.*)\s+;",readdata,re.I):
			readdata_re=re.search(r"TS_\S+(.*);(.*)",readdata,re.I)
			writedata=re.sub(r"\s","",readdata_re.group(1))
			commentdata=re.sub(r"\t","",readdata_re.group(2))
			fp_write_vecfile.write(writedata+"\n")

			if re.search(r"//",readdata,re.I):
				fp_write_cmtfile.write(str(lineNo)+" "+commentdata+"\n")

			if re.search(r"repeat\((.*)\)",readdata,re.I):
				readdata_re=re.search(r"repeat\((.*)\)",readdata,re.I)
				repeat=readdata_re.group(1)

				if flag_first_Opcode==0:
					lines_OpcodeInterval=lines_OpcodeInterval+1
					flag_first_Opcode=1

				#sprgfile
				fp_write_sprgfile.write("      <Instruction id=\"genVec\" value=\""+str(lines_OpcodeInterval-1)+"\"/>\n")
				fp_write_sprgfile.write("      <Instruction id=\"genVec\" value=\"1\">\n")
				fp_write_sprgfile.write("        <Assignment id=\"repeat\" value=\""+str(repeat)+"\"/>\n")
				fp_write_sprgfile.write("      </Instruction>\n")

				line_numbers=line_numbers-lines_OpcodeInterval
				lines_OpcodeInterval=0

			lineNo+=1
			lines_OpcodeInterval+=1

	#sprgfile
	fp_write_sprgfile.write("    <Instruction id=\"genVec\" value=\""+str(line_numbers)+"\"/>\n")
	fp_write_sprgfile.write("  </Instrument>\n")
	fp_write_sprgfile.write("</Program>\n")

	fp_write_sprgfile.close()
	fp_write_vecfile.close()
	fp_write_cmtfile.close()

	CreateAsciiFile_Smart8(sprgfile,vecfile,cmtfile,asciifile)

	if int(Flag_zip)==1:
		Zipfile=inputfile.replace('.digipatsrc','.zip')
		patfile=inputfile.replace('.digipatsrc','.pat')

		fp_zip=zipfile.ZipFile(Zipfile, 'w', zipfile.ZIP_DEFLATED)

		fp_zip.write(sprgfile)
		fp_zip.write(vecfile)
		fp_zip.write(cmtfile)
		fp_zip.close()

		#compress vec&sprg&cmt file
		os.rename(Zipfile,patfile)

		#remove vec&sprg&cmt file
		os.remove(sprgfile)
		os.remove(vecfile)
		os.remove(cmtfile)



if __name__=="__main__":
	global list_readline
	Pinmap=["SCL","SDA"]
	BaudRates=["400K","100K"]
	OtherPin={}
	PinInfo={}
	Flag_OtherPin=0
	Flag_EvenParity=0
	Flag_carriage=0
	Flag_readdata=1
	Flag_lineNo=0
	Flag_zip=1

	#method1:External input by cmd(only window)
	# Pinmap=[str(input("Input SCL PinName [Str]:")),str(input("Input SDA PinName [Str]:"))]

	# for i in range(10):
	# 	Flag_OtherPin=int(input("Selete Pattern add OtherPin [0/1]:"))

	# 	if Flag_OtherPin==1:
	# 		OtherPin[i+2]=str(input("Input OtherPin Name [Str]:")),str(input("Input OtherPin State [0/1/L/H/X/M]:"))
	# 	else:
	# 		break

	# BaudRates=[str(input("Input PatternWrite BaudRate [Str]:")),str(input("Input PatternRead BaudRate [Str]:"))]
	# Flag_EvenParity=int(input("Selete WritePattern add Even Parity [0/1]:"))
	# Flag_carriage=int(input("Selete WritePattern add CarriageFlag(\\r\\n) [0/1]:"))
	# Flag_readdata=int(input("Selete ReadPattern add ReadData result [0/1]:"))
	# Flag_lineNo=int(input("Show line Number on the comment [0/1]:"))
	# Flag_zip=int(input("whether vec&sprg&cmt file compress to patfile [0/1]:"))

	#method2:External input by setup(window and linux)
	files=os.listdir(os.getcwd())
 
	print(files)

	for i,inputfile in enumerate(files):
		if re.search(r"InputFile.setup",inputfile,re.I):
			fp_read=open(inputfile,'r')
			list_readline=fp_read.readlines()
			DeleteCarriage(list_readline)
			fp_read.close()
    
			Pinmap=[re.sub(r"\s","",list_readline[0]).split(':')[1],re.sub(r"\s","",list_readline[1]).split(':')[1]]

			cout_Flag_OtherPin=0
			for j,readdata in enumerate(list_readline):
				if re.search(r"Selete Pattern add OtherPin",readdata,re.I):
					Flag_OtherPin=int(re.sub(r"\s","",list_readline[j]).split(':')[1])

					if Flag_OtherPin==1:
						OtherPin[2+cout_Flag_OtherPin]=str(re.sub(r"\s","",list_readline[j+1]).split(':')[1]),str(re.sub(r"\s","",list_readline[j+2]).split(':')[1])
						cout_Flag_OtherPin+=1
					else:
						BaudRates=[re.sub(r"\s","",list_readline[j+1]).split(':')[1],re.sub(r"\s","",list_readline[j+2]).split(':')[1]]
						Flag_readdata=int(re.sub(r"\s","",list_readline[j+3]).split(':')[1])
						Flag_lineNo=int(re.sub(r"\s","",list_readline[j+4]).split(':')[1])
						Flag_zip=int(re.sub(r"\s","",list_readline[j+5]).split(':')[1])
						break


			PinInfo=BaudRate2PinInfo(Pinmap,BaudRates)
			PinInfo.update(OtherPin)


			# use for Smart8,remove pat file
			files=os.listdir(os.getcwd())

			# for i,inputfile in enumerate(files):
			# 	if re.search(r'\.pat',inputfile,re.I):
			# 		os.remove(inputfile)

			# all format Files turn into stardard txt
			files=os.listdir(os.getcwd())

			for i,inputfile in enumerate(files):
				if re.search(r".txt",inputfile,re.I):
					fp_read=open(inputfile,'r')
					list_readlines=fp_read.readlines()
					fp_read.close()

					outputfile=inputfile.replace('.txt','.digipatsrc')

					if list_readlines!=[]:
						DeleteCarriage(list_readlines)
						HexTxt2StardardTxt(outputfile,list_readlines,Flag_carriage)

			# stardard txt turn into sts pattern
			files=os.listdir(os.getcwd())
   
			print(files)

			for i,inputfile in enumerate(files):
				if re.search(r".digipatsrc",inputfile,re.I):
					fp_read=open(inputfile,'r')
					list_readline=fp_read.readlines()
					fp_read.close()

					DeleteCarriage(list_readline)
					returnData=StardardTxt2NiPattern(inputfile,PinInfo,Flag_EvenParity,Flag_readdata,list_readline,Flag_lineNo)
					PinGroup=returnData[0]
					line_numbers=returnData[1]

					# use for Smart8,create vec&sprg&cmt file
					fp_read=open(inputfile,'r')
					list_readlines=fp_read.readlines()
					fp_read.close()

					DeleteCarriage(list_readlines)
					NiPattern2Smart8Pattern(inputfile,list_readlines,PinGroup,line_numbers,Flag_zip)

			print('Done!')