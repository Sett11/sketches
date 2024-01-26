from re import match

print(['NO','YES'][bool(match(r'^(7-)?\d{3}-\d{3}-\d{4}$',input()))])