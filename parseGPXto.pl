#!/usr/bin/perl -w


use XML::LibXML;

sub parseGPXFileto {
# give me the first argument as a filename of a gpx to parse
  $dom = XML::LibXML->load_xml(location=>$_[0]);
  foreach my $tracksegment ($dom->findnodes('//trkseg')) {
    my @tracksegment;
    foreach my $trackpoint ($tracksegment->findnodes('trkpt') {
      print $trackpoint->to_literal();
#      push @tracksegment, ;
    }
  }
}

opendir (GPX,"./data/gpx") or die $!;
while ( my $gpxFile = readdir(GPX) ) {

  print $gpxFile;

  parseGPXto("data/gpx/".$gpxFile);
}
