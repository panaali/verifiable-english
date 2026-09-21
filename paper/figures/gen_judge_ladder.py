#!/usr/bin/env python3
"""DEV-PILOT plot and tables from committed raw-count summaries, never live calls."""
from pathlib import Path
import json,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gen_e0_tables import write,table
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.hashsalt':'ve-paper-judges'})

def main():
    local=[]
    for line in (ROOT/'sources/local-ladder.md').read_text().splitlines():
        if not re.search(r'^\| .* \| fol_symbols\|none \| \d+/\d+ \(', line): continue
        name=line.split('|')[1].strip()
        counts=re.findall(r'(\d+)/(\d+)',line)
        assert len(counts)==5,(name,counts)
        fail,acc,fa,ha,approve=[tuple(map(int,c)) for c in counts]
        name=name.replace('-Instruct-4bit','').replace('-it-4bit','').replace('@verdict=forced',' (forced)')
        local.append(dict(name=name,fa=fa,ha=ha,fail=fail))
    assert len(local)==9
    colab=[]
    for row in json.loads((ROOT/'sources/colab-ladder.json').read_text()):
        name=row['model'].split('/')[-1].replace('-Instruct','').replace('=fp8',' (fp8)')
        colab.append(dict(name=name,fa=row['false_approval'],ha=row['honest_acceptance'],fail=(row['parse_fail'],row['n'])))
    hosted=[]
    for line in (ROOT/'sources/e1-pilot-dev.md').read_text().splitlines():
        if '| weak judge |' not in line: continue
        name=line.split('|')[1].strip().replace('claude-haiku-4-5-20251001','Haiku 4.5')
        counts=re.findall(r'(\d+)/(\d+)',line)
        assert len(counts)==3
        acc,fa,ha=[tuple(map(int,c)) for c in counts]
        hosted.append(dict(name=name,fa=fa,ha=ha,fail=(int(line.split('|')[-2]),acc[1])))
    assert len(hosted)==2
    def rate(v):return f'{v[0]}/{v[1]} ({100*v[0]/v[1]:.1f}%)'
    for name,rows,caption,source in [
        ('judge-local-table.md',local,'DEV-PILOT: local MLX, 4-bit; forced rows use log-probability verdict selection.','paper/sources/local-ladder.md'),
        ('judge-colab-table.md',colab+hosted,'DEV-PILOT: Colab L4 rows followed by hosted reference rows. Serving settings differ.','paper/sources/colab-ladder.json; paper/sources/e1-pilot-dev.md')]:
        write(name,caption+'\n\n'+table(['Judge','False approval','Honest acceptance','Parse failures'],[[r['name'],rate(r['fa']),rate(r['ha']),rate(r['fail'])] for r in rows])+'\n<!-- src: '+source+'; original paths/revisions in paper/sources/manifest.json. -->')
    fig,axs=plt.subplots(3,1,figsize=(8.4,8.8),gridspec_kw={'height_ratios':[9,6,2]},layout='constrained')
    for ax,rows,title in zip(axs,[local,colab,hosted],['Local MLX (4-bit)','Colab L4 (AWQ/fp8 where labeled)','Hosted reference']):
        ax.axvspan(30,60,color='#e9edf2',label='E1 calibration band')
        y=list(range(len(rows)))
        ax.scatter([100*r['fa'][0]/r['fa'][1] for r in rows],[i-.12 for i in y],s=30,c='#b55239',label='False approval',zorder=3)
        ax.scatter([100*r['ha'][0]/r['ha'][1] for r in rows],[i+.12 for i in y],s=30,c='#216a88',marker='s',label='Honest acceptance',zorder=3)
        ax.set(yticks=y,yticklabels=[r['name'] for r in rows],xlim=(-3,103),ylim=(len(rows)-.55,-.55),xticks=range(0,101,20))
        ax.set_title(title,loc='left',fontweight='bold',fontsize=10)
        ax.grid(axis='x',alpha=.2);ax.spines[['top','right','left']].set_visible(False)
    axs[0].legend(loc='lower left',bbox_to_anchor=(0,1.08),ncol=3,frameon=False,fontsize=8)
    axs[-1].set_xlabel('Assigned-case percentage (failures scored adversely)')
    fig.suptitle('Judge calibration - DEV-PILOT only',fontsize=13,fontweight='bold')
    for suffix in ['pdf','svg','png']:
        meta={'Creator':'VE paper generator'}
        if suffix=='pdf':meta.update(CreationDate=None,ModDate=None)
        elif suffix=='svg':meta.update(Date=None)
        fig.savefig(ROOT/f'figures/judge-ladder.{suffix}',dpi=180,metadata=meta)
        if suffix == 'svg':
            path = ROOT / 'figures/judge-ladder.svg'
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    plt.close(fig)
    write('judge-ladder-data.json',json.dumps({'local':local,'colab':colab,'hosted':hosted},indent=2))
    print('Judge tables and plot: DEV-PILOT counts parsed from frozen sources.')

if __name__=='__main__':main()
