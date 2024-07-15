#step1:remove comment.txt
#    rm debugfile

#step2:execute pythonfile,convert txtfile to ascfile&patfile
path=$1
files=$(ls $path)

for inputfile in $files
do
  if [[ $inputfile =~ ".py" ]]; then
    # echo $inputfile >> debugfile

    python $inputfile
  fi
done
