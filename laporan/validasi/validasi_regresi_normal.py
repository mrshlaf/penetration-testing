"""Uji regresi HTTP normal pada salinan terisolasi versi perbaikan."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode
import argparse, http.client, json, os, shutil, socket, subprocess, tempfile, time
from bs4 import BeautifulSoup

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
 parser.add_argument("--out",type=Path,default=Path(__file__).resolve().parent)
 args=parser.parse_args()
 repo=args.repo.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
 node=shutil.which("node")
 if not node:raise RuntimeError("Node.js tidak ditemukan")
 deps=repo/"node_modules"
 if not deps.exists():raise RuntimeError("Dependensi Node belum tersedia; pasang dependensi proyek terlebih dahulu.")
 work=Path(tempfile.mkdtemp(prefix="kemjar-regresi-"))
 version=subprocess.check_output(["git","-C",str(repo),"rev-parse","v2-patched"],text=True).strip()
 for name in ["server.js","header.ejs","footer.ejs","dokumen.ejs","aspirasi.ejs"]:
  data=subprocess.check_output(["git","-C",str(repo),"show",f"v2-patched:{name}"])
  (work/name).write_bytes(data)
 (work/"docs").mkdir()
 documents=["panduan_kurikulum_2026.txt","kalender_akademik_gasal.txt","tata_tertib_laboratorium.txt"]
 for name in documents:
  data=subprocess.check_output(["git","-C",str(repo),"show",f"v2-patched:docs/{name}"])
  (work/"docs"/name).write_bytes(data)
 (work/"aspirasi.json").write_text("[]",encoding="utf-8")
 # Bind hanya ke loopback; logika rute dan templat tetap berasal dari tag perbaikan.
 path=work/"server.js"
 path.write_text(path.read_text(encoding="utf-8").replace("app.listen(PORT, ()","app.listen(PORT, '127.0.0.1', ()"),encoding="utf-8")
 sock=socket.socket();sock.bind(("127.0.0.1",0));port=sock.getsockname()[1];sock.close()
 env=dict(os.environ)
 for key in list(env):
  if key.upper().startswith("SUPABASE"):env.pop(key)
 env.update(PORT=str(port),NODE_ENV="test",NODE_PATH=str(deps),SUPABASE_URL="")
 proc=None;log=(work/"server.log").open("w",encoding="utf-8")
 flags=getattr(subprocess,"CREATE_NO_WINDOW",0)
 records=[]
 def request(method,path,body=None):
  conn=http.client.HTTPConnection("127.0.0.1",port,timeout=10)
  headers={}
  if body is not None:
   body=urlencode(body);headers["Content-Type"]="application/x-www-form-urlencoded"
  conn.request(method,path,body=body,headers=headers)
  res=conn.getresponse();status=res.status;hdr={k.lower():v for k,v in res.getheaders()}
  text=res.read().decode("utf-8");conn.close()
  return status,hdr,text
 def start():
  nonlocal proc
  proc=subprocess.Popen([node,str(work/"server.js")],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
  deadline=time.monotonic()+15
  while time.monotonic()<deadline:
   if proc.poll() is not None:raise RuntimeError("Server uji gagal dimulai")
   try:
    if request("GET","/dokumen")[0]==200:return
   except (OSError,http.client.HTTPException):pass
   time.sleep(.1)
  raise RuntimeError("Server uji tidak siap")
 def stop():
  nonlocal proc
  if proc and proc.poll() is None:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
 def record(ident,title,check):
  try:
   detail=check()
   records.append({"id":ident,"test":title,"status":"PASS","result":detail})
  except Exception as exc:
   records.append({"id":ident,"test":title,"status":"FAIL","result":str(exc)})
   raise
 def redirect():
  status,h,_=request("GET","/")
  assert status==302 and h.get("location")=="/dokumen"
  return "302 dan Location /dokumen"
 def document(name):
  status,_,text=request("GET","/dokumen?"+urlencode({"file":name}))
  node=BeautifulSoup(text,"html.parser").select_one(".doc-content")
  assert status==200 and node is not None
  assert node.get_text().strip()==(work/"docs"/name).read_text(encoding="utf-8").strip()
  return "200; isi cocok dengan dokumen pada tag perbaikan"
 def empty():
  status,_,text=request("GET","/aspirasi")
  assert status==200 and len(BeautifulSoup(text,"html.parser").select(".aspirasi-text"))==0
  return "200; datastore awal kosong"
 def post_message(message):
  status,h,_=request("POST","/aspirasi",{"nama":"Penguji Regresi","kategori":"Akademik","pesan":message})
  assert status==302 and h.get("location")=="/aspirasi?terkirim=1"
  status,_,text=request("GET","/aspirasi")
  assert status==200
  items=BeautifulSoup(text,"html.parser").select(".aspirasi-text")
  found=next(x for x in items if x.get_text()==message)
  return found
 def normal():
  post_message("Layanan akademik berjalan normal.")
  return "POST 302; pesan normal muncul pada GET berikutnya"
 def encoding():
  message="Catatan <b>format</b> & layanan"
  item=post_message(message)
  assert item.find("b") is None and item.get_text()==message
  return "Karakter khusus tampil sebagai teks; tidak terbentuk elemen b"
 def headers():
  expected={"content-security-policy":"default-src 'self'","x-frame-options":"DENY","x-content-type-options":"nosniff"}
  for path in ["/dokumen","/aspirasi"]:
   status,h,_=request("GET",path)
   assert status==200 and all(h.get(k)==v for k,v in expected.items())
  return "Tiga nilai header sesuai pada /dokumen dan /aspirasi"
 def unavailable():
  status,_,text=request("GET","/dokumen?"+urlencode({"file":"dokumen-tidak-tersedia.txt"}))
  assert status==403 and BeautifulSoup(text,"html.parser").select_one(".doc-content") is None
  return "403; berkas biasa di luar daftar tidak dibaca"
 def restart():
  data=json.loads((work/"aspirasi.json").read_text(encoding="utf-8"))
  assert len(data)==2
  stop();start()
  status,_,text=request("GET","/aspirasi")
  soup=BeautifulSoup(text,"html.parser")
  messages=[x.get_text() for x in soup.select(".aspirasi-text")]
  assert status==200 and len(messages)==2
  assert "Layanan akademik berjalan normal." in messages and "Catatan <b>format</b> & layanan" in messages
  assert all(x.find("b") is None for x in soup.select(".aspirasi-text"))
  return "Dua rekaman tetap ada setelah restart; teks khusus tetap di-escape"
 failure=None
 try:
  start()
  record("R01","Pengalihan beranda",redirect)
  for i,name in enumerate(documents,2):
   record(f"R{i:02}","Dokumen resmi: "+name,lambda n=name:document(n))
  record("R05","Forum awal",empty)
  record("R06","Pengiriman pesan normal",normal)
  record("R07","Encoding teks HTML nonaktif",encoding)
  record("R08","Header keamanan",headers)
  record("R09","Nama dokumen biasa di luar daftar",unavailable)
  record("R10","Persistensi JSON setelah restart",restart)
 except Exception as exc:failure=str(exc)
 finally:
  stop();log.close()
  results={"timestamp":datetime.now(timezone.utc).isoformat(),"source_tag":"v2-patched","source_commit":version,
   "storage":"JSON lokal terisolasi; Supabase dinonaktifkan","binding":"127.0.0.1","runtime":subprocess.check_output([node,"--version"],text=True).strip(),
   "scope":"Regresi HTTP normal dan encoding teks; bukan pengujian eksekusi script di peramban.",
   "cases":records,"passed":sum(x["status"]=="PASS" for x in records),"failed":sum(x["status"]=="FAIL" for x in records),"error":failure}
  (out/"hasil_regresi_normal.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
  print(json.dumps(results,ensure_ascii=False))
 if failure:raise SystemExit(1)

if __name__=="__main__":main()

