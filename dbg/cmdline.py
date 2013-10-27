
import time

from net import con

ent=con(127, "s")

print("opening connection")
ent.connect()
time.sleep(0.1)

print("doing hit")
ent.outgoingq.put(('evnt',{'name':'got_hit_event','weapon':'basic','team':'teamblu','from':7589}))
time.sleep(0.1)

print("doing ping")
ent.outgoingq.put(('evnt',{'name':'ping_event','testdata':'woot'}))
print("waiting for pong...")
print(ent.incomingq.get())
time.sleep(0.1)

print("closing connection")
ent.close()
