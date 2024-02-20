#!/bin/bash

# Remote host details for the iperf client
remote_host="163.117.140.101"
ssh_user="netcom"
ssh_password="netcom;"

# Iperf server details
iperf_server_host="163.117.140.243"
iperf_server_user="netcom"
iperf_server_password="netcom;"

# Folder path to store results on the remote host and iperf server
client_results_folder="/home/netcom/Downloads/results/"
server_results_folder="/home/netcom/Downloads/results/"

# Ensure the folder exists on the iperf server to store results
sshpass -p "$iperf_server_password" ssh "$iperf_server_user@$iperf_server_host" "[ -d \"$server_results_folder\" ] || mkdir -p \"$server_results_folder\""

# Start the iperf server on a different machine with output redirected to a file
echo "Starting iperf server on $iperf_server_host"
sshpass -p "$iperf_server_password" ssh "$iperf_server_user@$iperf_server_host" "nohup iperf3 -s -p 5002 -1 --logfile $server_results_folder/iperf_server_output_be.txt > /dev/null 2>&1 &"
sleep 2  # Add a sleep command to wait for the server to initialize
echo "iperf server started on $iperf_server_host with output logging"

# Array of rates to test
rates="90"

# Duration for the ping command (adjust as needed)
ping_duration="10"

# Loop through each rate
for rate in "${rates[@]}"; do
    # iperf client command to be executed on the remote host
    iperf_command="iperf3 -c 10.0.1.7 -u -p 5002 --cport 10002 -b ${rate}M -i 1 -t 80"

    echo "Executing iperf client remotely on $remote_host as $ssh_user: $iperf_command"

    # Use SSH with password to execute the iperf client command on the remote host
    sshpass -p "$ssh_password" ssh "$ssh_user@$remote_host" "$iperf_command"

    # Since the server collects all results, no need to check each client execution status here for result collection
done

# After all client tests are completed, retrieve the server-side results
echo "Retrieving iperf server results from $iperf_server_host"
sshpass -p "$iperf_server_password" scp "$iperf_server_user@$iperf_server_host:$server_results_folder/iperf_server_output_be.txt" /home/netcom-i11-16/Downloads/results/
if [ $? -eq 0 ]; then
    echo "iperf server results file copied successfully to /home/netcom/Downloads/results/"
else
    echo "Error copying iperf server results file from $iperf_server_host."
fi

# Optionally, stop the iperf server or leave it running based on your requirement
#sshpass -p "$iperf_server_password" ssh "$iperf_server_user@$iperf_server_host" "killall iperf3"
