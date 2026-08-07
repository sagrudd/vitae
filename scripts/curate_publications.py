#!/usr/bin/env python3
"""Editorial publication curation; reads, never regenerates, the publication database."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PUB=ROOT/'publications'
THEMES={
 'Scientific Vision':['rudd2003est'],
 'Software Platforms':['rudd2003sputnik','rudd2005opensputnik','rudd2005plantmarkers'],
 'Computational Methods':['rudd2004smar','tetko2006smar','friedel2005svm'],
 'Classification & Machine Learning':['rudd2005eclair','chappell2018'],
 'Clinical Translation':['derienzo2016mesothelioma','gunaletchumy2012','wise2016stemcells'],
 'Modern Computational Biology':['schmutzer2017plant']}
EXEC=['rudd2003est','rudd2005opensputnik','rudd2004smar','rudd2005eclair','derienzo2016mesothelioma','gunaletchumy2012','chappell2018']
STORIES={
'rudd2003est':'Articulated a scientific direction for sequence resources as a complement to whole genomes; a conversation starter on evidence, data strategy and biological utility.',
'rudd2003sputnik':'Turned comparative plant-genomics data into a usable platform, anticipating later work on scientist-facing products and workflow ecosystems.',
'rudd2004smar':'Applied genome-scale computational prediction to expose a biological pattern in scaffold/matrix attachment regions - evidence of algorithmic and systems-level thinking.',
'rudd2005eclair':'Addressed mixed biological sequence analysis through computational classification and decision support, foreshadowing modern AI-assisted assignment workflows without overstating the method.',
'rudd2005opensputnik':'Extended comparative-genomics infrastructure into a reusable EST resource for working scientists.',
'rudd2005plantmarkers':'Translated prediction into a practical molecular-marker discovery resource.',
'tetko2006smar':'Connected genome-scale prediction with spatiotemporal expression control, moving computational inference toward biological explanation.',
'friedel2005svm':'Used support vector machines to separate mixed plant-pathogen EST collections, demonstrating early machine-learning application to biological classification.',
'chappell2018':'Applied signature-based clustering to metagenomic analysis, linking computational classification to fast scientific decision support.',
'derienzo2016mesothelioma':'Contributed to molecular and clinical understanding of malignant pleural mesothelioma, evidencing breadth into human disease.',
'wise2016stemcells':'Applied genomic analysis to a clinically relevant regenerative-medicine question.',
'gunaletchumy2012':'Applied genome sequencing to clinically sourced Helicobacter pylori isolates from Malaysia, adding a practical infectious-disease and national-genomics perspective.',
'schmutzer2017plant':'Connected plant genomics resources, services and scientific infrastructure to a modern bioinformatics ecosystem.'}

def latex(value):
 return str(value).replace('\\','\\textbackslash{}').replace('&','\\&').replace('%','\\%').replace('_','\\_').replace('#','\\#')

def main():
 records={r['id']:r for r in json.loads((PUB/'publications.yaml').read_text())['records']}
 scores={k:sum([10, 8 if 'Software' in records[k]['category'] else 0,8 if records[k]['database'] else 0,8 if records[k]['methods'] else 0,6 if k in EXEC else 0]) for k in STORIES}
 portfolio=[k for group in THEMES.values() for k in group]
 def payload(keys):
  return {'selection':[{'id':k,'career_score':scores[k],'theme':next(t for t,v in THEMES.items() if k in v),'title':records[k]['title'],'story':STORIES[k]} for k in keys]}
 (PUB/'executive_publications.yaml').write_text(json.dumps(payload(EXEC),indent=2)+'\n')
 (PUB/'portfolio_publications.yaml').write_text(json.dumps(payload(portfolio),indent=2)+'\n')
 (PUB/'website_publications.yaml').write_text(json.dumps({'selection':[{'id':r['id'],'themes':r['category'],'career_phase':r['career_phase'],'technologies':r['technologies']} for r in records.values()]},indent=2)+'\n')
 (PUB/'executive_publications.tex').write_text('% Editorial executive selection\n\\nocite{'+','.join(EXEC)+'}\n')
 blocks=[]
 for theme,keys in THEMES.items():
  blocks.append('\\subsection*{'+latex(theme)+'}\n'+'\n'.join('\\textbf{'+latex(records[k]['title'])+'}\\par '+latex(STORIES[k])+'\\par' for k in keys))
 (PUB/'scientific_contributions.tex').write_text('% Generated editorial stories\n'+'\n'.join(blocks)+'\n')
 (PUB/'portfolio_publications.tex').write_text('% Editorial portfolio selection\n\\nocite{'+','.join(portfolio)+'}\n')
 print(f'Curated {len(EXEC)} executive and {len(portfolio)} portfolio publications.')
if __name__=='__main__': main()
