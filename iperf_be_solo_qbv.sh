#!/bin/bash

# Remote host details for the iperf client
remote_host="163.117.140.101"
ssh_user="netcom"
ssh_password="netcom;"

# Iperf server details
iperf_server_host="163.117.140.243"
iperf_server_user="netcom"
iperf_server_password="netcom;"

# QBV AP Intel details
Intel_AP_host="163.117.140.31"
Intel_AP_user="netcom"
Intel_AP_password="netcom;"

# Folder path to store results on the remote host and iperf server
server_results_folder="/home/netcom/Downloads/results/"

# Stopping all procedures
echo "Stoppin all procedures"
ssh "source" "sudo pkill tcpdump"
ssh "source" "sudo pkill iperf3"
ssh "destination" "sudo pkill tcpdump"
ssh "destination" "sudo pkill iperf3"

# Ensure the folder exists on the iperf server to store results
ssh "destination" "[ -d \"$server_results_folder\" ] || mkdir -p \"$server_results_folder\""



# Array of rates to test
rates=("10" "20" "30" "40" "50" "60" "70" "80" "90" "100" "110" "120")
q_times=("25" "50" "75" "100")
shapers=("25" "50" "75" "100")
for shaper in "${shapers[@]}"
do
	for q_time in "${q_times[@]}"
	do
		for rate in "${rates[@]}"
		do	
			echo "iperf server started on $iperf_server_host with output logging"
			echo "Configuration selected: \n"
			echo "Throutput: ${rate}MBytes/s"
			echo "Shaper: ${shaper}% of the channel"
			echo "Qtime: ${q_time}% of the cycle \n"
			
			#config command to be executed
			config_command="sudo python3 /home/netcom/WTSN-Binaries/scripts/qbv_scheduler.py -f /etc/WTSN/qbv_q${q_time}_s${shaper}.json"

			#iperf client command to be executed on the server
			iperf_server_command="nohup iperf3 -s -p 5002 -1 -i 10 --logfile $server_results_folder/Qbv_be_iperf_q${q_time}_s${shaper}_${rate}.txt > /dev/null 2>&1 &"

			#iperf client command to be executed on the client host
			iperf_command="iperf3 -c 10.0.1.7 -u -p 5002 --cport 10002 -b ${rate}M -i 10 -t 300"
		    
			#tcpdump client command to be executed on the client host
			tcpdump_client_command="sudo tcpdump -i enp2s0 --nano -w /home/netcom/Downloads/results/Qbv_be_iperf_client_q${q_time}_s${shaper}_${rate}.pcap"
		    
			#tcpdump server command to be executed on the client host
			tcpdump_server_command="sudo tcpdump -i enp2s0 --nano -w /home/netcom/Downloads/results/Qbv_be_iperf_server_q${q_time}_s${shaper}_${rate}.pcap"
		    		    
			#abrir tcpdump server
			echo "Starting tcpdump on $iperf_server_host (server)"
			ssh "destination" "$tcpdump_server_command" &
		    
			#abrir tcpdump client
		 	echo "Starting tcpdump on $remote_host (client)"
			ssh "source" "$tcpdump_client_command" &
		    
			# Start the iperf server on a different machine with output redirected to a file
			echo "Starting iperf server on $iperf_server_host"
			ssh "destination" "$iperf_server_command"
			sleep 2  # Add a sleep command to wait for the server to initialize
		    
			#Flash configuration on AP
			echo "Booting the selected configuration with command:  $config_command"
			ssh "intelap" "$config_command"
		    
			# Use SSH with password to execute the iperf client command on the remote host
			echo "Executing iperf client remotely on $remote_host as $ssh_user: $iperf_command"
			ssh "source" "$iperf_command"

			# After a client test are completed, retrieve the server-side results
			echo "Finished. Retrieving iperf server results from $iperf_server_host"
			scp "destination:/home/netcom/Downloads/results/Qbv_be_iperf_q${q_time}_s${shaper}_${rate}.txt" /home/netcom-i11-16/Downloads/results/
			if [ $? -eq 0 ]; then
				echo "iperf server results file copied successfully to /home/netcom-i11-16/Downloads/results/"
				ssh "destination" "rm -r /home/netcom/Downloads/results/Qbv_be_iperf_q${q_time}_s${shaper}_${rate}.txt"
	 		else
				echo "Error copying iperf server results file from $iperf_server_host."
			fi
			
			# Stopping all procedures
			echo "Stoppin all procedures"
			ssh "source" "sudo pkill tcpdump"
			ssh "source" "sudo pkill iperf3"
			ssh "destination" "sudo pkill tcpdump"
			ssh "destination" "sudo pkill iperf3"
	
			sleep 2
			
			echo "retrieving pcap from server"
			scp "destination:/home/netcom/Downloads/results/Qbv_be_iperf_server_q${q_time}_s${shaper}_${rate}.pcap"	"core:/mnt/imagenes/pcaps/pcaps_server/"
			echo "sent"
			sleep 2
			echo "deleting the file from server"
			ssh "destination" "rm -r /home/netcom/Downloads/results/Qbv_be_iperf_server_q${q_time}_s${shaper}_${rate}.pcap"
			echo "deleted"
			echo "retrieving pcap from client"
			scp "source:/home/netcom/Downloads/results/Qbv_be_iperf_client_q${q_time}_s${shaper}_${rate}.pcap" "core:/mnt/imagenes/pcaps/pcaps_client/"
			sleep 2
			echo "deleting the file from client"
			ssh "source" "rm -r /home/netcom/Downloads/results/Qbv_be_iperf_client_q${q_time}_s${shaper}_${rate}.pcap"
			echo "deleted"
			
		done
	done
done


# Optionally, stop the iperf server or leave it running based on your requirement
#ssh "destination" "killall iperf3"
