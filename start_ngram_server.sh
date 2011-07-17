#!/bin/bash
# update with your own paths
LATTICE_TOOL_DIR=/media/Data/work/Tools/srilm/bin/i686-m64
LM_DIR=/media/Data/work/Development/EclipseWorkspace/TextCleanser/data/
$LATTICE_TOOL_DIR/ngram -lm $LM_DIR/tweet-lm.gz -mix-lm $LM_DIR/latimes-lm.gz -lambda 0.7 -mix-lambda2 0.3 -server-port 12345 &
