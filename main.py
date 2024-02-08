build_query_string = lambda a:'&'.join(map(lambda x:f'{x[0]}={x[1]}',sorted(a.items())))

print(build_query_string({'sport': 'hockey', 'game': 2, 'time': 17}))