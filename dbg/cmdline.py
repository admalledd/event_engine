


from net import con

ent=con(127, b"s")

print("opening connection")
ent.connect()

print("doing hit")
ent.outgoingq.put((b'evnt',{'name':'got_hit_event','weapon':'basic','team':'teamblu','from':7589}))

print("doing ping")
ent.outgoingq.put((b'evnt',{'name':'ping_event','testdata':'woot'}))


print("closing connection")
ent.close()