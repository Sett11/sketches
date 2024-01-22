b,c,d,e=int(input()),int(input()),int(input()),int(input())
print(['NO','YES'][(d,e) in [(b-1,c+2),(b+1,c+2),(b-1,c-2),(b+1,c-2),(b+2,c-1),(b+2,c+1),(b-2,c-1),(b-2,c+1)]])