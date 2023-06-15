#!/bin/bash

# Function to check if PostgreSQL is up
wait_for_postgres() {
    echo "Waiting for PostgreSQL to start"

    host="$1"
    port="$2"
    retries=5
    while [[ $retries -ge 0 ]]
    do
        nc -z "$host" "$port"
        result=$?
        
        if [ $result -eq 0 ]; then
            echo "PostgreSQL started"
            return 0
        fi

        retries=$((retries-1))
        sleep 10
    done

    echo "Failed to connect to PostgreSQL"
    return 1
}

# Call the function with PostgreSQL host and port
wait_for_postgres "postgres" 5432

# Execute your Python script
exec python usg_sprint_9/main.py
