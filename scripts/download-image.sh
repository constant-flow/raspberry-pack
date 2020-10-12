#!/bin/bash
while [ $# -gt 0 ]; do

   if [[ $1 == *"-"* ]]; then
        v="${1/-/}"
        declare $v="$2"
   fi

  shift
done

rm *.img
curl -L $url -o temp.zip
unzip temp.zip
rm temp.zip
mv *.img raspberry-pack.img
echo $url > raspberry-pack.img.version
sleep 3