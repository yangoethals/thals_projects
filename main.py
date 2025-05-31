import speedtest

wifi=speedtest.Speedtest()

print("download:",round(wifi.download()/1000000,2),"Mbs")
print("upload:",round(wifi.upload()/1000000,2),"Mbs")
