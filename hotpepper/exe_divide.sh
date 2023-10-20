cd _async/async_n0
pwd
which python
echo "async_n0"
# /opt/homebrew/bin/python3.11 ../../getSalonDetail.py

for i in {8..10}
do
    echo "This is iteration $i"
    cd /Users/m1mac/dev/python/scrape/hotpepper/_async/async_n$i
    pwd
    /opt/homebrew/bin/python3.11 ../../getSalonDetail.py &

done
