#!/bin/bash
DATA=$PWD/data/locations.json

docker compose up -d
curl -s -o /dev/null --retry 5 --retry-all-errors --retry-delay 3 -f -k -u "redis@redis.com:redis" https://localhost:9443/v1/bootstrap

echo -e "\n*** Build Redis Cluster ***"
docker exec -it re1 /opt/redislabs/bin/rladmin cluster create name cluster.local username redis@redis.com password redis
docker exec -it re2 /opt/redislabs/bin/rladmin cluster join nodes 192.168.20.2 username redis@redis.com password redis
docker exec -it re3 /opt/redislabs/bin/rladmin cluster join nodes 192.168.20.2 username redis@redis.com password redis
sleep 1

echo -e "\n*** Build Target Redis DB ***"
curl -s -o /dev/null -k -u "redis@redis.com:redis" https://localhost:9443/v1/bdbs -H "Content-Type:application/json" -d @$PWD/redis/redb.json

if [ ! -f $DATA ]
then
    echo -e "\n*** Generate Data ***"
    python3 $PWD/src/datagen.py
fi

sleep 5
echo -e "\n*** Create Redis Index ***"
redis-cli -h localhost -p 12000 FT.CREATE locationidx ON JSON PREFIX 1 location: SCHEMA $.point_lnglat AS point_lnglat GEO SORTABLE $.point_wkt AS point_wkt GEOSHAPE SPHERICAL SORTABLE $.dob AS dob NUMERIC SORTABLE $.uuid AS uuid TAG SORTABLE

echo -e "\n*** Ingest Data to Redis ***"
riot file-import -h localhost -p 12000 --threads 20 $DATA json.set --keyspace location --key uuid

echo -e "\n*** Build Pinot Schema and Table ***"
docker exec -it pinot-controller /opt/pinot/bin/pinot-admin.sh AddTable -tableConfigFile /tmp/pinot/config/table.json -schemaFile /tmp/pinot/config/schema.json -controllerHost localhost -controllerPort 9000 -exec > /dev/null 2>&1

sleep 1
echo -e "\n*** Ingest Data to Pinot ***"
docker exec -it pinot-controller /opt/pinot/bin/pinot-admin.sh LaunchDataIngestionJob -jobSpecFile /tmp/pinot/config/job-spec.yaml > /dev/null 2>&1