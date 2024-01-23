new_list=[]
lst = [1, [2, 3], [[2], 5], 6]

def flatten(lst) :
    if all(isinstance(i,int) for i in lst):
        [new_list.append(i) for i in lst]
        return new_list
    return flatten(sum([[i] if isinstance(i,int) else i for i in lst],[]))

print(flatten(lst))
print(new_list)