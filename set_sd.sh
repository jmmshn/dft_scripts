#!/bin/bash
lin_num=0
#move=( Pb I )
move=( "$@" )

coord_line=-100
echo ${move[0]}
rm POSCAR.sel
while read line
do
  (( lin_num++ ))
  if [ $lin_num -lt 6 ]; then
    echo "$line" >> POSCAR.sel
    continue
  elif [ $lin_num -eq 6 ]; then
    atom=($line)
    echo "$line" >> POSCAR.sel
    continue
  elif [ $lin_num -eq 7 ]; then
    n_atom=($line)
    echo "$line" >> POSCAR.sel
    # Creat a larg array of atom names and count
    ntot=0
    name_list=''
    for ((i=0; i<${#atom[*]}; i++));
    do
      #echo ${atom[i]} ${n_atom[i]}
      ntot=$((ntot + ${n_atom[i]}))
      name_list=$name_list$(printf "${atom[i]} %.0s" $(seq 1 ${n_atom[i]}))
    done
    name_list=( $name_list )
    continue
  elif [ $lin_num -eq 8 ]; then
    # check selective dynamics
    word=$(echo $line | cut -d " " -f1)
    if [  ${word,,} != 'selective' ]; then
      echo Selective dynamics >> POSCAR.sel
      echo Direct >> POSCAR.sel
      coord_line=$lin_num
      echo $lin_num
    else
      echo "$line" >> POSCAR.sel
      coord_line=$((lin_num + 1))
      echo $lin_num $coord_line
    fi
    continue
  elif [ $coord_line -eq $lin_num ]; then
    echo $line >> POSCAR.sel
  elif [ $lin_num -lt $((coord_line + ntot + 1)) ]; then
    move_this=0
    current_atom=$((lin_num - coord_line - 1))
    echo $current_atom
    current_atom_name=${name_list[current_atom]}

    for element in ${move[*]};
    do
      if [ $current_atom_name == $element ]; then
        move_this=1
      fi
    done

    if [ $move_this == 1 ]; then
      echo $line | awk '{print $1, $2, $3" T T T"}' >> POSCAR.sel
    else 
      echo $line | awk '{print $1, $2, $3" F F F"}' >> POSCAR.sel
    fi
  else
    continue
  fi



done < POSCAR
