'''
this is the constant deffinition file 

'''
from lib.cfg import abs_suit as cfg


#what the suit gives when it sends data, a 4 byte type, request, response and status update only.

#contains all 4-byte types used in first section of packet
first=cfg['first_type'].values()


#Query sub types, for when the server askes a question of the suit, and the suit responds
query=cfg['query_type'].values()