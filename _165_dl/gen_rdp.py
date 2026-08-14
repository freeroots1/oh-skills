words = ["admin","Admin","administrator","Administrator","bjhzsv","BjhZsv","BJHS","bjhz","beijing","Beijing","BEIJING","hongsheng","HongSheng","test","Test","shell","Shell","guest","User","password","Password"]
with open("/tmp/rdp_pwds.txt","w") as f:
    for w in words:
        f.write(w + "\n")
        for s in ["1","12","123","1234","12345","123456","888","666","999","01","001","000"]:
            f.write(w + s + "\n")
    for n in range(100000, 1001000):
        f.write(str(n) + "\n")
print("Done")
