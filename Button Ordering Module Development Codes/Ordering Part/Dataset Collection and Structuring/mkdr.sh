arr=("1" "2" "3" "4" "5" "6" "7" "8" "9" "10")

for fld in "${arr[@]}"
do 
  # echo "$fld : "
  echo "ls ./$fld/csv" | bash
done
