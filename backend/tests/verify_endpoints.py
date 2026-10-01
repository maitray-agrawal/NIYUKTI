import urllib.request
import urllib.parse
import json

def run_tests():
    base = 'http://127.0.0.1:8000/api'
    
    # 1. Test /candidates/locations
    with urllib.request.urlopen(f'{base}/candidates/locations') as resp:
        loc_data = json.loads(resp.read().decode())
        print('1. /locations total:', loc_data['total_candidates'])
        for h in loc_data['hubs'][:6]:
            print(f'   {h["city"]}: {h["count"]} ({h["percentage"]}%)')
            
    # 2. Test search with aliases
    for loc in ['Bengaluru', 'Delhi-NCR', 'Pune', 'Mumbai']:
        url = f'{base}/candidates/?location={urllib.parse.quote(loc)}&limit=5'
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode())
            print(f'2. Search location="{loc}": {len(data)} results, X-Total-Count={resp.headers.get("X-Total-Count")}')
            
    # 3. Test skill and title search via q
    for q in ['Python', 'FastAPI', 'Data Scientist', 'Pune']:
        url = f'{base}/candidates/?q={urllib.parse.quote(q)}&limit=5'
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode())
            print(f'3. Search q="{q}": {len(data)} results, X-Total-Count={resp.headers.get("X-Total-Count")}')

if __name__ == '__main__':
    run_tests()
