#!/bin/bash

bm_arr=( "phold" "TimingLeaf" "RingTransmit" "RingTransmitMessage" "EchoLeaf" "EchoMessageLeaf" "MessageExchange" )

for bm in "${bm_arr[@]}";
do
	for d in "${bm}-"*;
	do
		if [ -d "$d" ];
		then
			mv "$d" "${d/${bm}/${bm}Federate}"
		fi
	done
done
     
