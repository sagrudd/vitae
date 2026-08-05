#!/usr/bin/env python3
"""Bootstrap and build the long-lived, object-per-file professional graph.

Object files use JSON syntax, which is valid YAML 1.2, avoiding a runtime YAML
dependency.  Existing profile.json and product Markdown remain supported inputs.
"""
from __future__ import annotations
import csv, html, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; CONTENT=ROOT/'content'; GRAPH=ROOT/'dashboard'; SITE=ROOT/'site'
def slug(s): return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def write(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def load_dir(kind): return [json.loads(p.read_text()) for p in sorted((CONTENT/kind).glob('*.yaml'))]

def bootstrap():
    if (CONTENT/'roles').exists(): return
    p=json.loads((CONTENT/'profile.json').read_text())
    for item in p['experience']:
        employer=slug(item['organisation']); write(CONTENT/'employers'/f'{employer}.yaml',{'id':employer,'type':'Employer','name':item['organisation'],'locations':[item['location']]})
        rid=slug(item['organisation']+' '+item['role']); write(CONTENT/'roles'/f'{rid}.yaml',{'id':rid,'type':'Role','title':item['role'],'period':item['period'],'summary':item['short'],'employer':employer,'achievements':item['achievements'],'relationships':{'technologies':['nextflow','genomics'] if 'Nanopore' in item['organisation'] else ['genomics']}})
    for i,item in enumerate(p['talks'],1):
        name,_,venue=item.partition(' - '); write(CONTENT/'talks'/f'talk_{i:02}.yaml',{'id':f'talk_{i:02}','type':'Talk','title':name,'venue':venue,'relationships':{'technologies':['nextflow'] if 'Nextflow' in item else []}})
    for i,item in enumerate(p['training'],1): write(CONTENT/'training'/f'training_{i:02}.yaml',{'id':f'training_{i:02}','type':'Training Course','description':item,'relationships':{'domains':['Bioinformatics Capability Building']}})
    products={'EPI2ME':'Oxford Nanopore workflow platform.','Sputnik':'Comparative plant-genomics database platform.','openSputnik':'EST-oriented comparative genomics resource.','PlantMarkers':'Plant molecular marker database.','Éclair':'Sequence-origin web service.','Plant Breeding API':'Plant-science interoperability API.','Mnemosyne':'Independent genomics consultancy.'}
    for name,description in products.items():
        ident=slug(name); write(CONTENT/'products'/f'{ident}.yaml',{'id':ident,'type':'Product','name':name,'description':description,'problem':'Scientific data and analysis need accessible, reusable systems.','solution':description,'impact':'Connects scientific users with repeatable delivery.','technologies':['genomics','nextflow'] if name=='EPI2ME' else ['genomics'],'publications':[],'employers':['oxford_nanopore_technologies'] if name=='EPI2ME' else [],'projects':[],'career_phase':'Product leadership'})
    for name in ['COVID Response','MyGenome','Proboscis Monkey','Arabidopsis Genome','Core Facility','Commercial Bioinformatics']:
        ident=slug(name); write(CONTENT/'projects'/f'{ident}.yaml',{'id':ident,'type':'Project','name':name,'relationships':{'products':[],'publications':[],'technologies':['genomics']}})
    for name in ['Genomics','Nextflow','Long-read Sequencing','Cloud Computing','Interoperability']:
        ident=slug(name); write(CONTENT/'technologies'/f'{ident}.yaml',{'id':ident,'type':'Technology','name':name})

def build():
    bootstrap(); types=['employers','roles','talks','training','products','projects','technologies']; objects=[]
    for kind in types: objects += load_dir(kind)
    pubs=json.loads((ROOT/'publications'/'publications.yaml').read_text())['records']
    objects += [{'id':r['id'],'type':'Publication','name':r['title'],'year':r['year'],'relationships':{'categories':r['category'],'technologies':r['technologies']}} for r in pubs]
    GRAPH.mkdir(exist_ok=True); write(GRAPH/'knowledge_graph.json',{'schema_version':1,'objects':objects}); write(GRAPH/'search.json',objects)
    counts=Counter(x['type'] for x in objects); employers=load_dir('employers'); roles=load_dir('roles')
    career={'objects':dict(counts),'employers':len(employers),'countries':sorted({l for e in employers for l in e.get('locations',[])}),'leadership_progression':[{'role':r['title'],'employer':r['employer'],'period':r['period']} for r in roles]}
    write(GRAPH/'career_dashboard.json',career)
    years=Counter(r.get('year') for r in objects if r['type']=='Publication'); timeline=[{'year':y,'publication_count':n} for y,n in sorted(years.items())]
    write(GRAPH/'timeline.json',timeline)
    with (GRAPH/'timeline.csv').open('w',newline='') as f: w=csv.DictWriter(f,['year','publication_count'],lineterminator='\n');w.writeheader();w.writerows(timeline)
    (GRAPH/'timeline.tex').write_text('% Generated from dashboard/timeline.json\n\\begin{tabular}{rr}\nYear & Publications\\\\\n'+'\n'.join(f'{x["year"]} & {x["publication_count"]}\\\\' for x in timeline)+'\n\\end{tabular}\n')
    points=' '.join(f'{20+i*45},{180-min(130,x["publication_count"]*12)}' for i,x in enumerate(timeline))
    (GRAPH/'timeline.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {len(timeline)*45+40} 220"><polyline fill="none" stroke="#38647A" stroke-width="3" points="{points}"/></svg>')
    cards=''.join(f'<li><b>{html.escape(str(x.get("name",x.get("title",x["id"]))))}</b><small>{html.escape(x["type"])}</small></li>' for x in objects)
    shared='<style>:root{color-scheme:light dark}body{font:16px system-ui;max-width:1000px;margin:3rem auto;padding:0 1rem}input{width:100%;padding:1rem}li{padding:.6rem;border-bottom:1px solid #ccd}small{margin-left:1rem;color:#687}a{color:inherit}</style>'
    search=f'<!doctype html><meta charset=utf-8>{shared}<h1>Professional knowledge base</h1><input id=q placeholder="Search career, products, projects, publications, talks, training and technologies"><ul id=r>{cards}</ul><script>q.oninput=()=>[...r.children].forEach(x=>x.hidden=!x.innerText.toLowerCase().includes(q.value.toLowerCase()))</script>'
    dashboard=f'<!doctype html><meta charset=utf-8>{shared}<h1>Career dashboard</h1><p>Generated from object-per-file professional data.</p><ul>'+''.join(f'<li><b>{k}</b> {v}</li>' for k,v in counts.items())+'</ul><h2>Timeline</h2><img src="timeline.svg" alt="Publication timeline"></img>'
    GRAPH.joinpath('career_dashboard.html').write_text(dashboard); GRAPH.joinpath('timeline.html').write_text(dashboard.replace('Career dashboard','Career timeline'))
    for page,content in [('search',search),('dashboard',dashboard),('timeline',dashboard.replace('Career dashboard','Career timeline'))]:
        d=SITE/page;d.mkdir(parents=True,exist_ok=True);(d/'index.html').write_text(content)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table
        from reportlab.lib.styles import getSampleStyleSheet
        out=ROOT/'output';out.mkdir(exist_ok=True);styles=getSampleStyleSheet()
        for name,title,data in [('career_dashboard.pdf','Career dashboard',list(counts.items())),('career_timeline.pdf','Career timeline',[(x['year'],x['publication_count']) for x in timeline])]:
            SimpleDocTemplate(str(out/name),pagesize=A4).build([Paragraph(title,styles['Title']),Spacer(1,16),Table([[str(a),str(b)] for a,b in data])])
    except ImportError: pass
    print(f'Built knowledge graph with {len(objects)} objects.')
if __name__=='__main__': build()
