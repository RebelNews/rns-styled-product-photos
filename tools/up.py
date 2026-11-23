import json,re,sys,subprocess,os,concurrent.futures as cf
f,off=sys.argv[1],int(sys.argv[2])
txt=''.join(t.get('text','') for t in json.load(open(f)))
d=json.loads(re.search(r'\{"data".*\}',txt,re.S).group(0))['data']
targets=[d[k]['stagedTargets'][0] for k in sorted(d,key=lambda s:int(s[1:]))]
todo=json.load(open('work/todo_good.json'))[off:off+len(targets)]
done=json.load(open('work/uploaded.json')) if os.path.exists('work/uploaded.json') else {}
def up(pair):
    r,t=pair
    cmd=['curl','-sS','-m','120','-o','/dev/null','-w','%{http_code}',t['url']]
    for p in t['parameters']: cmd+=['--form-string',f"{p['name']}={p['value']}"]
    cmd+=['-F',f"file=@{r['out']};type=image/jpeg"]
    code=subprocess.run(cmd,capture_output=True,text=True).stdout
    return r,t,code
bad=0
with cf.ThreadPoolExecutor(6) as ex:
    for r,t,code in ex.map(up,zip(todo,targets)):
        if code in('201','204','200'): done[r['mid']]={'url':t['resourceUrl'],'pid':r['padm'],'fn':r['fn'],'bg':r['bg'],'alt':r['alt'],'title':r['title'],'applied':False}
        else: bad+=1
json.dump(done,open('work/uploaded.json','w'))
print('uploaded',len(todo)-bad,'bad',bad,'total',len(done))
print(targets[0]['resourceUrl'])
