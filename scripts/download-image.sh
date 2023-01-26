#!/bin/bash
while [ $# -gt 0 ]; do

   if [[ $1 == *"-"* ]]; then
        v="${1/-/}"
        declare $v="$2"
   fi

  shift
done

rm *.img
curl -L $url -o temp.img.xz
unxz temp.img.xz
# rm temp.xz
mv *.img raspberry-pack.img
echo $url > raspberry-pack.img.version
echo "\aImage download done."
sleep 3