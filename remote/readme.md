Here is where all the "remotely accessable" plugins will go. (or more, the "remote" sub-sub folder)

The reason for the nesting is to make sure to break the normal python importer on the server side, clients need not worry
they just use the RemoteImporter as per normal. 


Note that EVERY "remote plugin" MUST also conform to the server plugin methodology!