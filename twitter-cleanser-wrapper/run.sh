#!/bin/bash

export TEXT_CLEANSER_HOME=/media/Data/work/Development/EclipseWorkspace/TextCleanser/penguin-src
LIBRARIES=lib/guava-r09.jar:lib/lucene-core-3.0.3.jar:lib/text-0.1.0.jar:lib/text-0.1.0-sources.jar:lib/twitter-text-1.1.8.jar

mkdir -p bin
javac -d bin -cp $LIBRARIES src/edu/isi/twitter_cleanser/*.java
java -cp $LIBRARIES:bin edu.isi.twitter_cleanser.TextCleanserUsageExample
