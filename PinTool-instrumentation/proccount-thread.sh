
# $@ is the application with its arguments

echo "PROCCOUNT"

pin-3.11/pin -t pin-3.11/source/tools/ManualExamples/obj-intel64/proccount-thread1.so -- $@ 

mv proccount2.out $1-proccount.out
mv proccount1.out $1-func.out

echo "CREATE FUNC"
python proccount1.py $1-proccount.out