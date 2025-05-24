from datetime import datetime, timedelta

agora = datetime.now()
amanha = agora + timedelta(days=1)

print("Agora:", agora)
print("Amanhã:", amanha)
