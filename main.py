from collections import Counter

c=Counter(input().lower())
print(f"Аденин: {c['а']}",f"Гуанин: {c['г']}",f"Цитозин: {c['ц']}",f"Тимин: {c['т']}",sep='\n')