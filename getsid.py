import win32api
import win32security
uname=win32api.GetUserName()
print "You are",uname
sid,domain,atype=win32security.LookupAccountName(None,uname)
print "You have SID",str(sid).split(':')[1],"on domain",domain,"with type",atype