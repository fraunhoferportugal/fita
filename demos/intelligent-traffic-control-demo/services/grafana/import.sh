# mkdir -p datasources && curl -s "http://172.16.5.81:45000/api/datasources"  -u admin:yO5rE3MoJ3JgXRmdRrVAAchmrg37RiFA2YZNQXvU | jq -c -M '.[]' | split -l 1 - datasources/
#!/bin/bash
set -e

DIR=$(cd "$(dirname "$0")" && pwd)
GRAFANA_URL="http://localhost:45000"
GRAFANA_USER="admin"
GRAFANA_PASSWORD=""
INFLUX_TOKEN=""

usage()
{
    echo "$SCRIPT_NAME [options]"
    echo "options"
    echo " -l, --url          Grafana URL (default: $GRAFANA_URL)"
    echo " -u, --username     Grafana Username (default: $GRAFANA_USER)"
    echo " -p, --password     Grafana Password (default: $GRAFANA_PASSWORD)"
    echo " -t, --influx_token Influx Token (default: $INFLUX_TOKEN)"
    exit 1;
}

process_args()
{
    save_next_arg=0
    for arg in "$@"
    do
        if [ $save_next_arg -eq 1 ]; then
            GRAFANA_URL="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 2 ]; then
            GRAFANA_USER="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 3 ]; then
            GRAFANA_PASSWORD="$arg"
            save_next_arg=0
        elif [ $save_next_arg -eq 4 ]; then
            INFLUX_TOKEN="$arg"
            save_next_arg=0
        else
            case "$arg" in
                "-h" | "--help" ) usage;;
                "-l" | "--url" ) save_next_arg=1;;
                "-u" | "--username" ) save_next_arg=2;;
                "-p" | "--password" ) save_next_arg=3;;
                "-t" | "--influx_token" ) save_next_arg=4;;
                * ) usage;;
            esac
        fi
    done
}

# process command line args
process_args "$@"

# get influxdb datasource
datasource=$(cat $DIR/datasources/influxdb.json)

# replace by the token
datasource=${datasource/<>/$INFLUX_TOKEN}

# post it to Grafana
curl -X "POST" "$GRAFANA_URL/api/datasources" \
    -H "Content-Type: application/json" \
    --user $GRAFANA_USER:$GRAFANA_PASSWORD \
    --data-binary "$datasource"
echo ""

# get prometheus datasource
datasource=$(cat $DIR/datasources/prometheus.json)

# post it to Grafana
curl -X "POST" "$GRAFANA_URL/api/datasources" \
    -H "Content-Type: application/json" \
    --user $GRAFANA_USER:$GRAFANA_PASSWORD \
    --data-binary "$datasource"
echo ""

# get dashboard
dashboard=$(cat $DIR/dashboard.json)

# post it to Grafana
curl -X "POST" "$GRAFANA_URL/api/dashboards/import" \
    -H "Content-Type: application/json" \
    --user $GRAFANA_USER:$GRAFANA_PASSWORD \
    --data-binary "$dashboard"

echo "Done"
