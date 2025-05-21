import os
import threading
import time
import subprocess

def get_users():
    
    output = subprocess.check_output(
        ['docker', 'ps', '--filter', 'name=host', '--format', '{{.Names}}'],
        text=True
    )
    return sorted(output.strip().splitlines())

def extract_num_host(name):
  
    pre = name.split('-')[1]
    result = pre.split('host')[1]
    result1 = result[:-1]
    result2 = result[-1]
    return result1, result2
   
def ping_task(frm, to, ip, results, lock_thread):
   
    start = time.time()
    cmd = f"docker exec {frm} ping -c 5 -W 0.1 {ip}"
    print(f"{cmd}")

    code = os.system(cmd)
    elapsed = time.time() - start
    success = (code == 0)

    with lock_thread:
        results.append((frm, to, success, elapsed))

def main():
    
    users = get_users()
    if not users:
        print(f"Erro: nenhum host rodando. Execute 'make up'.")
        return
    
    tasks = [(frm, to, f"172.20.{extract_num_host(to)[0]}.1{extract_num_host(to)[1]}") for frm in users for to in users if frm != to]
    
    results = []
    threads = []
    lock_thread = threading.Lock()
    
    for frm, to, ip in tasks:
        thread = threading.Thread(target=ping_task, args=(frm, to, ip, results, lock_thread))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    summary = {}
    
    for frm, to, ok, tempo in results:
        summary.setdefault(frm, []).append((to, ok, tempo))
    
    total_ok = 0
    total = len(results)
    
    for frm in sorted(summary):
        print(f"\n=== Host {frm} ===")
        
        for to, ok, tempo in summary[frm]:
            
            status = "OK" if ok else "Falha"
            
            print(f"{frm} -> {to}: {status} ({tempo:.2f}s)")
            if ok:
                total_ok += 1
            
    print(f"\nTotal de pings: {total}, Sucessos: {total_ok}, Falhas: {total - total_ok}")

if __name__ == "__main__":
    main()