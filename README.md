
# idea

# plan

- get a copy of some sort of trace data
- figure a better format for chreod data, maybe just tab delim
- write utility for converting

- figure and grab osm data subset for new york
- figure specification for street network, intersections as nodes,
  streets and models of connections between the two
- convert OSM data to a street network

- figure out how to calculate distance between a point and a line
  model
- figure an alignment algorithm to assing points to street segments

# organization

`data`
: OSM, chreod/trace, streetnetworks, etc. data in several directories
    `osm`
    : is osm data, in xml
    `gpx`
    : is gpx trace files, in xml
    `traces`
    : are gpx proced to a tab-delimited format

`src`
: little scripts and things

`outz`
: output, plots and things

