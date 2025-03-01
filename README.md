# Redis and Pinot (SQL) Geospatial Search

## Contents
1.  [Summary](#summary)
2.  [Architecture](#architecture)
3.  [Features](#features)
4.  [Prerequisites](#prerequisites)
5.  [Installation](#installation)
6.  [Usage](#usage)
7.  [Sample Query](#query)

## Summary <a name="summary"></a>
This is a Docker-based deployment of Redis and Apache Pinot.  It includes a notebook with equivalent geospatial queries utilizing the Redis Query Engine (RQE) syntax and SQL syntax with Apache Pinot OSS.

## Architecture <a name="architecture"></a>
![architecture](https://docs.google.com/drawings/d/e/2PACX-1vSx2JFAePUvUmBzbuMA6xmqPWWAySxqQ53a5z33xu5qqwZhxvkeAsW5LiW9-3WsSZ0QwIXyJ32ub7V0/pub?w=822&h=586)  

## Features <a name="features"></a>
- Builds a Redis and Apache Pinot architecture in Docker:  1-node, 1-shard Redis Software cluster, 3-node, 1-segment Apache Pinot OSS cluster.
- Generates a 1 million-record JSON geospatial data set covering the US
- Loads those records into Redis and Pinot with no-code tools
    - Redis
        - redis-cli is used for index creation
        - riot is used for data loading
    - Pinot 
        - pinot-admin.sh is used for table creation and data loading
- Jupyter notebook demonstrating equivalent Redis and Pinot queries


## Prerequisites <a name="prerequisites"></a>
- Docker
- Docker Compose
- python3
- [riot](https://github.com/redis/riot)
- [redis-cli](https://redis.io/docs/latest/develop/tools/cli/)
- [jq](https://github.com/jqlang/jq)

## Installation <a name="installation"></a>
```bash
git clone https://github.com/joeywhelan/redis-pinot-geo.git && cd redis-pinot-geo
pip install faker shapely
```

## Usage <a name="usage"></a>
### Docker Containers Start-up
```bash
./start.sh
```
### Jupyter Notebook
```
src/geodemo.ipynb
```
### Docker Containers Stop
```bash
./stop.sh
```
###

## Sample Query <a name="query"></a>
### Redis
```bash
FT.AGGREGATE locationidx '(@point_wkt:[WITHIN $WP1] | @point_wkt:[WITHIN $WP2])' 
PARAMS 4 
WP1 'POLYGON((-105.080 38.980, -105.020 38.980, -105.020 38.920, -105.080 38.920, -105.080 38.980))' 
WP2 'POLYGON((-105.110 38.960, -105.050 38.960, -105.050 38.900, -105.110 38.900, -105.110 38.960))' 
LOAD 1 @dob 
GROUPBY 1 @dob 
REDUCE COUNT 0 AS Total 
SORTBY 2 @Total DESC 
DIALECT 2
```
### Pinot
```sql
SELECT dob,
  COUNT(*) AS Total
FROM locations
WHERE ST_Within(
    point_h3,
    toSphericalGeography(
      ST_GeomFromText(
        'POLYGON((-105.080 38.980, -105.020 38.980, -105.020 38.920, -105.080 38.920, -105.080 38.980))'
      )
    )
  ) IS True
  OR ST_Within(
    point_h3,
    toSphericalGeography(
      ST_GeomFromText(
        'POLYGON((-105.110 38.960, -105.050 38.960, -105.050 38.900, -105.110 38.900, -105.110 38.960))'
      )
    )
  ) IS True
GROUP BY dob
ORDER BY Total DESC;
```