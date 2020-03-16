cd $1
rm cscope.in.out cscope.out cscope.po.out cscope.files
find . -name '*.[ch]' -o -name '*.cpp' -o -name '*.cc' > cscope.files
cscope -b -q -k