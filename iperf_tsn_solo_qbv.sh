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

# Ensure the folder exists on the iperf server to store results
ssh "destination" "[ -d \"$server_results_folder\" ] || mkdir -p \"$server_results_folder\""



# Array of rates to test
q_times=("25" "50" "75" "100")
flujos=("1" "2" "5" "10")
ciclos=("1" "5" "10")
rates=("1" "2" "3" "4" "5" "6" "7" "8" "9" "11" "12")

for ciclo in "${ciclos[@]}"
do
	for q_time in "${q_times[@]}"
	do
		for flujo in "${flujos[@]}"
		do
			for rate in "${rates[@]}"
			do
				echo "iperf server started on $iperf_server_host with output logging"
				echo "Configuration selected: \n"
				echo "flujo: ${flujo} TSN"
				echo "Qtime: ${q_time}% of the cycle \n"
				echo "Ciclo: ${ciclo}ms  \n"
				echo "Throutput: ${rate}MBytes/s"
			
				#config command to be executed
				config_command="sudo python3 /home/netcom/WTSN-Binaries/scripts/qbv_scheduler.py -f /etc/WTSN/qbv_tsn_q${q_time}_c${ciclo}.json"
			
				#Flash configuration on AP
				echo "Booting the selected configuration with command:  $config_command"
				ssh "intelap" "$config_command"
			
				#tcpdump client command to be executed on the client host
				tcpdump_client_command="sudo tcpdump -i enp2s0 --nano -w /home/netcom/Downloads/results/Qbv_tsn_iperf_client_q${q_time}_f${flujo}_c${ciclo}_${rate}.pcap -s 43"
		    
				#tcpdump server command to be executed on the client host
				tcpdump_server_command="sudo tcpdump -i enp2s0 --nano -w /home/netcom/Downloads/results/Qbv_tsn_iperf_server_q${q_time}_f${flujo}_c${ciclo}_${rate}.pcap -s 43"
		    		    
				#abrir tcpdump server
				echo "Starting tcpdump on $iperf_server_host (server)"
				ssh "destination" "$tcpdump_server_command" &
			    
				#abrir tcpdump client
				echo "Starting tcpdump on $remote_host (client)"
				ssh "source" "$tcpdump_client_command" &
				
				#iperf client command to be executed on the server
				for ((i=0; i<flujo; i++)); 
				do
					# Construct the command
					iperf_server_command="nohup iperf3 -s -p $((5000 + i)) -1 -i 10 --logfile $server_results_folder/Qbv_tsn_iperf_q${q_time}_f${flujo}_c${ciclo}_${rate}.txt > /dev/null 2>&1 &"
					 # Check if it's the last command; if not, append '&' at the end of the client command.
					if [[ $i -lt $((flujo - 1)) ]]; then
						iperf_command="iperf3 -c 10.0.1.7 -u -p $((5000 + i)) --cport $((10000 + i)) -b ${rate}M -i 10 -t 300"
        				else
						iperf_command="iperf3 -c 10.0.1.7 -u -p $((5000 + i)) --cport $((10000 + i)) -b ${rate}M -i 10 -t 300"
					fi
					
					echo "Starting iperf server on $iperf_server_host"
					ssh "destination" "$iperf_server_command" 
					#sleep 1  # Add a sleep command to wait for the server to initialize
					
					if [[ $i -lt $((flujo - 1)) ]]; then
						echo "Executing iperf client remotely on $remote_host as $ssh_user: $iperf_command"
						ssh "source" "$iperf_command" &
        				else
						echo "Executing iperf client remotely on $remote_host as $ssh_user: $iperf_command"
						ssh "source" "$iperf_command"
					fi 
				done
			
				# After a client test are completed, retrieve the server-side results
				echo "Finished. Retrieving iperf server results from $iperf_server_host"
				scp "destination:/home/netcom/Downloads/results/Qbv_tsn_iperf_q${q_time}_f${flujo}_c${ciclo}_${rate}.txt" /home/netcom-i11-16/Downloads/results/tsn/
			
				if [ $? -eq 0 ]; then
					echo "iperf server results file copied successfully to /home/netcom-i11-16/Downloads/results/"
					ssh "destination" "rm -r /home/netcom/Downloads/results/Qbv_tsn_iperf_q${q_time}_f${flujo}_c${ciclo}_${rate}.txt"
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
				scp "destination:/home/netcom/Downloads/results/Qbv_tsn_iperf_server_q${q_time}_f${flujo}_c${ciclo}_${rate}.pcap" "core:/mnt/imagenes/pcaps/pcaps_server/tsn/"
				sleep 2
				echo "deleting the file from server"
				ssh "destination" "rm -r /home/netcom/Downloads/results/Qbv_tsn_iperf_server_q${q_time}_f${flujo}_c${ciclo}_${rate}.pcap"
				echo "deleted"
				echo "retrieving pcap from client"
				scp "source:/home/netcom/Downloads/results/Qbv_tsn_iperf_client_q${q_time}_f${flujo}_c${ciclo}_${rate}.pcap" "core:/mnt/imagenes/pcaps/pcaps_client/tsn/"
				sleep 2
				echo "deleting the file from client"
				ssh "source" "rm -r /home/netcom/Downloads/results/Qbv_tsn_iperf_client_q${q_time}_f${flujo}_c${ciclo}_${rate}.pcap"
				echo "deleted"
			done	
		done
	done	
done


# Optionally, stop the iperf server or leave it running based on your requirement
#sshpass -p "$iperf_server_password" ssh "$iperf_server_user@$iperf_server_host" "killall iperf3"
