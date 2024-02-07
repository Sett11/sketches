a,b,c=[set(input().split()) for _ in range(3)]
print(*sorted(((a|b)-c)|((a|c)-b)|((b|c)-a),key=int))