


from net import con

ent=con(127, b"s")

print("opening connection")
ent.connect()

print("doing hit")
ent.outgoingq.put((b'ghit',{'weapon':'basic','team':'teamblu','from':7589}))

print("closing connection")
ent.close()