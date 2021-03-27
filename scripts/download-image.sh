#!/bin/bash
while [ $# -gt 0 ]; do

   if [[ $1 == *"-"* ]]; then
        v="${1/-/}"
        declare $v="$2"
   fi

  shift
done

rm *.img

if command -v curl &> /dev/null
then
    # osx default
    echo "Use curl to download"
    curl -L $url -o temp.zip
else
    # linux default
    echo "Use wget to download"
    wget -O temp.zip --show-progress $url
fi

unzip temp.zip
rm temp.zip
mv *.img raspberry-pack.img
echo $url > raspberry-pack.img.version
echo "\aImage download done."
sleep 3